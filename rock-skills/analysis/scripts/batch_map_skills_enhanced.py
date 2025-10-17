"""
Enhanced ROCK Skills Batch Mapping Pipeline with spaCy Integration

Combines spaCy preprocessing with LLM-assisted mapping for better accuracy
and reduced token usage.

Key Enhancements:
- spaCy preprocessing for cleaner semantic search
- Concept extraction for better candidate filtering
- Structural analysis for pre-filtering obvious mismatches
- Enhanced prompt context with spaCy-derived features

Usage:
    python batch_map_skills_enhanced.py \\
        --skill-ids-file ./temp_priority_skill_ids.txt \\
        --content-area "English Language Arts" \\
        --checkpoint-interval 10 \\
        --output-dir ./outputs/enhanced_mapping \\
        --skip-existing ./llm_skill_mappings.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import boto3
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from spacy_processor import SkillProcessor
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("Install with: pip install boto3 sentence-transformers scikit-learn spacy")
    print("Then run: python -m spacy download en_core_web_sm")
    DEPENDENCIES_AVAILABLE = False


class EnhancedLLMMapperAssistant:
    """
    Enhanced LLM-assisted taxonomy mapping with spaCy preprocessing.
    
    Improvements over base version:
    1. spaCy preprocessing for better semantic candidates
    2. Concept extraction for smarter candidate filtering
    3. Structural pre-filtering to reduce LLM calls
    4. Enhanced prompts with concept context
    """
    
    def __init__(self, taxonomy_df: pd.DataFrame, model='all-MiniLM-L6-v2', use_spacy=True):
        """Initialize the enhanced LLM mapper."""
        self.taxonomy_df = taxonomy_df
        self.model_name = model
        self.use_spacy = use_spacy
        
        # Initialize spaCy processor
        if use_spacy:
            print("Initializing spaCy processor...")
            self.spacy_processor = SkillProcessor()
        else:
            self.spacy_processor = None
        
        # Load sentence transformer
        print(f"Loading embedding model: {model}")
        self.encoder = SentenceTransformer(model)
        
        # Pre-compute taxonomy embeddings with spaCy preprocessing
        self.taxonomy_texts = []
        self.taxonomy_texts_raw = []
        self.taxonomy_paths = []
        self.taxonomy_concepts = []
        
        print("Preparing taxonomy entries...")
        for _, row in taxonomy_df.iterrows():
            # Build taxonomy path
            path_parts = []
            for level in ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']:
                if pd.notna(row.get(level)) and row.get(level):
                    path_parts.append(str(row[level]))
            
            if path_parts:
                taxonomy_path = ' > '.join(path_parts)
                self.taxonomy_paths.append(taxonomy_path)
                
                # Create text for embedding
                annotation = row.get('Skill Subset Annotation', '')
                raw_text = f"{taxonomy_path}"
                if pd.notna(annotation) and annotation:
                    raw_text += f". {annotation}"
                
                self.taxonomy_texts_raw.append(raw_text)
                
                # Preprocess with spaCy for better embeddings
                if self.use_spacy and self.spacy_processor:
                    concepts = self.spacy_processor.extract_concepts(raw_text)
                    processed_text = concepts.cleaned_text
                    self.taxonomy_concepts.append({
                        'actions': concepts.actions,
                        'targets': concepts.targets,
                        'key_concepts': concepts.key_concepts
                    })
                else:
                    processed_text = raw_text
                    self.taxonomy_concepts.append({})
                
                self.taxonomy_texts.append(processed_text)
        
        print(f"Computing embeddings for {len(self.taxonomy_texts)} taxonomy nodes...")
        self.taxonomy_embeddings = self.encoder.encode(self.taxonomy_texts, show_progress_bar=True)
        
        # Initialize Bedrock client
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
        self.spacy_filtered_count = 0
    
    def find_semantic_candidates(self, 
                                 skill_text: str, 
                                 skill_concepts: Optional[Dict] = None,
                                 top_k: int = 20,
                                 concept_boost: bool = True) -> List[Tuple[str, float, Dict]]:
        """
        Find top-k semantically similar taxonomy nodes with concept boosting.
        
        Args:
            skill_text: Raw skill text
            skill_concepts: Pre-extracted concepts (optional)
            top_k: Number of candidates
            concept_boost: Boost scores based on concept overlap
            
        Returns:
            List of (path, score, concepts) tuples
        """
        # Extract concepts if not provided
        if skill_concepts is None and self.use_spacy:
            skill_concepts = self.spacy_processor.extract_concepts(skill_text)
            skill_text_processed = skill_concepts.cleaned_text
            skill_concepts_dict = {
                'actions': skill_concepts.actions,
                'targets': skill_concepts.targets,
                'key_concepts': skill_concepts.key_concepts
            }
        elif skill_concepts:
            skill_text_processed = skill_concepts.get('cleaned_text', skill_text)
            skill_concepts_dict = skill_concepts
        else:
            skill_text_processed = skill_text
            skill_concepts_dict = {}
        
        # Get semantic similarities
        skill_embedding = self.encoder.encode([skill_text_processed])
        similarities = cosine_similarity(skill_embedding, self.taxonomy_embeddings)[0]
        
        # Apply concept boosting
        if concept_boost and skill_concepts_dict and self.taxonomy_concepts:
            boosted_similarities = similarities.copy()
            
            for idx, tax_concepts in enumerate(self.taxonomy_concepts):
                if not tax_concepts:
                    continue
                
                # Calculate concept overlap
                skill_concepts_set = set(skill_concepts_dict.get('key_concepts', []))
                tax_concepts_set = set(tax_concepts.get('key_concepts', []))
                
                if skill_concepts_set and tax_concepts_set:
                    overlap = len(skill_concepts_set & tax_concepts_set)
                    if overlap > 0:
                        # Boost by up to 20% based on concept overlap
                        boost = min(0.2, overlap * 0.1)
                        boosted_similarities[idx] += boost
            
            similarities = boosted_similarities
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        candidates = [
            (
                self.taxonomy_paths[idx], 
                similarities[idx],
                self.taxonomy_concepts[idx] if idx < len(self.taxonomy_concepts) else {}
            )
            for idx in top_indices
        ]
        
        return candidates
    
    def pre_filter_candidates(self,
                             skill_concepts: Dict,
                             candidates: List[Tuple[str, float, Dict]],
                             threshold: float = 0.3) -> List[Tuple[str, float, Dict]]:
        """
        Pre-filter candidates using spaCy structural analysis.
        
        Removes obviously wrong matches before sending to LLM.
        
        Args:
            skill_concepts: Concepts from skill
            candidates: Candidate list
            threshold: Minimum concept overlap to keep
            
        Returns:
            Filtered candidates
        """
        if not self.use_spacy or not skill_concepts:
            return candidates
        
        filtered = []
        skill_concepts_set = set(skill_concepts.get('key_concepts', []))
        
        for path, score, tax_concepts in candidates:
            if not tax_concepts:
                filtered.append((path, score, tax_concepts))
                continue
            
            # Check concept overlap
            tax_concepts_set = set(tax_concepts.get('key_concepts', []))
            
            if not skill_concepts_set or not tax_concepts_set:
                filtered.append((path, score, tax_concepts))
                continue
            
            overlap_ratio = len(skill_concepts_set & tax_concepts_set) / len(skill_concepts_set)
            
            if overlap_ratio >= threshold or score >= 0.6:
                filtered.append((path, score, tax_concepts))
            else:
                self.spacy_filtered_count += 1
        
        return filtered if filtered else candidates[:5]  # Always keep at least 5
    
    def map_skill_with_llm(self,
                          skill_id: str,
                          skill_name: str,
                          skill_area: Optional[str],
                          content_area: Optional[str],
                          grade_level: Optional[str],
                          top_k: int = 3) -> Dict:
        """Map a single skill using enhanced pipeline."""
        
        # Stage 0: spaCy preprocessing
        skill_concepts = None
        if self.use_spacy and self.spacy_processor:
            concepts = self.spacy_processor.extract_concepts(skill_name)
            skill_concepts = {
                'cleaned_text': concepts.cleaned_text,
                'actions': concepts.actions,
                'targets': concepts.targets,
                'key_concepts': concepts.key_concepts
            }
        
        # Stage 1: Semantic search with concept boosting
        candidates = self.find_semantic_candidates(
            skill_name, 
            skill_concepts=skill_concepts,
            top_k=25,
            concept_boost=True
        )
        
        # Stage 1.5: Pre-filter with spaCy (NEW)
        candidates = self.pre_filter_candidates(skill_concepts, candidates)
        
        # Take top 20 for LLM
        candidates = candidates[:20]
        
        # Stage 2: LLM ranking
        prompt = self.build_enhanced_llm_prompt(
            skill_id, skill_name, skill_area, content_area, grade_level,
            candidates, skill_concepts, top_k
        )
        
        try:
            response = self.call_bedrock(prompt)
            self.api_calls += 1
            
            # Parse LLM response
            mappings = self.parse_llm_response(response['content'][0]['text'])
            
            if mappings:
                best_mapping = mappings[0]
                return {
                    'SKILL_ID': skill_id,
                    'SKILL_NAME': skill_name,
                    'TAXONOMY_PATH': best_mapping['taxonomy_path'],
                    'CONFIDENCE': best_mapping['confidence'],
                    'SEMANTIC_SIMILARITY': candidates[0][1],
                    'NEEDS_REVIEW': best_mapping['confidence'] in ['Low', 'Medium'],
                    'ALTERNATIVE_1': mappings[1]['taxonomy_path'] if len(mappings) > 1 else '',
                    'ALTERNATIVE_2': mappings[2]['taxonomy_path'] if len(mappings) > 2 else '',
                    'RATIONALE': best_mapping['rationale'],
                    'SPACY_ACTIONS': ', '.join(skill_concepts.get('actions', [])) if skill_concepts else '',
                    'SPACY_TARGETS': ', '.join(skill_concepts.get('targets', [])) if skill_concepts else ''
                }
            else:
                return None
            
        except Exception as e:
            print(f"  ✗ Error mapping skill: {e}")
            return None
    
    def build_enhanced_llm_prompt(self, 
                                 skill_id, skill_name, skill_area, 
                                 content_area, grade_level,
                                 candidates, skill_concepts, top_k):
        """Build enhanced LLM prompt with spaCy-derived context."""
        
        sor_context = """
SCIENCE OF READING FRAMEWORK CONTEXT:
The Science of Reading taxonomy is organized around five pillars:
1. Phonological Awareness (sounds in spoken language, no print involved)
2. Phonics & Decoding (letter-sound relationships, applying to read words)
3. Fluency (accurate, automatic reading with prosody)
4. Vocabulary (word meanings, relationships, context clues, morphology)
5. Comprehension (understanding, interpreting, analyzing text)

MAPPING PRINCIPLES:
- Match skill scope to appropriate taxonomy granularity
- Distinguish grade-agnostic vs. grade-dependent skills
- Consider prerequisite relationships
- Watch for skills outside literacy scope
"""
        
        # Add spaCy concept analysis to prompt
        concept_context = ""
        if skill_concepts:
            concept_parts = []
            if skill_concepts.get('actions'):
                concept_parts.append(f"  - Actions: {', '.join(skill_concepts['actions'])}")
            if skill_concepts.get('targets'):
                concept_parts.append(f"  - Targets: {', '.join(skill_concepts['targets'])}")
            if skill_concepts.get('key_concepts'):
                concept_parts.append(f"  - Key Concepts: {', '.join(skill_concepts['key_concepts'])}")
            
            if concept_parts:
                concept_context = "\n\nSKILL CONCEPT ANALYSIS (extracted via NLP):\n" + "\n".join(concept_parts)
        
        prompt = f"""You are an expert in literacy education and the Science of Reading framework.

{sor_context}

Your task: Map the following ROCK skill to the most appropriate Science of Reading taxonomy node(s).

ROCK SKILL:
- Skill ID: {skill_id}
- Skill Name: {skill_name}
- Skill Area: {skill_area or 'N/A'}
- Content Area: {content_area or 'N/A'}
- Grade Level: {grade_level or 'N/A'}{concept_context}

CANDIDATE TAXONOMY NODES (pre-filtered by semantic similarity and concept overlap):
{self.format_candidates_for_llm(candidates)}

INSTRUCTIONS:
1. Analyze the ROCK skill and identify its core learning objective
2. Select the top {top_k} best matches from the candidates above
3. For each match, provide:
   - Taxonomy path
   - Confidence level (High/Medium/Low)
   - Brief rationale

OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:
1. [Full Taxonomy Path] | Confidence: [High/Medium/Low] | Rationale: [explanation]
2. [Full Taxonomy Path] | Confidence: [High/Medium/Low] | Rationale: [explanation]
...

Start your response IMMEDIATELY with "1. " - no preamble!"""
        
        return prompt
    
    def format_candidates_for_llm(self, candidates: List[Tuple[str, float, Dict]]) -> str:
        """Format candidates for LLM prompt."""
        lines = []
        for i, (path, score, concepts) in enumerate(candidates, 1):
            line = f"{i}. {path} (similarity: {score:.3f})"
            # Add concept hints
            if concepts and concepts.get('key_concepts'):
                key_concepts = concepts['key_concepts'][:3]  # Top 3
                line += f" [concepts: {', '.join(key_concepts)}]"
            lines.append(line)
        return '\n'.join(lines)
    
    def call_bedrock(self, prompt: str) -> Dict:
        """Call AWS Bedrock API."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        })
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        
        # Track tokens
        if 'usage' in response_body:
            self.total_input_tokens += response_body['usage'].get('input_tokens', 0)
            self.total_output_tokens += response_body['usage'].get('output_tokens', 0)
        
        return response_body
    
    def parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse LLM response into structured mappings."""
        mappings = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            
            # Parse format: "1. Path | Confidence: High | Rationale: explanation"
            parts = line.split('|')
            if len(parts) >= 3:
                # Extract taxonomy path
                path_part = parts[0].strip()
                path = re.sub(r'^\d+\.\s*', '', path_part).strip()
                
                # Extract confidence
                conf_part = parts[1].strip()
                conf_match = re.search(r'Confidence:\s*(High|Medium|Low)', conf_part, re.IGNORECASE)
                confidence = conf_match.group(1).capitalize() if conf_match else 'Unknown'
                
                # Extract rationale
                rationale = parts[2].strip()
                if rationale.startswith('Rationale:'):
                    rationale = rationale[10:].strip()
                
                mappings.append({
                    'taxonomy_path': path,
                    'confidence': confidence,
                    'rationale': rationale
                })
        
        return mappings
    
    def get_usage_stats(self) -> Dict:
        """Get enhanced usage statistics."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        cost = (self.total_input_tokens / 1_000_000 * 3.0) + (self.total_output_tokens / 1_000_000 * 15.0)
        
        return {
            'api_calls': self.api_calls,
            'total_tokens': total_tokens,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'estimated_cost': cost,
            'spacy_filtered': self.spacy_filtered_count
        }


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced batch mapping with spaCy preprocessing"
    )
    
    # Input/output
    parser.add_argument('--skills-path', default='rock_schemas/SKILLS.csv')
    parser.add_argument('--taxonomy-path', default='POC_science_of_reading_literacy_skills_taxonomy.csv')
    parser.add_argument('--output-dir', default='./outputs/enhanced_batch_mapping')
    
    # Filtering
    parser.add_argument('--skill-ids-file')
    parser.add_argument('--content-area', default='English Language Arts')
    parser.add_argument('--start-index', type=int, default=0)
    parser.add_argument('--batch-size', type=int)
    
    # Skip existing
    parser.add_argument('--skip-existing')
    
    # Checkpointing
    parser.add_argument('--checkpoint-interval', type=int, default=25)
    
    # spaCy options
    parser.add_argument('--no-spacy', action='store_true',
                       help='Disable spaCy preprocessing')
    
    args = parser.parse_args()
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not installed")
        return 1
    
    print("=" * 70)
    print("ENHANCED ROCK SKILLS BATCH MAPPING PIPELINE")
    print("(with spaCy Integration)")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\nLoading data...")
    scripts_dir = Path(__file__).parent
    base_dir = scripts_dir.parent
    project_root = base_dir.parent
    
    if not Path(args.skills_path).is_absolute():
        skills_path = project_root / args.skills_path
    else:
        skills_path = Path(args.skills_path)
    
    if not Path(args.taxonomy_path).is_absolute():
        taxonomy_path = project_root / args.taxonomy_path
    else:
        taxonomy_path = Path(args.taxonomy_path)
    
    essential_columns = [
        'SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME', 'GRADE_LEVEL_SHORT_NAME'
    ]
    skills_df = pd.read_csv(skills_path, usecols=essential_columns)
    taxonomy_df = pd.read_csv(taxonomy_path)
    
    print(f"Loaded {len(skills_df):,} skills")
    print(f"Loaded {len(taxonomy_df):,} taxonomy nodes")
    
    # Apply filters (same as original)
    if args.skill_ids_file:
        skill_ids_file = Path(args.skill_ids_file)
        if not skill_ids_file.is_absolute():
            skill_ids_file = base_dir / skill_ids_file
        
        with open(skill_ids_file, 'r') as f:
            target_skill_ids = set(line.strip() for line in f if line.strip())
        
        print(f"Filtering to {len(target_skill_ids)} specific SKILL_IDs")
        skills_df = skills_df[skills_df['SKILL_ID'].isin(target_skill_ids)]
    
    if args.content_area:
        skills_df = skills_df[skills_df['CONTENT_AREA_NAME'] == args.content_area]
        print(f"Filtered to {len(skills_df)} {args.content_area} skills")
    
    if args.skip_existing:
        skip_path = Path(args.skip_existing)
        if not skip_path.is_absolute():
            skip_path = base_dir / skip_path
        
        if skip_path.exists():
            existing_df = pd.read_csv(skip_path)
            existing_ids = set(existing_df['SKILL_ID'])
            skills_df = skills_df[~skills_df['SKILL_ID'].isin(existing_ids)]
            print(f"Skipping {len(existing_ids)} already mapped skills")
            print(f"Remaining: {len(skills_df)} skills")
    
    if args.batch_size:
        end_index = min(args.start_index + args.batch_size, len(skills_df))
        skills_df = skills_df.iloc[args.start_index:end_index]
        print(f"Processing batch: {len(skills_df)} skills")
    
    if len(skills_df) == 0:
        print("No skills to process!")
        return 0
    
    # Initialize enhanced mapper
    print("\nInitializing enhanced mapper...")
    mapper = EnhancedLLMMapperAssistant(taxonomy_df, use_spacy=not args.no_spacy)
    
    # Process skills
    print(f"\nProcessing {len(skills_df)} skills...")
    print("=" * 70)
    
    results = []
    review_queue = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()
    
    for idx, (_, skill) in enumerate(skills_df.iterrows(), 1):
        print(f"[{idx}/{len(skills_df)}] {skill['SKILL_NAME'][:70]}...")
        
        result = mapper.map_skill_with_llm(
            skill['SKILL_ID'],
            skill['SKILL_NAME'],
            skill['SKILL_AREA_NAME'],
            skill['CONTENT_AREA_NAME'],
            skill['GRADE_LEVEL_NAME']
        )
        
        if result:
            result['SKILL_AREA_NAME'] = skill['SKILL_AREA_NAME']
            result['CONTENT_AREA_NAME'] = skill['CONTENT_AREA_NAME']
            result['GRADE_LEVEL_NAME'] = skill['GRADE_LEVEL_NAME']
            result['GRADE_LEVEL_SHORT_NAME'] = skill['GRADE_LEVEL_SHORT_NAME']
            
            # Parse taxonomy levels
            path_parts = result['TAXONOMY_PATH'].split(' > ')
            result['strand'] = path_parts[0] if len(path_parts) > 0 else ''
            result['pillar'] = path_parts[1] if len(path_parts) > 1 else ''
            result['domain'] = path_parts[2] if len(path_parts) > 2 else ''
            result['skill_area'] = path_parts[3] if len(path_parts) > 3 else ''
            result['skill_set'] = path_parts[4] if len(path_parts) > 4 else ''
            result['skill_subset'] = path_parts[5] if len(path_parts) > 5 else ''
            
            results.append(result)
            print(f"  ✓ {result['CONFIDENCE']} confidence")
            
            if result['NEEDS_REVIEW']:
                review_queue.append(result)
        
        # Checkpoint
        if idx % args.checkpoint_interval == 0 and results:
            checkpoint_path = output_dir / f"checkpoint_{timestamp}.csv"
            pd.DataFrame(results).to_csv(checkpoint_path, index=False)
            print(f"--- Checkpoint at {idx} skills ---")
            
            stats = mapper.get_usage_stats()
            print(f"API Calls: {stats['api_calls']} | Cost: ${stats['estimated_cost']:.2f} | spaCy Filtered: {stats['spacy_filtered']}")
    
    # Save final results
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("ENHANCED BATCH COMPLETE")
    print("=" * 70)
    print(f"Processed: {len(results)} skills")
    print(f"Time: {elapsed_time:.1f}s ({elapsed_time/len(results):.1f}s/skill)")
    
    if results:
        final_path = output_dir / f"enhanced_mappings_{timestamp}.csv"
        results_df = pd.DataFrame(results)
        results_df.to_csv(final_path, index=False)
        print(f"✓ Results: {final_path}")
    
    # Final stats
    stats = mapper.get_usage_stats()
    print("\n" + "=" * 70)
    print("ENHANCED PIPELINE STATISTICS")
    print("=" * 70)
    print(f"API Calls: {stats['api_calls']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Cost: ${stats['estimated_cost']:.2f}")
    print(f"spaCy Pre-filtered: {stats['spacy_filtered']} candidates")
    print(f"Avg Tokens per Skill: {stats['total_tokens']//len(results) if results else 0}")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

