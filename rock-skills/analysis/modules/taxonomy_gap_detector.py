#!/usr/bin/env python3
"""
Taxonomy Gap Detector

Analyzes unmappable skills to identify patterns and suggest taxonomy extensions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import json


class TaxonomyGapDetector:
    """
    Detects gaps in Science of Reading taxonomy based on unmappable ROCK skills.
    """
    
    def __init__(self, embedder=None):
        """
        Initialize gap detector.
        
        Args:
            embedder: Optional SentenceTransformer for semantic clustering
        """
        self.embedder = embedder
    
    def analyze_unmappable_skills(self, mappings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze skills with low confidence to detect gap patterns.
        
        Args:
            mappings_df: DataFrame with mapping results
            
        Returns:
            DataFrame of skills identified as potential gaps
        """
        # Filter to low confidence and needs review
        gap_candidates = mappings_df[
            (mappings_df['confidence'] == 'Low') |
            (mappings_df['needs_review'] == True)
        ].copy()
        
        if len(gap_candidates) == 0:
            print("No gap candidates found (all mappings have acceptable confidence)")
            return pd.DataFrame()
        
        print(f"Analyzing {len(gap_candidates)} potential gap candidates...")
        
        # Parse gap_analysis if it exists
        if 'gap_analysis' in gap_candidates.columns:
            gap_candidates['gap_data'] = gap_candidates['gap_analysis'].apply(
                lambda x: json.loads(x) if pd.notna(x) and x != '' else {}
            )
            
            # Extract gap types
            gap_candidates['gap_type'] = gap_candidates['gap_data'].apply(
                lambda x: x.get('gap_type', 'unknown') if x else 'unknown'
            )
        else:
            gap_candidates['gap_type'] = 'unknown'
        
        return gap_candidates
    
    def categorize_gaps(self, gap_skills_df: pd.DataFrame) -> Dict[str, List]:
        """
        Categorize gap skills by type.
        
        Args:
            gap_skills_df: DataFrame of gap candidate skills
            
        Returns:
            Dict mapping gap types to skill lists
        """
        categories = defaultdict(list)
        
        for _, row in gap_skills_df.iterrows():
            gap_type = row.get('gap_type', 'unknown')
            categories[gap_type].append({
                'skill_id': row.get('skill_id'),
                'skill_name': row.get('skill_name'),
                'grade_level': row.get('grade_level', 'N/A'),
                'semantic_similarity': row.get('semantic_similarity', 0),
                'rationale': row.get('rationale', '')
            })
        
        return dict(categories)
    
    def cluster_gap_patterns(
        self,
        gap_skills: List[Dict],
        min_cluster_size: int = 2
    ) -> Dict[int, List[Dict]]:
        """
        Use semantic clustering to group similar unmappable skills.
        
        Args:
            gap_skills: List of gap skill dicts
            min_cluster_size: Minimum skills per cluster
            
        Returns:
            Dict mapping cluster_id to skill lists
        """
        if len(gap_skills) < min_cluster_size:
            return {0: gap_skills}  # Single cluster
        
        # Extract skill names for clustering
        skill_names = [s['skill_name'] for s in gap_skills]
        
        # Use TF-IDF for text clustering
        vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(skill_names)
            
            # DBSCAN clustering
            clustering = DBSCAN(eps=0.5, min_samples=min_cluster_size, metric='cosine')
            cluster_labels = clustering.fit_predict(tfidf_matrix.toarray())
            
            # Group by cluster
            clusters = defaultdict(list)
            for skill, label in zip(gap_skills, cluster_labels):
                clusters[int(label)].append(skill)
            
            print(f"  Identified {len([k for k in clusters.keys() if k != -1])} skill clusters")
            return dict(clusters)
            
        except Exception as e:
            print(f"  Clustering failed: {e}, returning unclustered")
            return {0: gap_skills}
    
    def suggest_taxonomy_extensions(
        self,
        categories: Dict[str, List],
        clusters: Dict[int, List[Dict]]
    ) -> List[Dict]:
        """
        Suggest potential taxonomy extensions based on gap patterns.
        
        Args:
            categories: Gap skills categorized by type
            clusters: Clustered gap skills
            
        Returns:
            List of suggested taxonomy extension dicts
        """
        suggestions = []
        
        # Category-based suggestions
        category_suggestions = {
            'digital-literacy': {
                'proposed_node': 'Digital Literacy',
                'parent_pillar': 'New Pillar: 21st Century Literacies',
                'justification': 'Digital research, online comprehension, and multimedia literacy are increasingly critical but not represented in traditional Science of Reading framework.',
                'sub_nodes': ['Online Research', 'Digital Comprehension', 'Media Literacy', 'Digital Communication']
            },
            'social-emotional': {
                'proposed_node': 'Collaborative Reading',
                'parent_pillar': 'Comprehension (or new SEL-Literacy Integration pillar)',
                'justification': 'Collaboration and discussion are research-backed comprehension strategies but lack explicit representation in taxonomy.',
                'sub_nodes': ['Peer Discussion', 'Collaborative Interpretation', 'Social Annotation']
            },
            'metacognition': {
                'proposed_node': 'Metacognitive Strategies',
                'parent_pillar': 'Comprehension',
                'justification': 'Monitoring comprehension, self-questioning, and fix-up strategies are critical research-based skills.',
                'sub_nodes': ['Comprehension Monitoring', 'Self-Questioning', 'Fix-Up Strategies', 'Goal Setting']
            },
            'writing-conventions': {
                'proposed_node': 'Writing Mechanics',
                'parent_pillar': 'New Pillar: Writing (if taxonomy expands beyond reading)',
                'justification': 'Handwriting, typing, and formatting skills support literacy but are distinct from reading.',
                'sub_nodes': ['Letter Formation', 'Keyboarding', 'Formatting', 'Editing Conventions']
            }
        }
        
        for gap_type, skills in categories.items():
            if gap_type in category_suggestions and len(skills) > 0:
                suggestion = category_suggestions[gap_type].copy()
                suggestion['gap_type'] = gap_type
                suggestion['skill_count'] = len(skills)
                suggestion['example_skills'] = [s['skill_name'] for s in skills[:3]]
                suggestions.append(suggestion)
        
        # Cluster-based suggestions (for large unnamed clusters)
        for cluster_id, cluster_skills in clusters.items():
            if cluster_id == -1:  # DBSCAN noise cluster
                continue
            
            if len(cluster_skills) >= 3:  # Significant cluster
                # Extract common terms
                skill_text = ' '.join([s['skill_name'].lower() for s in cluster_skills])
                common_words = self._extract_common_terms(skill_text)
                
                # Check if this cluster doesn't match existing categories
                cluster_types = [s.get('gap_type', 'unknown') for s in cluster_skills if 'gap_type' in s]
                if cluster_types.count('unknown') == len(cluster_types):
                    # Uncategorized cluster
                    suggestions.append({
                        'proposed_node': f"Cluster {cluster_id}: {common_words[:3]}",
                        'parent_pillar': 'Unknown (requires expert review)',
                        'justification': f'Identified {len(cluster_skills)} related skills that don\'t fit existing taxonomy.',
                        'skill_count': len(cluster_skills),
                        'example_skills': [s['skill_name'] for s in cluster_skills[:3]],
                        'common_terms': common_words[:5],
                        'gap_type': 'clustered-pattern'
                    })
        
        return suggestions
    
    def _extract_common_terms(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract most common meaningful terms from text.
        """
        # Simple tokenization
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(top_n)]
    
    def generate_gap_summary(
        self,
        mappings_df: pd.DataFrame,
        gap_candidates_df: pd.DataFrame,
        categories: Dict,
        suggestions: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive gap analysis summary.
        
        Args:
            mappings_df: Full mappings DataFrame
            gap_candidates_df: Gap candidate skills
            categories: Categorized gaps
            suggestions: Taxonomy extension suggestions
            
        Returns:
            Dict with summary statistics and insights
        """
        total_skills = len(mappings_df)
        gap_count = len(gap_candidates_df)
        gap_percentage = (gap_count / total_skills * 100) if total_skills > 0 else 0
        
        # Confidence distribution
        confidence_dist = mappings_df['confidence'].value_counts().to_dict()
        
        # Category distribution
        category_dist = {k: len(v) for k, v in categories.items()}
        
        # Grade distribution of gaps
        grade_dist = gap_candidates_df['grade_level'].value_counts().head(10).to_dict() if 'grade_level' in gap_candidates_df.columns else {}
        
        summary = {
            'total_skills_mapped': total_skills,
            'gap_candidates': gap_count,
            'gap_percentage': gap_percentage,
            'confidence_distribution': confidence_dist,
            'gap_categories': category_dist,
            'grade_distribution_of_gaps': grade_dist,
            'suggested_extensions': len(suggestions),
            'high_priority_suggestions': [s for s in suggestions if s.get('skill_count', 0) >= 5]
        }
        
        return summary


def main():
    """
    Test taxonomy gap detector.
    """
    print("=" * 70)
    print("TAXONOMY GAP DETECTOR TEST")
    print("=" * 70)
    
    # Create mock data
    mock_mappings = pd.DataFrame([
        {'skill_id': '1', 'skill_name': 'Use digital tools to research', 'confidence': 'Low', 'needs_review': True, 'semantic_similarity': 0.35, 'grade_level': 'Grade 8', 'gap_analysis': '{"gap_type": "digital-literacy"}'},
        {'skill_id': '2', 'skill_name': 'Collaborate online with peers', 'confidence': 'Low', 'needs_review': True, 'semantic_similarity': 0.32, 'grade_level': 'Grade 7', 'gap_analysis': '{"gap_type": "social-emotional"}'},
        {'skill_id': '3', 'skill_name': 'Monitor own comprehension', 'confidence': 'Low', 'needs_review': True, 'semantic_similarity': 0.45, 'grade_level': 'Grade 5', 'gap_analysis': '{"gap_type": "metacognition"}'},
        {'skill_id': '4', 'skill_name': 'Identify main idea', 'confidence': 'High', 'needs_review': False, 'semantic_similarity': 0.89, 'grade_level': 'Grade 3', 'gap_analysis': ''},
        {'skill_id': '5', 'skill_name': 'Type fluently on keyboard', 'confidence': 'Low', 'needs_review': True, 'semantic_similarity': 0.28, 'grade_level': 'Grade 4', 'gap_analysis': '{"gap_type": "writing-conventions"}'},
    ])
    
    detector = TaxonomyGapDetector()
    
    # Analyze gaps
    gap_candidates = detector.analyze_unmappable_skills(mock_mappings)
    print(f"\nFound {len(gap_candidates)} gap candidates")
    
    # Categorize
    categories = detector.categorize_gaps(gap_candidates)
    print(f"\nCategories identified: {list(categories.keys())}")
    
    # Suggest extensions
    suggestions = detector.suggest_taxonomy_extensions(categories, {})
    print(f"\nSuggested {len(suggestions)} taxonomy extensions:")
    for sug in suggestions:
        print(f"  - {sug['proposed_node']} ({sug['skill_count']} skills)")
    
    # Generate summary
    summary = detector.generate_gap_summary(mock_mappings, gap_candidates, categories, suggestions)
    print(f"\nSummary:")
    print(f"  Gap Percentage: {summary['gap_percentage']:.1f}%")
    print(f"  High Priority Extensions: {len(summary['high_priority_suggestions'])}")
    
    print("\n" + "=" * 70)
    print("✓ Gap detector test completed")
    print("=" * 70)


if __name__ == '__main__':
    main()

