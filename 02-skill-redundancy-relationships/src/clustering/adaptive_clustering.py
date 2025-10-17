#!/usr/bin/env python3
"""
Adaptive Domain-Specific Clustering Module

Implements domain-specific clustering strategies optimized for different skill types:
- Phonics/Decoding: Verb-focused clustering (high weight on action verbs)
- Comprehension/Reading: Concept-focused clustering (semantic meaning)
- Writing/Speaking: Process-focused clustering (action sequences)
- Default: Balanced approach

Usage:
    from adaptive_clustering import AdaptiveClusterer
    
    clusterer = AdaptiveClusterer()
    clusters = clusterer.cluster_by_domain(skills_df, metadata_df)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False
    print("Warning: clustering libraries not available. Using fallback approach.")


class AdaptiveClusterer:
    """Domain-specific adaptive clustering for base skill extraction."""
    
    def __init__(self):
        """Initialize the adaptive clusterer."""
        if CLUSTERING_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Loaded sentence transformer for adaptive clustering")
        else:
            self.embedder = None
        
        # Define domain groupings
        self.phonics_domains = ['Phonics', 'Decoding', 'Phonological Awareness', 'Phonemic Awareness']
        self.comprehension_domains = ['Comprehension', 'Reading', 'Literary Analysis']
        self.writing_domains = ['Writing', 'Composition', 'Speaking', 'Presentation']
        self.language_domains = ['Vocabulary', 'Language Conventions', 'Grammar']
    
    def cluster_by_domain(self, skills_df: pd.DataFrame, 
                         metadata_df: Optional[pd.DataFrame] = None,
                         threshold: float = 0.75) -> Dict:
        """
        Apply domain-specific clustering strategies.
        
        Args:
            skills_df: DataFrame with ROCK skills
            metadata_df: Optional DataFrame with enhanced metadata
            threshold: Similarity threshold for clustering
            
        Returns:
            Dictionary mapping cluster IDs to skill indices
        """
        print("\n=== ADAPTIVE DOMAIN-SPECIFIC CLUSTERING ===\n")
        
        # Merge with metadata if available
        if metadata_df is not None and 'SKILL_ID' in metadata_df.columns:
            working_df = skills_df.merge(
                metadata_df[['SKILL_ID', 'skill_domain', 'skill_family', 'root_verb', 
                           'direct_objects', 'actions', 'targets', 'key_concepts']],
                on='SKILL_ID',
                how='left',
                suffixes=('', '_meta')
            )
        else:
            working_df = skills_df.copy()
            # Infer skill_domain from SKILL_AREA_NAME if available
            if 'SKILL_AREA_NAME' in working_df.columns:
                working_df['skill_domain'] = working_df['SKILL_AREA_NAME'].apply(
                    self._infer_domain_from_area
                )
            else:
                working_df['skill_domain'] = 'unknown'
        
        # Group by inferred domain
        all_clusters = {}
        cluster_id_offset = 0
        
        domain_groups = working_df.groupby('skill_domain')
        
        for domain, group_df in domain_groups:
            print(f"Clustering domain: {domain} ({len(group_df)} skills)")
            
            # Select clustering strategy based on domain
            if domain in self.phonics_domains or self._is_phonics_domain(domain):
                domain_clusters = self.cluster_verb_focused(group_df, threshold, weight=0.7)
                strategy = "verb-focused"
            
            elif domain in self.comprehension_domains or self._is_comprehension_domain(domain):
                domain_clusters = self.cluster_semantic_focused(group_df, threshold, weight=0.7)
                strategy = "semantic-focused"
            
            elif domain in self.writing_domains or self._is_writing_domain(domain):
                domain_clusters = self.cluster_process_focused(group_df, threshold, weight=0.6)
                strategy = "process-focused"
            
            else:
                domain_clusters = self.cluster_balanced(group_df, threshold)
                strategy = "balanced"
            
            # Add clusters with offset IDs to avoid collisions
            for cluster_id, skill_indices in domain_clusters.items():
                all_clusters[cluster_id_offset + cluster_id] = skill_indices
            
            num_clusters = len([k for k in domain_clusters.keys() if k != -1])
            print(f"  ✓ Created {num_clusters} clusters using {strategy} strategy")
            
            cluster_id_offset += max(domain_clusters.keys()) + 1 if domain_clusters else 0
        
        print(f"\n✓ Total clusters created: {len([k for k in all_clusters.keys() if k != -1])}")
        
        return all_clusters
    
    def cluster_verb_focused(self, skills_df: pd.DataFrame, 
                            threshold: float, weight: float = 0.7) -> Dict:
        """
        Verb-focused clustering for phonics/decoding skills.
        
        High weight on action verbs, lower weight on semantic meaning.
        """
        if not self.embedder:
            return self._fallback_clustering(skills_df)
        
        # Extract verb information
        if 'root_verb' in skills_df.columns:
            verbs = skills_df['root_verb'].fillna('unknown')
        elif 'actions' in skills_df.columns:
            # Extract first action from pipe-delimited string
            verbs = skills_df['actions'].fillna('unknown').apply(
                lambda x: str(x).split('|')[0] if '|' in str(x) else str(x)
            )
        else:
            # Fall back to extracting first word (often a verb)
            verbs = skills_df['SKILL_NAME'].apply(
                lambda x: str(x).split()[0].lower() if x else 'unknown'
            )
        
        # Create verb-enhanced representations
        skill_names = skills_df['SKILL_NAME'].tolist()
        
        # Embed skill names
        name_embeddings = self.embedder.encode(skill_names)
        
        # Embed verbs
        verb_embeddings = self.embedder.encode(verbs.tolist())
        
        # Combine with higher weight on verbs
        combined_embeddings = (
            weight * verb_embeddings +
            (1 - weight) * name_embeddings
        )
        
        # Normalize
        norms = np.linalg.norm(combined_embeddings, axis=1, keepdims=True)
        combined_embeddings = combined_embeddings / np.maximum(norms, 1e-10)
        
        # Cluster
        return self._cluster_embeddings(combined_embeddings, threshold)
    
    def cluster_semantic_focused(self, skills_df: pd.DataFrame,
                                threshold: float, weight: float = 0.7) -> Dict:
        """
        Semantic-focused clustering for comprehension/reading skills.
        
        High weight on overall semantic meaning and key concepts.
        """
        if not self.embedder:
            return self._fallback_clustering(skills_df)
        
        skill_names = skills_df['SKILL_NAME'].tolist()
        
        # Embed full skill names (captures semantic meaning)
        name_embeddings = self.embedder.encode(skill_names)
        
        # If key_concepts available, incorporate them
        if 'key_concepts' in skills_df.columns:
            concepts = skills_df['key_concepts'].fillna('').apply(
                lambda x: ' '.join(str(x).split('|')[:3]) if x else ''  # Use top 3 concepts
            )
            concept_embeddings = self.embedder.encode(concepts.tolist())
            
            # Combine with higher weight on concepts
            combined_embeddings = (
                (1 - weight) * name_embeddings +
                weight * concept_embeddings
            )
            
            # Normalize
            norms = np.linalg.norm(combined_embeddings, axis=1, keepdims=True)
            combined_embeddings = combined_embeddings / np.maximum(norms, 1e-10)
        else:
            combined_embeddings = name_embeddings
        
        # Cluster with focus on semantic similarity
        return self._cluster_embeddings(combined_embeddings, threshold)
    
    def cluster_process_focused(self, skills_df: pd.DataFrame,
                               threshold: float, weight: float = 0.6) -> Dict:
        """
        Process-focused clustering for writing/speaking skills.
        
        Consider action sequences and process steps.
        """
        if not self.embedder:
            return self._fallback_clustering(skills_df)
        
        skill_names = skills_df['SKILL_NAME'].tolist()
        
        # Embed skill names
        name_embeddings = self.embedder.encode(skill_names)
        
        # If actions available, use them to identify process similarities
        if 'actions' in skills_df.columns:
            # Get full action sequences
            action_sequences = skills_df['actions'].fillna('')
            action_embeddings = self.embedder.encode(action_sequences.tolist())
            
            # Combine
            combined_embeddings = (
                (1 - weight) * name_embeddings +
                weight * action_embeddings
            )
            
            # Normalize
            norms = np.linalg.norm(combined_embeddings, axis=1, keepdims=True)
            combined_embeddings = combined_embeddings / np.maximum(norms, 1e-10)
        else:
            combined_embeddings = name_embeddings
        
        # Cluster
        return self._cluster_embeddings(combined_embeddings, threshold)
    
    def cluster_balanced(self, skills_df: pd.DataFrame, threshold: float) -> Dict:
        """
        Balanced clustering for general or mixed domains.
        
        Equal weight on all features.
        """
        if not self.embedder:
            return self._fallback_clustering(skills_df)
        
        skill_names = skills_df['SKILL_NAME'].tolist()
        embeddings = self.embedder.encode(skill_names)
        
        return self._cluster_embeddings(embeddings, threshold)
    
    def _cluster_embeddings(self, embeddings: np.ndarray, threshold: float) -> Dict:
        """Cluster embeddings using HDBSCAN."""
        if not CLUSTERING_AVAILABLE:
            # Fallback: each skill in its own cluster
            return {i: [i] for i in range(len(embeddings))}
        
        # Use HDBSCAN for clustering
        clusterer = HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric='cosine',
            cluster_selection_epsilon=1 - threshold
        )
        
        cluster_labels = clusterer.fit_predict(embeddings)
        
        # Group by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clusters[int(label)].append(idx)
        
        return dict(clusters)
    
    def _fallback_clustering(self, skills_df: pd.DataFrame) -> Dict:
        """Fallback clustering when embeddings not available."""
        # Simple rule-based clustering by first word (often the verb)
        clusters = defaultdict(list)
        
        for idx, skill_name in enumerate(skills_df['SKILL_NAME']):
            # Use first word as cluster key
            first_word = str(skill_name).split()[0].lower() if skill_name else 'unknown'
            cluster_id = hash(first_word) % 1000  # Simple hash to int
            clusters[cluster_id].append(idx)
        
        return dict(clusters)
    
    def _infer_domain_from_area(self, skill_area: str) -> str:
        """Infer skill domain from SKILL_AREA_NAME."""
        if not skill_area:
            return 'unknown'
        
        area_lower = str(skill_area).lower()
        
        # Phonics-related
        if any(word in area_lower for word in ['phon', 'decod', 'letter', 'sound']):
            return 'Phonics'
        
        # Comprehension-related
        if any(word in area_lower for word in ['comprehension', 'reading', 'understand', 
                                               'character', 'plot', 'theme', 'inference']):
            return 'Comprehension'
        
        # Writing-related
        if any(word in area_lower for word in ['writing', 'compos', 'speaking', 'present']):
            return 'Writing'
        
        # Language/Vocabulary
        if any(word in area_lower for word in ['vocabulary', 'language', 'grammar', 'word']):
            return 'Vocabulary'
        
        # Fluency
        if any(word in area_lower for word in ['fluency', 'rate', 'accuracy']):
            return 'Fluency'
        
        return 'unknown'
    
    def _is_phonics_domain(self, domain: str) -> bool:
        """Check if domain is phonics-related."""
        return any(phon in str(domain).lower() for phon in ['phon', 'decod', 'sound'])
    
    def _is_comprehension_domain(self, domain: str) -> bool:
        """Check if domain is comprehension-related."""
        return any(comp in str(domain).lower() for comp in ['comprehens', 'reading', 'literary'])
    
    def _is_writing_domain(self, domain: str) -> bool:
        """Check if domain is writing-related."""
        return any(write in str(domain).lower() for write in ['writ', 'compos', 'speaking'])


def main():
    """Example usage of AdaptiveClusterer."""
    print("Adaptive Domain-Specific Clustering Module")
    print("=" * 50)
    print("\nThis module provides domain-specific clustering strategies.")
    print("\nUsage:")
    print("  from adaptive_clustering import AdaptiveClusterer")
    print("  clusterer = AdaptiveClusterer()")
    print("  clusters = clusterer.cluster_by_domain(skills_df, metadata_df)")
    print("\nSupported domains:")
    print("  - Phonics/Decoding: Verb-focused clustering")
    print("  - Comprehension/Reading: Semantic-focused clustering")
    print("  - Writing/Speaking: Process-focused clustering")
    print("  - Others: Balanced approach")


if __name__ == '__main__':
    main()

