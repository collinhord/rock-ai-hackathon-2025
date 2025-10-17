#!/usr/bin/env python3
"""
Quality Metrics Module

Comprehensive quality assessment for base skills including:
- Coherence scoring (cluster tightness)
- Granularity scoring (appropriate size)
- Coverage scoring (variant diversity)
- SoR alignment scoring (scientific validity)

Usage:
    from quality_metrics import QualityMetricsCalculator
    
    calculator = QualityMetricsCalculator()
    quality = calculator.calculate_base_skill_quality(base_skill, metadata_df, sor_taxonomy)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.metrics import silhouette_score
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Some quality metrics will be limited.")


class QualityMetricsCalculator:
    """Calculate comprehensive quality metrics for base skills."""
    
    def __init__(self):
        """Initialize the quality metrics calculator."""
        if EMBEDDINGS_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedder = None
    
    def calculate_base_skill_quality(self, base_skill: Dict, 
                                     metadata_df: pd.DataFrame,
                                     sor_taxonomy: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calculate multi-dimensional quality score for a base skill.
        
        Args:
            base_skill: Base skill definition
            metadata_df: DataFrame with skill metadata
            sor_taxonomy: Optional Science of Reading taxonomy
            
        Returns:
            Dictionary with quality metrics
        """
        member_skill_ids = base_skill.get('member_skill_ids', [])
        
        if not member_skill_ids:
            return self._empty_quality_scores()
        
        member_skills = metadata_df[metadata_df['SKILL_ID'].isin(member_skill_ids)]
        
        if len(member_skills) == 0:
            return self._empty_quality_scores()
        
        # Metric 1: Coherence (how similar are member skills?)
        coherence_score = self.calculate_coherence(member_skills)
        
        # Metric 2: Granularity (appropriate size and scope?)
        granularity_score = self.calculate_granularity(member_skills)
        
        # Metric 3: Coverage (does it cover distinct variants well?)
        coverage_score = self.calculate_coverage(member_skills)
        
        # Metric 4: SoR Alignment (matches research-based concepts?)
        sor_alignment_score = self.calculate_sor_alignment(base_skill, sor_taxonomy) if sor_taxonomy is not None else 0.5
        
        # Overall quality (weighted average)
        overall = (
            0.35 * coherence_score +
            0.25 * granularity_score +
            0.25 * coverage_score +
            0.15 * sor_alignment_score
        )
        
        return {
            'coherence_score': float(coherence_score),
            'granularity_score': float(granularity_score),
            'coverage_score': float(coverage_score),
            'sor_alignment_score': float(sor_alignment_score),
            'overall_quality': float(overall),
            'grade': 'A' if overall >= 0.85 else 'B' if overall >= 0.70 else 'C' if overall >= 0.55 else 'D',
            'member_count': len(member_skills),
            'base_skill_id': base_skill.get('base_skill_id', 'unknown')
        }
    
    def calculate_coherence(self, member_skills: pd.DataFrame) -> float:
        """
        Calculate coherence score (cluster tightness).
        
        High coherence = member skills are semantically similar
        
        Args:
            member_skills: DataFrame of member skills
            
        Returns:
            Coherence score (0-1)
        """
        if len(member_skills) < 2:
            return 1.0  # Single skill is perfectly coherent
        
        if not self.embedder:
            # Fallback: use simple heuristic based on shared words
            return self._calculate_lexical_coherence(member_skills)
        
        # Calculate embeddings
        skill_names = member_skills['SKILL_NAME'].tolist()
        embeddings = self.embedder.encode(skill_names)
        
        # Calculate pairwise cosine similarities
        similarities = cosine_similarity(embeddings)
        
        # Average similarity (excluding diagonal)
        n = len(similarities)
        avg_similarity = (similarities.sum() - n) / (n * (n - 1)) if n > 1 else 0
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        coherence = (avg_similarity + 1) / 2
        
        return float(np.clip(coherence, 0, 1))
    
    def _calculate_lexical_coherence(self, member_skills: pd.DataFrame) -> float:
        """
        Fallback coherence calculation using lexical overlap.
        
        Args:
            member_skills: DataFrame of member skills
            
        Returns:
            Coherence score (0-1)
        """
        skill_names = member_skills['SKILL_NAME'].tolist()
        
        # Tokenize and get unique words per skill
        skill_words = [set(name.lower().split()) for name in skill_names]
        
        # Calculate Jaccard similarity for each pair
        similarities = []
        for i in range(len(skill_words)):
            for j in range(i + 1, len(skill_words)):
                intersection = len(skill_words[i] & skill_words[j])
                union = len(skill_words[i] | skill_words[j])
                if union > 0:
                    similarities.append(intersection / union)
        
        return np.mean(similarities) if similarities else 0.5
    
    def calculate_granularity(self, member_skills: pd.DataFrame) -> float:
        """
        Calculate granularity score (appropriate size).
        
        Optimal size is around 10-20 skills per base skill.
        Too few = over-fragmentation
        Too many = over-generalization
        
        Args:
            member_skills: DataFrame of member skills
            
        Returns:
            Granularity score (0-1)
        """
        size = len(member_skills)
        
        # Optimal range: 10-20 skills
        optimal_min = 10
        optimal_max = 20
        
        if optimal_min <= size <= optimal_max:
            return 1.0
        elif size < optimal_min:
            # Penalty for being too small (min acceptable: 3)
            return max(0.3, (size - 3) / (optimal_min - 3)) if size >= 3 else 0.0
        else:
            # Penalty for being too large (max acceptable: 50)
            return max(0.3, 1.0 - (size - optimal_max) / (50 - optimal_max)) if size <= 50 else 0.3
    
    def calculate_coverage(self, member_skills: pd.DataFrame) -> float:
        """
        Calculate coverage score (variant diversity).
        
        Good coverage = skills cover multiple specification combinations
        
        Args:
            member_skills: DataFrame of member skills
            
        Returns:
            Coverage score (0-1)
        """
        # Count unique specification combinations
        spec_fields = ['text_type', 'complexity_band', 'support_level', 'cognitive_demand', 'scope']
        
        available_fields = [f for f in spec_fields if f in member_skills.columns]
        
        if not available_fields:
            return 0.5  # No spec data available
        
        # Count unique combinations
        unique_combinations = member_skills[available_fields].drop_duplicates()
        num_unique = len(unique_combinations)
        
        # Good coverage = 10+ unique variants
        coverage = min(1.0, num_unique / 10)
        
        return float(coverage)
    
    def calculate_sor_alignment(self, base_skill: Dict, sor_taxonomy: pd.DataFrame) -> float:
        """
        Calculate SoR (Science of Reading) alignment score.
        
        Checks if base skill aligns with research-based concepts.
        
        Args:
            base_skill: Base skill definition
            sor_taxonomy: Science of Reading taxonomy
            
        Returns:
            Alignment score (0-1)
        """
        if sor_taxonomy is None or len(sor_taxonomy) == 0:
            return 0.5  # Unknown
        
        base_skill_name = base_skill.get('base_skill_name', '').lower()
        
        if not base_skill_name:
            return 0.0
        
        # Check for direct matches or high semantic similarity
        sor_concepts = sor_taxonomy['Skill'].tolist() if 'Skill' in sor_taxonomy.columns else []
        
        if not sor_concepts:
            return 0.5
        
        # Simple lexical matching (can be enhanced with embeddings)
        best_match_score = 0.0
        
        for sor_concept in sor_concepts:
            sor_concept_lower = str(sor_concept).lower()
            
            # Check for substring matches
            if base_skill_name in sor_concept_lower or sor_concept_lower in base_skill_name:
                best_match_score = max(best_match_score, 0.8)
            
            # Check for word overlap
            base_words = set(base_skill_name.split())
            sor_words = set(sor_concept_lower.split())
            
            if base_words and sor_words:
                overlap = len(base_words & sor_words)
                total = len(base_words | sor_words)
                if total > 0:
                    score = overlap / total
                    best_match_score = max(best_match_score, score)
        
        return float(min(1.0, best_match_score))
    
    def _empty_quality_scores(self) -> Dict:
        """Return empty/default quality scores."""
        return {
            'coherence_score': 0.0,
            'granularity_score': 0.0,
            'coverage_score': 0.0,
            'sor_alignment_score': 0.0,
            'overall_quality': 0.0,
            'grade': 'F',
            'member_count': 0
        }
    
    def generate_quality_report(self, base_skills: List[Dict], 
                                metadata_df: pd.DataFrame,
                                sor_taxonomy: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive quality report for all base skills.
        
        Args:
            base_skills: List of base skill definitions
            metadata_df: DataFrame with skill metadata
            sor_taxonomy: Optional Science of Reading taxonomy
            
        Returns:
            Quality report dictionary
        """
        print("\n=== QUALITY METRICS CALCULATION ===\n")
        
        quality_scores = []
        
        for base_skill in base_skills:
            quality = self.calculate_base_skill_quality(base_skill, metadata_df, sor_taxonomy)
            quality_scores.append(quality)
        
        # Calculate aggregate statistics
        df_quality = pd.DataFrame(quality_scores)
        
        report = {
            'total_base_skills': len(base_skills),
            'average_quality': float(df_quality['overall_quality'].mean()),
            'median_quality': float(df_quality['overall_quality'].median()),
            'quality_distribution': {
                'A': int((df_quality['grade'] == 'A').sum()),
                'B': int((df_quality['grade'] == 'B').sum()),
                'C': int((df_quality['grade'] == 'C').sum()),
                'D': int((df_quality['grade'] == 'D').sum()),
                'F': int((df_quality['grade'] == 'F').sum())
            },
            'average_metrics': {
                'coherence': float(df_quality['coherence_score'].mean()),
                'granularity': float(df_quality['granularity_score'].mean()),
                'coverage': float(df_quality['coverage_score'].mean()),
                'sor_alignment': float(df_quality['sor_alignment_score'].mean())
            },
            'flagged_for_review': [
                {
                    'base_skill_id': score['base_skill_id'],
                    'overall_quality': score['overall_quality'],
                    'grade': score['grade'],
                    'reason': self._get_flagged_reason(score)
                }
                for score in quality_scores
                if score['overall_quality'] < 0.70
            ],
            'top_quality': [
                {
                    'base_skill_id': score['base_skill_id'],
                    'overall_quality': score['overall_quality'],
                    'grade': score['grade']
                }
                for score in sorted(quality_scores, key=lambda x: x['overall_quality'], reverse=True)[:10]
            ],
            'quality_scores': quality_scores
        }
        
        print(f"✓ Calculated quality metrics for {len(base_skills)} base skills")
        print(f"  Average Quality: {report['average_quality']:.3f}")
        print(f"  Grade Distribution: A={report['quality_distribution']['A']}, "
              f"B={report['quality_distribution']['B']}, "
              f"C={report['quality_distribution']['C']}, "
              f"D={report['quality_distribution']['D']}, "
              f"F={report['quality_distribution']['F']}")
        print(f"  Flagged for Review: {len(report['flagged_for_review'])}")
        
        return report
    
    def _get_flagged_reason(self, quality_score: Dict) -> str:
        """Determine why a base skill was flagged for review."""
        reasons = []
        
        if quality_score['coherence_score'] < 0.50:
            reasons.append('low_coherence')
        if quality_score['granularity_score'] < 0.50:
            reasons.append('poor_granularity')
        if quality_score['coverage_score'] < 0.30:
            reasons.append('insufficient_coverage')
        if quality_score['sor_alignment_score'] < 0.40:
            reasons.append('low_sor_alignment')
        
        return ', '.join(reasons) if reasons else 'overall_low_quality'


class ValidationSetManager:
    """Manage gold-standard validation sets for testing."""
    
    def __init__(self, validation_set_path: Optional[str] = None):
        """
        Initialize validation set manager.
        
        Args:
            validation_set_path: Path to validation set CSV (optional)
        """
        self.validation_set_path = validation_set_path
        self.validation_set = None
        
        if validation_set_path and Path(validation_set_path).exists():
            self.load_validation_set()
    
    def load_validation_set(self):
        """Load validation set from file."""
        try:
            self.validation_set = pd.read_csv(self.validation_set_path)
            print(f"✓ Loaded validation set: {len(self.validation_set)} gold-standard base skills")
        except Exception as e:
            print(f"⚠ Could not load validation set: {e}")
            self.validation_set = None
    
    def create_default_validation_set(self) -> pd.DataFrame:
        """Create a default validation set with manually curated examples."""
        gold_standard = [
            {
                'base_skill_id': 'GOLD-001',
                'base_skill_name': 'Determine Main Idea',
                'expected_member_count_range_min': 10,
                'expected_member_count_range_max': 30,
                'expected_specifications': 'text_type, complexity_band, support_level',
                'sor_alignment': 'Main Idea & Summaries',
                'quality_grade': 'A'
            },
            {
                'base_skill_id': 'GOLD-002',
                'base_skill_name': 'Analyze Character Motivation',
                'expected_member_count_range_min': 5,
                'expected_member_count_range_max': 15,
                'expected_specifications': 'text_type, complexity_band, scope',
                'sor_alignment': 'Infer Character Motivation',
                'quality_grade': 'A'
            },
            {
                'base_skill_id': 'GOLD-003',
                'base_skill_name': 'Compare Narrative Structures',
                'expected_member_count_range_min': 8,
                'expected_member_count_range_max': 20,
                'expected_specifications': 'text_type, complexity_band, scope, quantity',
                'sor_alignment': 'Analyze Text Structure',
                'quality_grade': 'A'
            },
            {
                'base_skill_id': 'GOLD-004',
                'base_skill_name': 'Decode Multisyllabic Words',
                'expected_member_count_range_min': 5,
                'expected_member_count_range_max': 12,
                'expected_specifications': 'complexity_band, support_level',
                'sor_alignment': 'Multisyllabic Word Decoding',
                'quality_grade': 'A'
            },
            {
                'base_skill_id': 'GOLD-005',
                'base_skill_name': 'Identify Supporting Details',
                'expected_member_count_range_min': 12,
                'expected_member_count_range_max': 25,
                'expected_specifications': 'text_type, complexity_band, support_level, scope',
                'sor_alignment': 'Details & Evidence',
                'quality_grade': 'A'
            }
        ]
        
        self.validation_set = pd.DataFrame(gold_standard)
        return self.validation_set
    
    def save_validation_set(self, path: str):
        """Save validation set to file."""
        if self.validation_set is not None:
            self.validation_set.to_csv(path, index=False)
            print(f"✓ Saved validation set to {path}")
        else:
            print("⚠ No validation set to save")


def main():
    """Example usage of QualityMetricsCalculator."""
    print("Quality Metrics Module")
    print("=" * 50)
    print("\nThis module provides comprehensive quality assessment for base skills.")
    print("\nUsage:")
    print("  from quality_metrics import QualityMetricsCalculator")
    print("  calculator = QualityMetricsCalculator()")
    print("  quality = calculator.calculate_base_skill_quality(base_skill, metadata_df)")
    print("\nFor full pipeline integration, use generate_quality_report().")


if __name__ == '__main__':
    main()

