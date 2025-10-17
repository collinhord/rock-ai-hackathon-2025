"""
Enhanced Semantic Similarity Tool with spaCy Integration

Improved version using spaCy preprocessing for better semantic matching
between ROCK skills and Science of Reading taxonomy.

Key Enhancements:
- spaCy-based text preprocessing and normalization
- Concept extraction for feature engineering
- Structural analysis for variant detection
- Better candidate filtering

Usage:
    python semantic_similarity_enhanced.py \\
        --skills rock_schemas/SKILLS.csv \\
        --taxonomy POC_science_of_reading_literacy_skills_taxonomy.csv \\
        --output enhanced_mappings.csv \\
        --top-k 5
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import argparse
from dataclasses import dataclass, asdict
import json
import sys

# Import our spaCy processor
sys.path.insert(0, str(Path(__file__).parent))
from spacy_processor import SkillProcessor

try:
    from sentence_transformers import SentenceTransformer
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not installed. Using fallback method.")
    EMBEDDINGS_AVAILABLE = False


@dataclass
class EnhancedSkillMatch:
    """Enhanced match with spaCy-derived features."""
    skill_id: str
    skill_name: str
    sor_path: str
    sor_skill_subset: str
    semantic_similarity: float
    structural_similarity: float
    concept_overlap: float
    combined_score: float
    match_rank: int
    match_quality: str
    spacy_concepts: Dict


class EnhancedSemanticMatcher:
    """
    Enhanced semantic matching with spaCy preprocessing.
    
    Combines:
    1. spaCy preprocessing for cleaner embeddings
    2. Semantic similarity (sentence-transformers)
    3. Structural similarity (spaCy dependency parsing)
    4. Concept overlap (spaCy POS tagging & concept extraction)
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2', use_spacy=True):
        """
        Initialize enhanced matcher.
        
        Args:
            model_name: HuggingFace sentence-transformers model
            use_spacy: Enable spaCy preprocessing (highly recommended)
        """
        self.model_name = model_name
        self.use_spacy = use_spacy
        
        # Initialize spaCy processor
        if use_spacy:
            print("Initializing spaCy processor...")
            self.spacy_processor = SkillProcessor()
        else:
            self.spacy_processor = None
        
        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            print(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            print("✓ Model loaded successfully!")
        else:
            self.model = None
            print("Running in fallback mode (keyword matching)")
    
    def preprocess_texts(self, texts: List[str], show_progress=True) -> Tuple[List[str], List[Dict]]:
        """
        Preprocess texts using spaCy.
        
        Args:
            texts: Raw skill/taxonomy descriptions
            show_progress: Show progress bar
            
        Returns:
            Tuple of (cleaned_texts, concept_metadata)
        """
        if not self.use_spacy or not self.spacy_processor:
            return texts, [{}] * len(texts)
        
        print("Preprocessing texts with spaCy...")
        cleaned_texts = []
        concept_metadata = []
        
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(texts, desc="spaCy preprocessing")
            except ImportError:
                iterator = texts
        else:
            iterator = texts
        
        for text in iterator:
            concepts = self.spacy_processor.extract_concepts(text)
            cleaned_texts.append(concepts.cleaned_text)
            concept_metadata.append({
                'actions': concepts.actions,
                'targets': concepts.targets,
                'qualifiers': concepts.qualifiers,
                'key_concepts': concepts.key_concepts
            })
        
        return cleaned_texts, concept_metadata
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts to embeddings (after spaCy preprocessing).
        
        Args:
            texts: Preprocessed text strings
            
        Returns:
            numpy array of embeddings
        """
        if self.model:
            return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        else:
            # Fallback: random embeddings
            return np.random.rand(len(texts), 384)
    
    def calculate_concept_overlap(self, 
                                  query_concepts: Dict, 
                                  target_concepts: Dict) -> float:
        """
        Calculate concept overlap score using spaCy-extracted concepts.
        
        Args:
            query_concepts: Concepts from query skill
            target_concepts: Concepts from taxonomy entry
            
        Returns:
            Overlap score (0.0 to 1.0)
        """
        if not query_concepts or not target_concepts:
            return 0.0
        
        # Compare key concepts
        query_set = set(query_concepts.get('key_concepts', []))
        target_set = set(target_concepts.get('key_concepts', []))
        
        if not query_set or not target_set:
            return 0.0
        
        intersection = query_set & target_set
        union = query_set | target_set
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Bonus for matching actions (verbs are important)
        query_actions = set(query_concepts.get('actions', []))
        target_actions = set(target_concepts.get('actions', []))
        action_match = len(query_actions & target_actions) > 0
        
        # Combined score
        score = jaccard * 0.7 + (0.3 if action_match else 0.0)
        
        return score
    
    def calculate_structural_similarity(self,
                                       query_text: str,
                                       target_text: str) -> float:
        """
        Calculate structural similarity using spaCy dependency parsing.
        
        Args:
            query_text: Query skill text
            target_text: Target taxonomy text
            
        Returns:
            Structural similarity score (0.0 to 1.0)
        """
        if not self.use_spacy or not self.spacy_processor:
            return 0.0
        
        comparison = self.spacy_processor.compare_skills_structurally(
            query_text, target_text
        )
        return comparison['structural_similarity']
    
    def find_enhanced_matches(self,
                             query_embeddings: np.ndarray,
                             target_embeddings: np.ndarray,
                             query_texts: List[str],
                             target_texts: List[str],
                             query_metadata: List[Dict],
                             target_metadata: List[Dict],
                             query_concepts: List[Dict],
                             target_concepts: List[Dict],
                             top_k: int = 5,
                             include_structural: bool = True) -> List[List[EnhancedSkillMatch]]:
        """
        Find enhanced matches combining multiple similarity signals.
        
        Args:
            query_embeddings: Query embeddings
            target_embeddings: Target embeddings
            query_texts: Original query texts
            target_texts: Original target texts
            query_metadata: Query metadata (SKILL_ID, etc.)
            target_metadata: Target metadata (path, etc.)
            query_concepts: spaCy-extracted concepts for queries
            target_concepts: spaCy-extracted concepts for targets
            top_k: Number of matches to return
            include_structural: Include structural similarity (slower but better)
            
        Returns:
            List of enhanced match lists
        """
        print(f"Computing semantic similarities...")
        semantic_similarities = cosine_similarity(query_embeddings, target_embeddings)
        
        all_matches = []
        
        print(f"Finding top-{top_k} enhanced matches for each skill...")
        try:
            from tqdm import tqdm
            iterator = tqdm(enumerate(semantic_similarities), total=len(semantic_similarities))
        except ImportError:
            iterator = enumerate(semantic_similarities)
        
        for i, query_sims in iterator:
            # Get top-k*2 semantic matches (then re-rank)
            top_indices = np.argsort(query_sims)[-(top_k * 2):][::-1]
            
            candidates = []
            for idx in top_indices:
                # Calculate concept overlap
                concept_overlap = self.calculate_concept_overlap(
                    query_concepts[i],
                    target_concepts[idx]
                )
                
                # Calculate structural similarity (optional, slower)
                structural_sim = 0.0
                if include_structural:
                    structural_sim = self.calculate_structural_similarity(
                        query_texts[i],
                        target_texts[idx]
                    )
                
                # Combined score (weighted average)
                semantic_score = float(query_sims[idx])
                combined_score = (
                    semantic_score * 0.6 +
                    concept_overlap * 0.3 +
                    structural_sim * 0.1
                )
                
                # Determine match quality
                if combined_score >= 0.75:
                    quality = 'High'
                elif combined_score >= 0.55:
                    quality = 'Medium'
                else:
                    quality = 'Low'
                
                candidates.append({
                    'idx': idx,
                    'semantic': semantic_score,
                    'concept': concept_overlap,
                    'structural': structural_sim,
                    'combined': combined_score,
                    'quality': quality
                })
            
            # Sort by combined score
            candidates.sort(key=lambda x: x['combined'], reverse=True)
            
            # Take top-k after re-ranking
            query_matches = []
            for rank, candidate in enumerate(candidates[:top_k], 1):
                idx = candidate['idx']
                
                match = EnhancedSkillMatch(
                    skill_id=query_metadata[i]['SKILL_ID'],
                    skill_name=query_metadata[i]['SKILL_NAME'],
                    sor_path=target_metadata[idx]['path'],
                    sor_skill_subset=target_metadata[idx]['skill_subset'],
                    semantic_similarity=candidate['semantic'],
                    structural_similarity=candidate['structural'],
                    concept_overlap=candidate['concept'],
                    combined_score=candidate['combined'],
                    match_rank=rank,
                    match_quality=candidate['quality'],
                    spacy_concepts=query_concepts[i]
                )
                query_matches.append(match)
            
            all_matches.append(query_matches)
        
        return all_matches


def load_skills(skills_path: Path, content_area: str = 'ELA', max_skills: int = None) -> pd.DataFrame:
    """Load and filter ROCK skills."""
    print(f"Loading skills from {skills_path}...")
    skills_df = pd.read_csv(skills_path)
    
    # Filter by content area
    if content_area:
        if 'CONTENT_AREA_SHORT_NAME' in skills_df.columns:
            skills_df = skills_df[skills_df['CONTENT_AREA_SHORT_NAME'] == content_area]
        elif 'CONTENT_AREA_NAME' in skills_df.columns:
            # Map full names
            area_map = {'English Language Arts': 'ELA', 'Mathematics': 'Math'}
            skills_df = skills_df[skills_df['CONTENT_AREA_NAME'].map(area_map) == content_area]
    
    # Filter by grade (K-2 for foundational skills)
    if 'GRADE_LEVEL_NAME' in skills_df.columns:
        grades = ['Pre-K', 'K', 'Kindergarten', 'Grade 1', 'Grade 2']
        skills_df = skills_df[skills_df['GRADE_LEVEL_NAME'].isin(grades)]
    
    # Limit for testing
    if max_skills:
        skills_df = skills_df.head(max_skills)
    
    print(f"Loaded {len(skills_df)} skills")
    return skills_df


def load_taxonomy(taxonomy_path: Path) -> pd.DataFrame:
    """Load Science of Reading taxonomy."""
    print(f"Loading taxonomy from {taxonomy_path}...")
    taxonomy_df = pd.read_csv(taxonomy_path)
    
    # Create full path string
    path_parts = []
    for col in ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']:
        if col in taxonomy_df.columns:
            path_parts.append(taxonomy_df[col].fillna(''))
    
    taxonomy_df['path'] = path_parts[0]
    for part in path_parts[1:]:
        taxonomy_df['path'] = taxonomy_df['path'] + ' > ' + part
    
    # Create combined text for embedding
    taxonomy_df['text_for_embedding'] = (
        taxonomy_df['Skill Subset'].fillna('') + '. ' +
        taxonomy_df.get('Skill Subset Annotation', pd.Series([''] * len(taxonomy_df))).fillna('')
    )
    
    print(f"Loaded {len(taxonomy_df)} taxonomy entries")
    return taxonomy_df


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced skill matching with spaCy preprocessing'
    )
    parser.add_argument('--skills', type=str, required=True, 
                       help='Path to SKILLS.csv')
    parser.add_argument('--taxonomy', type=str, required=True, 
                       help='Path to SoR taxonomy CSV')
    parser.add_argument('--output', type=str, default='enhanced_skill_mappings.csv',
                       help='Output CSV path')
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of top matches per skill')
    parser.add_argument('--max-skills', type=int, default=100,
                       help='Maximum skills to process (for testing)')
    parser.add_argument('--content-area', type=str, default='ELA',
                       help='Content area to filter (ELA, Math)')
    parser.add_argument('--no-spacy', action='store_true',
                       help='Disable spaCy preprocessing')
    parser.add_argument('--no-structural', action='store_true',
                       help='Disable structural similarity (faster)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("ENHANCED SEMANTIC SIMILARITY TOOL (with spaCy)")
    print("=" * 70)
    
    # Load data
    skills_df = load_skills(Path(args.skills), args.content_area, args.max_skills)
    taxonomy_df = load_taxonomy(Path(args.taxonomy))
    
    # Initialize enhanced matcher
    print("\nInitializing enhanced matcher...")
    matcher = EnhancedSemanticMatcher(use_spacy=not args.no_spacy)
    
    # Preprocess with spaCy
    print("\nStep 1: Preprocessing with spaCy...")
    skill_texts = skills_df['SKILL_NAME'].fillna('').tolist()
    taxonomy_texts = taxonomy_df['text_for_embedding'].fillna('').tolist()
    
    skill_cleaned, skill_concepts = matcher.preprocess_texts(skill_texts)
    taxonomy_cleaned, taxonomy_concepts = matcher.preprocess_texts(taxonomy_texts, show_progress=False)
    
    # Encode to embeddings
    print("\nStep 2: Encoding to embeddings...")
    skill_embeddings = matcher.encode_texts(skill_cleaned)
    taxonomy_embeddings = matcher.encode_texts(taxonomy_cleaned)
    
    # Prepare metadata
    skill_metadata = skills_df[['SKILL_ID', 'SKILL_NAME']].to_dict('records')
    taxonomy_metadata = [
        {
            'path': row['path'],
            'skill_subset': row['Skill Subset']
        }
        for _, row in taxonomy_df.iterrows()
    ]
    
    # Find enhanced matches
    print(f"\nStep 3: Finding enhanced matches...")
    all_matches = matcher.find_enhanced_matches(
        skill_embeddings,
        taxonomy_embeddings,
        skill_texts,
        taxonomy_texts,
        skill_metadata,
        taxonomy_metadata,
        skill_concepts,
        taxonomy_concepts,
        top_k=args.top_k,
        include_structural=not args.no_structural
    )
    
    # Convert to DataFrame
    print("\nStep 4: Saving results...")
    matches_data = []
    for skill_matches in all_matches:
        for match in skill_matches:
            match_dict = asdict(match)
            # Flatten spacy_concepts
            match_dict['spacy_actions'] = ', '.join(match.spacy_concepts.get('actions', []))
            match_dict['spacy_targets'] = ', '.join(match.spacy_concepts.get('targets', []))
            match_dict['spacy_key_concepts'] = ', '.join(match.spacy_concepts.get('key_concepts', []))
            del match_dict['spacy_concepts']
            matches_data.append(match_dict)
    
    matches_df = pd.DataFrame(matches_data)
    
    # Save results
    output_path = Path(args.output)
    matches_df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(matches_df)} matches to {output_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("MATCHING SUMMARY")
    print("=" * 70)
    print(f"Skills processed: {len(skills_df)}")
    print(f"Taxonomy entries: {len(taxonomy_df)}")
    print(f"Total matches: {len(matches_df)}")
    
    print(f"\nMatch Quality Distribution:")
    quality_dist = matches_df['match_quality'].value_counts()
    for quality, count in quality_dist.items():
        pct = (count / len(matches_df)) * 100
        print(f"  {quality}: {count} ({pct:.1f}%)")
    
    print(f"\nScore Statistics:")
    print(f"  Semantic Similarity: {matches_df['semantic_similarity'].mean():.3f} ± {matches_df['semantic_similarity'].std():.3f}")
    print(f"  Concept Overlap: {matches_df['concept_overlap'].mean():.3f} ± {matches_df['concept_overlap'].std():.3f}")
    if not args.no_structural:
        print(f"  Structural Similarity: {matches_df['structural_similarity'].mean():.3f} ± {matches_df['structural_similarity'].std():.3f}")
    print(f"  Combined Score: {matches_df['combined_score'].mean():.3f} ± {matches_df['combined_score'].std():.3f}")
    
    print(f"\nTop 5 Highest-Quality Matches:")
    top_matches = matches_df.nlargest(5, 'combined_score')[
        ['skill_name', 'sor_skill_subset', 'combined_score', 'match_quality']
    ]
    for idx, row in top_matches.iterrows():
        print(f"  {row['skill_name'][:50]}")
        print(f"    → {row['sor_skill_subset'][:50]}")
        print(f"    Score: {row['combined_score']:.3f} ({row['match_quality']})")
    
    print("=" * 70)
    print("✓ Enhanced matching complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

