#!/usr/bin/env python3
"""
Base Skill Extraction Pipeline

Extracts base skills from ROCK skill names using:
1. spaCy preprocessing (dependency parsing, NER, lemmatization)
2. Semantic clustering (sentence-transformers + HDBSCAN)
3. LLM refinement (Claude Sonnet 4.5)

Usage:
    python3 extract_base_skills.py --input SKILLS.csv --output base_skills.json
"""

import sys
import json
import pandas as pd
import spacy
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime
import argparse

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import HDBSCAN
    import numpy as np
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False
    print("Warning: sentence-transformers or sklearn not available. Clustering disabled.")

try:
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not available. LLM refinement disabled.")


class BaseSkillExtractor:
    """Extract base skills from ROCK skill names using spaCy + semantic clustering + LLM."""
    
    def __init__(self, use_llm: bool = True, use_clustering: bool = True, redundancy_results_path: str = None):
        """
        Initialize the extractor.
        
        Args:
            use_llm: Whether to use LLM for refinement
            use_clustering: Whether to use clustering for grouping
            redundancy_results_path: Optional path to redundancy analysis results
        """
        self.use_llm = use_llm and BEDROCK_AVAILABLE
        self.use_clustering = use_clustering and CLUSTERING_AVAILABLE
        self.redundancy_results_path = redundancy_results_path
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
            print("✓ Loaded spaCy model: en_core_web_lg")
        except OSError:
            print("⚠ spaCy model 'en_core_web_lg' not found. Install with:")
            print("  python3 -m spacy download en_core_web_lg")
            sys.exit(1)
        
        # Load sentence transformer if available
        if self.use_clustering:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Loaded sentence transformer: all-MiniLM-L6-v2")
        
        # Initialize Bedrock client if available
        if self.use_llm:
            try:
                self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
                print("✓ Initialized AWS Bedrock client")
            except Exception as e:
                print(f"⚠ Could not initialize Bedrock: {e}")
                self.use_llm = False
    
    def normalize_skill_name(self, skill_name: str) -> str:
        """
        Normalize skill name by removing grade references, support qualifiers, etc.
        
        Args:
            skill_name: Original ROCK skill name
            
        Returns:
            Normalized skill name
        """
        if not skill_name or pd.isna(skill_name):
            return ""
        
        # Convert to lowercase for processing
        normalized = skill_name.lower()
        
        # Remove grade references
        normalized = re.sub(r'\(grade [pk\d-]+\)', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\bgr(ade)?\.?\s*[pk\d-]+\b', '', normalized, flags=re.IGNORECASE)
        
        # Remove support qualifiers
        support_phrases = [
            'with support',
            'with prompting',
            'with teacher support',
            'with guidance',
            'independently',
            'autonomously',
            'with assistance'
        ]
        for phrase in support_phrases:
            normalized = normalized.replace(phrase, '')
        
        # Remove complexity qualifiers
        complexity_phrases = [
            'simple',
            'complex',
            'basic',
            'advanced',
            'sophisticated',
            'multi-step',
            'single-step'
        ]
        for phrase in complexity_phrases:
            normalized = normalized.replace(phrase, '')
        
        # Clean up whitespace and punctuation
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        normalized = re.sub(r'\s*,\s*$', '', normalized)  # Remove trailing comma
        
        return normalized
    
    def extract_core_components_spacy(self, skill_name: str) -> Dict:
        """
        Extract core components using spaCy NLP.
        
        Args:
            skill_name: Normalized skill name
            
        Returns:
            Dictionary with extracted components
        """
        doc = self.nlp(skill_name)
        
        components = {
            'root_verb': None,
            'core_object': None,
            'action_phrases': [],
            'key_nouns': [],
            'lemmatized': []
        }
        
        # Find root verb
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                components['root_verb'] = token.lemma_
                break
        
        # Extract direct objects and prepositional objects
        for token in doc:
            if token.dep_ in ["dobj", "pobj"] and token.pos_ in ["NOUN", "PROPN"]:
                components['core_object'] = token.text
                break
        
        # Extract key nouns
        components['key_nouns'] = [
            token.lemma_ for token in doc 
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop
        ]
        
        # Get lemmatized form
        components['lemmatized'] = [
            token.lemma_ for token in doc 
            if not token.is_stop and token.pos_ in ["VERB", "NOUN", "ADJ"]
        ]
        
        return components
    
    def initialize_from_redundancy(self, skills_df: pd.DataFrame) -> Tuple[List[Dict], set]:
        """
        Seed clusters from redundancy SPECIFICATION_VARIANT relationships.
        
        Args:
            skills_df: DataFrame with ROCK skills
            
        Returns:
            Tuple of (seed_clusters, processed_skill_ids)
        """
        if not self.redundancy_results_path or not Path(self.redundancy_results_path).exists():
            print("  No redundancy results found, skipping seeded initialization")
            return [], set()
        
        print(f"  Loading redundancy results from {self.redundancy_results_path}...")
        
        try:
            with open(self.redundancy_results_path, 'r') as f:
                relationships = json.load(f)
        except Exception as e:
            print(f"  ⚠ Could not load redundancy results: {e}")
            return [], set()
        
        # Filter to SPECIFICATION_VARIANT relationships
        spec_variants = [r for r in relationships 
                        if r.get('relationship_type') == 'SPECIFICATION_VARIANT']
        
        print(f"  Found {len(spec_variants)} SPECIFICATION_VARIANT relationships")
        
        seed_clusters = []
        processed_skill_ids = set()
        
        for rel in spec_variants:
            skill_a_id = rel.get('skill_a_id')
            skill_b_id = rel.get('skill_b_id')
            
            if not skill_a_id or not skill_b_id:
                continue
            
            # Skip if already processed
            if skill_a_id in processed_skill_ids or skill_b_id in processed_skill_ids:
                continue
            
            # Get skill names for base skill generation
            skill_a_row = skills_df[skills_df['SKILL_ID'] == skill_a_id]
            skill_b_row = skills_df[skills_df['SKILL_ID'] == skill_b_id]
            
            if skill_a_row.empty or skill_b_row.empty:
                continue
            
            skill_a_name = skill_a_row.iloc[0]['SKILL_NAME']
            skill_b_name = skill_b_row.iloc[0]['SKILL_NAME']
            
            # Extract base skill name from structural components if available
            similarity_exp = rel.get('similarity_explanation', {})
            structural = similarity_exp.get('components', {}).get('structural', {})
            
            # Try to get overlapping actions and targets
            actions_overlap = structural.get('actions_overlap', [])
            targets_overlap = structural.get('targets_overlap', [])
            
            # Generate base skill name
            if actions_overlap and targets_overlap:
                action = actions_overlap[0] if actions_overlap else 'perform'
                target = targets_overlap[0] if targets_overlap else 'skill'
                base_name = f"{action.capitalize()} {target.capitalize()}"
            else:
                # Fallback: use normalized form of first skill
                base_name = self.normalize_skill_name(skill_a_name).title()
            
            # Extract specification differences if available
            spec_diffs = similarity_exp.get('specification_differences', {})
            
            seed_clusters.append({
                'base_skill_name': base_name,
                'member_skill_ids': [skill_a_id, skill_b_id],
                'member_skill_names': [skill_a_name, skill_b_name],
                'confidence': rel.get('confidence', 'medium'),
                'similarity_score': rel.get('similarity_scores', {}).get('composite', 0.0),
                'specifications': spec_diffs,
                'source': 'redundancy_seeded',
                'cluster_id': f"SEED-{len(seed_clusters)}"
            })
            
            processed_skill_ids.add(skill_a_id)
            processed_skill_ids.add(skill_b_id)
        
        print(f"  ✓ Created {len(seed_clusters)} seed clusters covering {len(processed_skill_ids)} skills")
        
        return seed_clusters, processed_skill_ids
    
    def cluster_similar_skills(self, skills_df: pd.DataFrame, threshold: float = 0.75) -> Dict[int, List]:
        """
        Cluster similar skills using semantic embeddings.
        
        Args:
            skills_df: DataFrame with normalized skill names
            threshold: Similarity threshold for clustering
            
        Returns:
            Dictionary mapping cluster_id to list of skill indices
        """
        if not self.use_clustering:
            print("⚠ Clustering disabled, assigning each skill to its own cluster")
            return {i: [i] for i in range(len(skills_df))}
        
        print(f"Generating embeddings for {len(skills_df)} skills...")
        skill_names = skills_df['normalized_name'].tolist()
        embeddings = self.embedder.encode(skill_names, show_progress_bar=True)
        
        print("Clustering similar skills...")
        clusterer = HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric='cosine',
            cluster_selection_epsilon=1 - threshold
        )
        cluster_labels = clusterer.fit_predict(embeddings)
        
        # Group skills by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clusters[label].append(idx)
        
        # Count clusters
        num_clusters = len([k for k in clusters.keys() if k != -1])
        num_noise = len(clusters.get(-1, []))
        
        print(f"✓ Found {num_clusters} clusters ({num_noise} unclustered skills)")
        
        return dict(clusters)
    
    def generate_base_skill_with_llm(self, skill_cluster: List[str], skill_ids: List[str]) -> Dict:
        """
        Use LLM to generate a base skill name and description for a cluster.
        
        Args:
            skill_cluster: List of similar skill names
            skill_ids: Corresponding skill IDs
            
        Returns:
            Dictionary with base skill definition
        """
        if not self.use_llm:
            # Fallback: use most common terms
            return {
                'base_skill_name': skill_cluster[0].title(),
                'base_skill_description': f"Skills related to: {skill_cluster[0]}",
                'created_by': 'rule_based',
                'confidence': 'low'
            }
        
        prompt = f"""You are an expert in literacy education and taxonomy design.

TASK: Analyze the following cluster of similar ROCK skills and generate a single BASE SKILL that represents their core competency.

ROCK SKILLS IN CLUSTER ({len(skill_cluster)} skills):
{chr(10).join(f"- {skill}" for skill in skill_cluster[:10])}
{"..." if len(skill_cluster) > 10 else ""}

INSTRUCTIONS:
1. Identify the CORE COMPETENCY shared by all these skills
2. Create a clear, concise base skill name (3-8 words)
3. Write a 1-2 sentence description of what this skill entails
4. Determine the skill family (Comprehension, Decoding, Fluency, Vocabulary, Writing, Speaking, Listening, Language Conventions, Phonological Awareness, Phonics)
5. Determine the cognitive category (recall, comprehension, application, analysis, synthesis, evaluation)

RESPOND ONLY WITH JSON:
{{
    "base_skill_name": "Clear, action-oriented name",
    "base_skill_description": "Detailed description of the skill",
    "skill_family": "Category",
    "cognitive_category": "Level",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation of your analysis"
}}

Start your response IMMEDIATELY with "{{" - no preamble!"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-sonnet-4-5-v2:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.3,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                })
            )
            
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['created_by'] = 'llm'
                return result
            else:
                raise ValueError("No JSON found in LLM response")
                
        except Exception as e:
            print(f"⚠ LLM generation failed: {e}")
            return {
                'base_skill_name': skill_cluster[0].title(),
                'base_skill_description': f"Skills related to: {skill_cluster[0]}",
                'skill_family': 'Unknown',
                'cognitive_category': 'comprehension',
                'created_by': 'fallback',
                'confidence': 'low',
                'error': str(e)
            }
    
    def extract_base_skills(self, skills_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Main extraction pipeline.
        
        Args:
            skills_df: DataFrame with ROCK skills
            
        Returns:
            Tuple of (skills_with_mappings, base_skills_list)
        """
        print("\n=== BASE SKILL EXTRACTION PIPELINE ===\n")
        
        # Step 1: Normalize skill names
        print("Step 1: Normalizing skill names...")
        skills_df['normalized_name'] = skills_df['SKILL_NAME'].apply(self.normalize_skill_name)
        skills_df['spacy_components'] = skills_df['normalized_name'].apply(
            lambda x: self.extract_core_components_spacy(x) if x else {}
        )
        
        # Step 1.5: Initialize from redundancy (if available)
        print("\nStep 1.5: Initializing from redundancy analysis...")
        seed_clusters, processed_skill_ids = self.initialize_from_redundancy(skills_df)
        
        # Step 2: Cluster similar skills (excluding already processed)
        print("\nStep 2: Clustering remaining skills...")
        if processed_skill_ids:
            unassigned_df = skills_df[~skills_df['SKILL_ID'].isin(processed_skill_ids)].copy()
            print(f"  Clustering {len(unassigned_df)} unassigned skills (out of {len(skills_df)} total)")
            clusters = self.cluster_similar_skills(unassigned_df)
        else:
            clusters = self.cluster_similar_skills(skills_df)
        
        # Step 3: Generate base skills for each cluster
        print("\nStep 3: Generating base skills...")
        base_skills = []
        base_skill_id_counter = 1
        
        # First, process seed clusters from redundancy
        for seed_cluster in seed_clusters:
            print(f"  Seed Cluster: {len(seed_cluster['member_skill_ids'])} skills (from redundancy)")
            
            # Generate base skill (use provided name or enhance with LLM)
            base_skill_name = seed_cluster['base_skill_name']
            
            if self.use_llm:
                base_skill_def = self.generate_base_skill_with_llm(
                    seed_cluster['member_skill_names'],
                    seed_cluster['member_skill_ids']
                )
            else:
                base_skill_def = {
                    'base_skill_name': base_skill_name,
                    'base_skill_description': f"Skills related to: {base_skill_name}",
                    'skill_family': 'Unknown',
                    'cognitive_category': 'comprehension',
                    'created_by': 'redundancy_seeded',
                    'confidence': seed_cluster['confidence']
                }
            
            # Add metadata
            base_skill_id = f"BS-{base_skill_id_counter:03d}"
            base_skill = {
                'base_skill_id': base_skill_id,
                'base_skill_name': base_skill_def.get('base_skill_name', base_skill_name),
                'base_skill_description': base_skill_def.get('base_skill_description', ''),
                'skill_family': base_skill_def.get('skill_family', 'Unknown'),
                'cognitive_category': base_skill_def.get('cognitive_category', 'comprehension'),
                'rock_skills_count': len(seed_cluster['member_skill_ids']),
                'created_by': 'redundancy_seeded',
                'validation_status': 'pending',
                'created_timestamp': datetime.utcnow().isoformat() + 'Z',
                'updated_timestamp': datetime.utcnow().isoformat() + 'Z',
                'cluster_id': seed_cluster['cluster_id'],
                'confidence': seed_cluster['confidence'],
                'similarity_score': seed_cluster['similarity_score'],
                'specifications': seed_cluster['specifications'],
                'llm_reasoning': base_skill_def.get('reasoning', 'Seeded from redundancy analysis')
            }
            
            base_skills.append(base_skill)
            
            # Assign base skill ID to ROCK skills
            for skill_id in seed_cluster['member_skill_ids']:
                skills_df.loc[skills_df['SKILL_ID'] == skill_id, 'base_skill_id'] = base_skill_id
                skills_df.loc[skills_df['SKILL_ID'] == skill_id, 'cluster_id'] = seed_cluster['cluster_id']
            
            base_skill_id_counter += 1
        
        # Then, process regular clusters
        for cluster_id, skill_indices in clusters.items():
            if cluster_id == -1:  # Skip noise cluster for now
                continue
            
            cluster_skills = skills_df.iloc[skill_indices] if isinstance(skill_indices, list) else unassigned_df.iloc[skill_indices]
            cluster_names = cluster_skills['normalized_name'].tolist()
            cluster_ids = cluster_skills['SKILL_ID'].tolist()
            
            print(f"  Cluster {cluster_id}: {len(skill_indices)} skills")
            
            # Generate base skill
            base_skill_def = self.generate_base_skill_with_llm(cluster_names, cluster_ids)
            
            # Add metadata
            base_skill_id = f"BS-{base_skill_id_counter:03d}"
            base_skill = {
                'base_skill_id': base_skill_id,
                'base_skill_name': base_skill_def.get('base_skill_name', 'Unknown'),
                'base_skill_description': base_skill_def.get('base_skill_description', ''),
                'skill_family': base_skill_def.get('skill_family', 'Unknown'),
                'cognitive_category': base_skill_def.get('cognitive_category', 'comprehension'),
                'rock_skills_count': len(skill_indices),
                'created_by': base_skill_def.get('created_by', 'unknown'),
                'validation_status': 'pending',
                'created_timestamp': datetime.utcnow().isoformat() + 'Z',
                'updated_timestamp': datetime.utcnow().isoformat() + 'Z',
                'cluster_id': int(cluster_id),
                'confidence': base_skill_def.get('confidence', 'medium'),
                'llm_reasoning': base_skill_def.get('reasoning', '')
            }
            
            base_skills.append(base_skill)
            
            # Assign base skill ID to ROCK skills
            for skill_id in cluster_ids:
                skills_df.loc[skills_df['SKILL_ID'] == skill_id, 'base_skill_id'] = base_skill_id
                skills_df.loc[skills_df['SKILL_ID'] == skill_id, 'cluster_id'] = cluster_id
            
            base_skill_id_counter += 1
        
        print(f"\n✓ Generated {len(base_skills)} base skills")
        
        return skills_df, base_skills


def main():
    parser = argparse.ArgumentParser(description='Extract base skills from ROCK skills')
    parser.add_argument('--input', default='../../rock_schemas/SKILLS.csv',
                       help='Input CSV file with ROCK skills')
    parser.add_argument('--output', default='../../taxonomy/base_skills',
                       help='Output directory for base skills JSON files')
    parser.add_argument('--redundancy-results', type=str, default=None,
                       help='Path to redundancy analysis results JSON (enables seed clustering)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of skills to process (for testing)')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM refinement')
    parser.add_argument('--no-clustering', action='store_true',
                       help='Disable clustering')
    parser.add_argument('--incremental', action='store_true',
                       help='Process only new skills not in existing mappings')
    parser.add_argument('--since', type=str, default=None,
                       help='Process only skills added after this date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Load ROCK skills
    print(f"Loading ROCK skills from {args.input}...")
    skills_df = pd.read_csv(args.input)
    
    # Incremental mode: filter to new skills only
    if args.incremental or args.since:
        mappings_file = Path(args.output).parent / "mappings" / "rock_to_base_mappings.csv"
        
        if args.incremental and mappings_file.exists():
            print("🔄 Incremental mode: Loading existing mappings...")
            existing_mappings = pd.read_csv(mappings_file)
            existing_skill_ids = set(existing_mappings['SKILL_ID'].values)
            
            original_count = len(skills_df)
            skills_df = skills_df[~skills_df['SKILL_ID'].isin(existing_skill_ids)]
            print(f"   Filtered to {len(skills_df)} new skills (out of {original_count} total)")
            
            if len(skills_df) == 0:
                print("✓ No new skills to process")
                return
        
        if args.since:
            print(f"📅 Date filter: Skills added after {args.since}...")
            # Note: Requires a date column in SKILLS.csv (e.g., 'CREATED_DATE')
            # If column doesn't exist, warn and skip
            if 'CREATED_DATE' in skills_df.columns:
                skills_df['CREATED_DATE'] = pd.to_datetime(skills_df['CREATED_DATE'])
                since_date = pd.to_datetime(args.since)
                original_count = len(skills_df)
                skills_df = skills_df[skills_df['CREATED_DATE'] > since_date]
                print(f"   Filtered to {len(skills_df)} skills after {args.since}")
            else:
                print("   ⚠️  Warning: CREATED_DATE column not found, skipping date filter")
    
    if args.limit:
        skills_df = skills_df.head(args.limit)
        print(f"Limited to {args.limit} skills for testing")
    
    print(f"Loaded {len(skills_df)} ROCK skills")
    
    # Initialize extractor
    extractor = BaseSkillExtractor(
        use_llm=not args.no_llm,
        use_clustering=not args.no_clustering,
        redundancy_results_path=args.redundancy_results
    )
    
    # Extract base skills
    skills_with_mappings, base_skills = extractor.extract_base_skills(skills_df)
    
    # Save base skills
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual base skill JSON files
    for base_skill in base_skills:
        skill_id = base_skill['base_skill_id']
        output_file = output_dir / f"{skill_id}.json"
        with open(output_file, 'w') as f:
            json.dump(base_skill, f, indent=2)
    
    # Save summary file
    summary_file = output_dir / "base_skills_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(base_skills, f, indent=2)
    
    # Save updated skills with mappings
    mappings_file = output_dir.parent / "mappings" / "rock_to_base_mappings.csv"
    mappings_file.parent.mkdir(parents=True, exist_ok=True)
    skills_with_mappings[['SKILL_ID', 'SKILL_NAME', 'base_skill_id', 'cluster_id', 'normalized_name']].to_csv(
        mappings_file, index=False
    )
    
    print(f"\n✓ Saved {len(base_skills)} base skills to {output_dir}")
    print(f"✓ Saved mappings to {mappings_file}")
    
    # Print summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total ROCK skills: {len(skills_df)}")
    print(f"Base skills generated: {len(base_skills)}")
    print(f"Average skills per base: {len(skills_df) / len(base_skills):.1f}")
    print(f"Unmapped skills: {skills_df['base_skill_id'].isna().sum()}")


if __name__ == '__main__':
    main()

