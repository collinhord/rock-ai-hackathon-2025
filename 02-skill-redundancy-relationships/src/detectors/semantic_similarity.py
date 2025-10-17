"""
Semantic Similarity Tool for ROCK Skills to Science of Reading Taxonomy Mapping

This tool uses sentence embeddings to find semantically similar matches between
ROCK skill descriptions and Science of Reading taxonomy entries.

Usage:
    python semantic_similarity.py --skills SKILLS.csv --taxonomy taxonomy.csv --output mappings.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import argparse
from dataclasses import dataclass
import json

try:
    from sentence_transformers import SentenceTransformer
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers not installed. Using fallback method.")
    EMBEDDINGS_AVAILABLE = False


@dataclass
class SkillMatch:
    """Represents a match between a ROCK skill and SoR taxonomy entry."""
    skill_id: str
    skill_name: str
    sor_path: str
    sor_skill_subset: str
    similarity_score: float
    match_rank: int


class SemanticMatcher:
    """Semantic matching between ROCK skills and Science of Reading taxonomy."""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize semantic matcher.
        
        Args:
            model_name: HuggingFace sentence-transformers model name
        """
        self.model_name = model_name
        if EMBEDDINGS_AVAILABLE:
            print(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            print("Model loaded successfully!")
        else:
            self.model = None
            print("Running in fallback mode (keyword matching)")
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts to embeddings.
        
        Args:
            texts: List of text strings
            
        Returns:
            numpy array of embeddings (shape: n_texts x embedding_dim)
        """
        if self.model:
            return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        else:
            # Fallback: return dummy embeddings
            return np.random.rand(len(texts), 384)
    
    def find_top_matches(self, 
                        query_embeddings: np.ndarray,
                        target_embeddings: np.ndarray,
                        query_metadata: List[Dict],
                        target_metadata: List[Dict],
                        top_k: int = 5) -> List[List[SkillMatch]]:
        """
        Find top-k most similar targets for each query.
        
        Args:
            query_embeddings: Embeddings for query items (ROCK skills)
            target_embeddings: Embeddings for target items (SoR taxonomy)
            query_metadata: Metadata for each query (SKILL_ID, SKILL_NAME, etc.)
            target_metadata: Metadata for each target (taxonomy path, etc.)
            top_k: Number of top matches to return per query
            
        Returns:
            List of lists of SkillMatch objects
        """
        # Compute cosine similarity
        similarities = cosine_similarity(query_embeddings, target_embeddings)
        
        matches = []
        for i, query_sims in enumerate(similarities):
            # Get top-k indices
            top_indices = np.argsort(query_sims)[-top_k:][::-1]
            
            query_matches = []
            for rank, idx in enumerate(top_indices, 1):
                match = SkillMatch(
                    skill_id=query_metadata[i]['SKILL_ID'],
                    skill_name=query_metadata[i]['SKILL_NAME'],
                    sor_path=target_metadata[idx]['path'],
                    sor_skill_subset=target_metadata[idx]['skill_subset'],
                    similarity_score=float(query_sims[idx]),
                    match_rank=rank
                )
                query_matches.append(match)
            
            matches.append(query_matches)
        
        return matches
    
    def keyword_fallback_score(self, skill_text: str, taxonomy_text: str) -> float:
        """Simple keyword-based similarity (fallback when embeddings unavailable)."""
        skill_words = set(skill_text.lower().split())
        taxonomy_words = set(taxonomy_text.lower().split())
        
        if not skill_words or not taxonomy_words:
            return 0.0
        
        intersection = skill_words & taxonomy_words
        union = skill_words | taxonomy_words
        
        # Jaccard similarity
        return len(intersection) / len(union)


def load_skills(skills_path: Path, content_area: str = 'ELA', max_skills: int = None) -> pd.DataFrame:
    """
    Load ROCK skills from CSV.
    
    Args:
        skills_path: Path to SKILLS.csv
        content_area: Filter by content area (default: ELA)
        max_skills: Maximum number of skills to load (for testing)
        
    Returns:
        DataFrame of filtered skills
    """
    print(f"Loading skills from {skills_path}...")
    skills_df = pd.read_csv(skills_path)
    
    # Filter by content area
    if content_area:
        skills_df = skills_df[skills_df['CONTENT_AREA_SHORT_NAME'] == content_area]
    
    # Filter by grade (K-2 for foundational skills)
    grades = ['Pre-K', 'K', 'Kindergarten', 'Grade 1', 'Grade 2']
    skills_df = skills_df[skills_df['GRADE_LEVEL_NAME'].isin(grades)]
    
    # Limit for testing
    if max_skills:
        skills_df = skills_df.head(max_skills)
    
    print(f"Loaded {len(skills_df)} skills")
    return skills_df


def load_taxonomy(taxonomy_path: Path) -> pd.DataFrame:
    """
    Load Science of Reading taxonomy from CSV.
    
    Args:
        taxonomy_path: Path to SoR taxonomy CSV
        
    Returns:
        DataFrame of taxonomy entries
    """
    print(f"Loading taxonomy from {taxonomy_path}...")
    taxonomy_df = pd.read_csv(taxonomy_path)
    
    # Create full path string for better matching
    taxonomy_df['path'] = (
        taxonomy_df['Strand'].fillna('') + ' > ' +
        taxonomy_df['Pillar'].fillna('') + ' > ' +
        taxonomy_df['Domain'].fillna('') + ' > ' +
        taxonomy_df['Skill Area'].fillna('')
    )
    
    # Create combined text for embedding
    taxonomy_df['text_for_embedding'] = (
        taxonomy_df['Skill Subset'].fillna('') + '. ' +
        taxonomy_df['Skill Subset Annotation'].fillna('')
    )
    
    print(f"Loaded {len(taxonomy_df)} taxonomy entries")
    return taxonomy_df


def main():
    parser = argparse.ArgumentParser(description='Match ROCK skills to Science of Reading taxonomy')
    parser.add_argument('--skills', type=str, required=True, help='Path to SKILLS.csv')
    parser.add_argument('--taxonomy', type=str, required=True, help='Path to SoR taxonomy CSV')
    parser.add_argument('--output', type=str, default='skill_taxonomy_matches.csv', 
                       help='Output CSV path')
    parser.add_argument('--top-k', type=int, default=5, 
                       help='Number of top matches per skill')
    parser.add_argument('--max-skills', type=int, default=100,
                       help='Maximum skills to process (for testing)')
    parser.add_argument('--content-area', type=str, default='ELA',
                       help='Content area to filter (ELA, Math)')
    
    args = parser.parse_args()
    
    # Load data
    skills_df = load_skills(Path(args.skills), args.content_area, args.max_skills)
    taxonomy_df = load_taxonomy(Path(args.taxonomy))
    
    # Initialize matcher
    matcher = SemanticMatcher()
    
    # Encode skills
    print("\nEncoding ROCK skills...")
    skill_texts = skills_df['SKILL_NAME'].fillna('').tolist()
    skill_embeddings = matcher.encode_texts(skill_texts)
    
    # Encode taxonomy
    print("\nEncoding SoR taxonomy...")
    taxonomy_texts = taxonomy_df['text_for_embedding'].fillna('').tolist()
    taxonomy_embeddings = matcher.encode_texts(taxonomy_texts)
    
    # Prepare metadata
    skill_metadata = skills_df[['SKILL_ID', 'SKILL_NAME', 'GRADE_LEVEL_NAME']].to_dict('records')
    taxonomy_metadata = [
        {
            'path': row['path'],
            'skill_subset': row['Skill Subset'],
            'annotation': row['Skill Subset Annotation']
        }
        for _, row in taxonomy_df.iterrows()
    ]
    
    # Find matches
    print(f"\nFinding top-{args.top_k} matches for each skill...")
    all_matches = matcher.find_top_matches(
        skill_embeddings,
        taxonomy_embeddings,
        skill_metadata,
        taxonomy_metadata,
        top_k=args.top_k
    )
    
    # Flatten results to DataFrame
    matches_data = []
    for skill_matches in all_matches:
        for match in skill_matches:
            matches_data.append({
                'SKILL_ID': match.skill_id,
                'SKILL_NAME': match.skill_name,
                'SOR_PATH': match.sor_path,
                'SOR_SKILL_SUBSET': match.sor_skill_subset,
                'SIMILARITY_SCORE': match.similarity_score,
                'MATCH_RANK': match.match_rank,
                'CONFIDENCE': 'High' if match.similarity_score > 0.7 else 'Medium' if match.similarity_score > 0.5 else 'Low'
            })
    
    matches_df = pd.DataFrame(matches_data)
    
    # Save results
    output_path = Path(args.output)
    matches_df.to_csv(output_path, index=False)
    print(f"\nSaved {len(matches_df)} matches to {output_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("MATCHING SUMMARY")
    print("="*60)
    print(f"Skills processed: {len(skills_df)}")
    print(f"Taxonomy entries: {len(taxonomy_df)}")
    print(f"Total matches generated: {len(matches_df)}")
    print(f"\nConfidence distribution:")
    print(matches_df['CONFIDENCE'].value_counts())
    print("\nTop 5 highest-confidence matches:")
    print(matches_df.nlargest(5, 'SIMILARITY_SCORE')[['SKILL_NAME', 'SOR_SKILL_SUBSET', 'SIMILARITY_SCORE']])
    print("="*60)


if __name__ == '__main__':
    main()

