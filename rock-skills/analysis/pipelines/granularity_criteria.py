#!/usr/bin/env python3
"""
Granularity Criteria Module

Implements automated split/merge recommendations for base skills based on:
- Size (too many or too few member skills)
- Coherence (semantic similarity of members)
- Skill family consistency
- Silhouette analysis for multi-modal distributions

Usage:
    from granularity_criteria import GranularityAnalyzer
    
    analyzer = GranularityAnalyzer()
    recommendations = analyzer.analyze_base_skills(base_skills, metadata_df)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.metrics import silhouette_score
    from sklearn.cluster import HDBSCAN
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False
    print("Warning: clustering libraries not available. Some features will be limited.")


class GranularityAnalyzer:
    """Analyze base skills for optimal granularity and provide split/merge recommendations."""
    
    def __init__(self):
        """Initialize the granularity analyzer."""
        if CLUSTERING_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedder = None
        
        # Optimal size parameters
        self.optimal_min = 10
        self.optimal_max = 20
        self.min_acceptable = 3
        self.max_acceptable = 50
        
        # Coherence thresholds
        self.min_coherence = 0.50
        self.good_coherence = 0.70
        
        # Similarity thresholds for merging
        self.merge_threshold = 0.85
        self.merge_threshold_with_conditions = 0.75
    
    def analyze_base_skills(self, base_skills: List[Dict], 
                           metadata_df: pd.DataFrame) -> Dict:
        """
        Analyze all base skills for granularity issues.
        
        Args:
            base_skills: List of base skill definitions
            metadata_df: DataFrame with skill metadata
            
        Returns:
            Dictionary with split/merge recommendations
        """
        print("\n=== GRANULARITY ANALYSIS ===\n")
        
        recommendations = {
            'split_recommendations': [],
            'merge_recommendations': [],
            'optimal_skills': [],
            'flagged_for_review': []
        }
        
        # Analyze each base skill for split potential
        print("Analyzing base skills for split candidates...")
        for base_skill in base_skills:
            split_analysis = self.analyze_for_split(base_skill, metadata_df)
            
            if split_analysis['should_split']:
                recommendations['split_recommendations'].append(split_analysis)
                print(f"  ⚠ Split candidate: {base_skill.get('base_skill_name', 'Unknown')} "
                      f"(reason: {split_analysis['primary_reason']})")
            elif split_analysis['is_optimal']:
                recommendations['optimal_skills'].append(base_skill['base_skill_id'])
            else:
                recommendations['flagged_for_review'].append({
                    'base_skill_id': base_skill['base_skill_id'],
                    'base_skill_name': base_skill.get('base_skill_name', 'Unknown'),
                    'reason': split_analysis.get('concern', 'manual_review_needed')
                })
        
        # Analyze pairs for merge potential
        print("\nAnalyzing base skill pairs for merge candidates...")
        merge_count = 0
        for i, skill_a in enumerate(base_skills):
            for skill_b in base_skills[i+1:]:
                merge_analysis = self.analyze_for_merge(skill_a, skill_b, metadata_df)
                
                if merge_analysis['should_merge']:
                    recommendations['merge_recommendations'].append(merge_analysis)
                    merge_count += 1
                    if merge_count <= 5:  # Only print first 5
                        print(f"  ⚠ Merge candidate: '{skill_a.get('base_skill_name', 'Unknown')}' + "
                              f"'{skill_b.get('base_skill_name', 'Unknown')}' "
                              f"(reason: {merge_analysis['primary_reason']})")
        
        if merge_count > 5:
            print(f"  ... and {merge_count - 5} more merge candidates")
        
        # Summary
        print(f"\n✓ Granularity analysis complete")
        print(f"  - Split recommendations: {len(recommendations['split_recommendations'])}")
        print(f"  - Merge recommendations: {len(recommendations['merge_recommendations'])}")
        print(f"  - Optimal skills: {len(recommendations['optimal_skills'])}")
        print(f"  - Flagged for review: {len(recommendations['flagged_for_review'])}")
        
        return recommendations
    
    def analyze_for_split(self, base_skill: Dict, metadata_df: pd.DataFrame) -> Dict:
        """
        Determine if a base skill should be split.
        
        Args:
            base_skill: Base skill definition
            metadata_df: DataFrame with skill metadata
            
        Returns:
            Analysis dictionary with split recommendation
        """
        member_skill_ids = base_skill.get('member_skill_ids', [])
        
        if not member_skill_ids:
            return {
                'should_split': False,
                'is_optimal': False,
                'base_skill_id': base_skill.get('base_skill_id'),
                'concern': 'no_members'
            }
        
        member_skills = metadata_df[metadata_df['SKILL_ID'].isin(member_skill_ids)]
        
        if len(member_skills) == 0:
            return {
                'should_split': False,
                'is_optimal': False,
                'base_skill_id': base_skill.get('base_skill_id'),
                'concern': 'members_not_in_metadata'
            }
        
        reasons = []
        confidence = 'medium'
        
        # Criterion 1: Size (too many skills)
        size = len(member_skills)
        if size > self.max_acceptable:
            reasons.append({
                'criterion': 'size',
                'description': f"Too many member skills ({size} > {self.max_acceptable})",
                'severity': 'high'
            })
            confidence = 'high'
        
        # Criterion 2: Low coherence (high variance in actions)
        if 'root_verb' in member_skills.columns:
            unique_actions = member_skills['root_verb'].nunique()
            if unique_actions > 3 and size > 10:
                reasons.append({
                    'criterion': 'action_diversity',
                    'description': f"High action verb diversity ({unique_actions} unique verbs)",
                    'severity': 'medium'
                })
        
        # Criterion 3: Multi-modal distribution (embeddings form sub-clusters)
        if self.embedder and len(member_skills) >= 10:
            coherence = self.calculate_coherence(member_skills)
            if coherence < self.min_coherence:
                reasons.append({
                    'criterion': 'low_coherence',
                    'description': f"Low semantic coherence ({coherence:.3f} < {self.min_coherence})",
                    'severity': 'high'
                })
                confidence = 'high'
        
        # Criterion 4: Spans multiple skill families
        if 'skill_family' in member_skills.columns:
            unique_families = member_skills['skill_family'].nunique()
            if unique_families > 2:
                reasons.append({
                    'criterion': 'family_diversity',
                    'description': f"Spans multiple skill families ({unique_families} families)",
                    'severity': 'high'
                })
                confidence = 'high'
        
        # Determine if should split
        should_split = len(reasons) > 0 and any(r['severity'] == 'high' for r in reasons)
        
        # Check if optimal (not too small, not too large, good coherence)
        is_optimal = (
            self.optimal_min <= size <= self.optimal_max and
            len(reasons) == 0
        )
        
        return {
            'should_split': should_split,
            'is_optimal': is_optimal,
            'base_skill_id': base_skill.get('base_skill_id'),
            'base_skill_name': base_skill.get('base_skill_name', 'Unknown'),
            'member_count': size,
            'reasons': reasons,
            'primary_reason': reasons[0]['description'] if reasons else None,
            'confidence': confidence,
            'recommended_action': self.generate_split_recommendation(base_skill, member_skills, reasons)
        }
    
    def analyze_for_merge(self, skill_a: Dict, skill_b: Dict, 
                         metadata_df: pd.DataFrame) -> Dict:
        """
        Determine if two base skills should be merged.
        
        Args:
            skill_a: First base skill
            skill_b: Second base skill
            metadata_df: DataFrame with skill metadata
            
        Returns:
            Analysis dictionary with merge recommendation
        """
        reasons = []
        confidence = 'low'
        
        # Criterion 1: High semantic similarity
        name_a = skill_a.get('base_skill_name', '')
        name_b = skill_b.get('base_skill_name', '')
        
        if self.embedder and name_a and name_b:
            similarity = self.calculate_similarity(name_a, name_b)
            if similarity > self.merge_threshold:
                reasons.append({
                    'criterion': 'semantic_similarity',
                    'description': f"High semantic similarity ({similarity:.3f})",
                    'value': similarity,
                    'severity': 'high'
                })
                confidence = 'high'
        
        # Criterion 2: Same root verb + overlapping targets
        if 'root_verb' in metadata_df.columns and 'direct_objects' in metadata_df.columns:
            members_a = metadata_df[metadata_df['SKILL_ID'].isin(skill_a.get('member_skill_ids', []))]
            members_b = metadata_df[metadata_df['SKILL_ID'].isin(skill_b.get('member_skill_ids', []))]
            
            if len(members_a) > 0 and len(members_b) > 0:
                verbs_a = set(members_a['root_verb'].dropna())
                verbs_b = set(members_b['root_verb'].dropna())
                
                if verbs_a & verbs_b:  # Overlapping verbs
                    # Check target overlap if available
                    targets_a = set()
                    targets_b = set()
                    
                    for targets_str in members_a['direct_objects'].dropna():
                        if targets_str:
                            targets_a.update(str(targets_str).split('|'))
                    
                    for targets_str in members_b['direct_objects'].dropna():
                        if targets_str:
                            targets_b.update(str(targets_str).split('|'))
                    
                    if targets_a and targets_b:
                        target_overlap = len(targets_a & targets_b) / len(targets_a | targets_b)
                        if target_overlap > 0.7:
                            reasons.append({
                                'criterion': 'structural_overlap',
                                'description': f"Same verb + high target overlap ({target_overlap:.3f})",
                                'value': target_overlap,
                                'severity': 'high'
                            })
                            confidence = 'high'
        
        # Criterion 3: Only differ by specification
        if self.differs_only_by_specification(skill_a, skill_b):
            reasons.append({
                'criterion': 'specification_variant',
                'description': "Skills differ only by specifications (should be same base)",
                'severity': 'high'
            })
            confidence = 'high'
        
        # Criterion 4: Too few member skills each
        count_a = len(skill_a.get('member_skill_ids', []))
        count_b = len(skill_b.get('member_skill_ids', []))
        
        if count_a < self.min_acceptable and count_b < self.min_acceptable:
            combined_size = count_a + count_b
            if combined_size <= self.optimal_max:
                reasons.append({
                    'criterion': 'small_clusters',
                    'description': f"Both clusters small ({count_a} + {count_b} = {combined_size})",
                    'severity': 'medium'
                })
                if confidence == 'low':
                    confidence = 'medium'
        
        # Determine if should merge
        should_merge = len(reasons) > 0 and (
            any(r['severity'] == 'high' for r in reasons) or
            len(reasons) >= 2  # Multiple medium reasons
        )
        
        return {
            'should_merge': should_merge,
            'skill_a_id': skill_a.get('base_skill_id'),
            'skill_a_name': name_a,
            'skill_b_id': skill_b.get('base_skill_id'),
            'skill_b_name': name_b,
            'reasons': reasons,
            'primary_reason': reasons[0]['description'] if reasons else None,
            'confidence': confidence,
            'recommended_action': self.generate_merge_recommendation(skill_a, skill_b, reasons)
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self.embedder:
            # Fallback to simple string similarity
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        emb1 = self.embedder.encode([text1])
        emb2 = self.embedder.encode([text2])
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def calculate_coherence(self, member_skills: pd.DataFrame) -> float:
        """Calculate coherence score for member skills."""
        if not self.embedder:
            return 0.5  # Unknown
        
        if len(member_skills) < 2:
            return 1.0  # Single skill is perfectly coherent
        
        skill_names = member_skills['SKILL_NAME'].tolist()
        embeddings = self.embedder.encode(skill_names)
        
        # Calculate average pairwise similarity
        similarities = cosine_similarity(embeddings)
        n = len(similarities)
        avg_similarity = (similarities.sum() - n) / (n * (n - 1)) if n > 1 else 0
        
        return float(avg_similarity)
    
    def differs_only_by_specification(self, skill_a: Dict, skill_b: Dict) -> bool:
        """Check if two skills differ only by specifications."""
        # Simple heuristic: check if names are very similar but not identical
        name_a = skill_a.get('base_skill_name', '').lower()
        name_b = skill_b.get('base_skill_name', '').lower()
        
        if not name_a or not name_b:
            return False
        
        # Remove common specification words
        spec_words = ['with support', 'with prompting', 'independent', 'basic', 'advanced',
                     'simple', 'complex', 'grade', 'k-2', '3-5', '6-8', '9-12']
        
        clean_a = name_a
        clean_b = name_b
        
        for word in spec_words:
            clean_a = clean_a.replace(word, '')
            clean_b = clean_b.replace(word, '')
        
        # If cleaned names are very similar, they likely differ only by specs
        similarity = self.calculate_similarity(clean_a, clean_b)
        return similarity > 0.90
    
    def generate_split_recommendation(self, base_skill: Dict, 
                                     member_skills: pd.DataFrame,
                                     reasons: List[Dict]) -> Dict:
        """Generate specific recommendation for how to split a base skill."""
        if not reasons:
            return {'action': 'none'}
        
        recommendation = {
            'action': 'split',
            'method': None,
            'details': {}
        }
        
        # Determine split method based on reasons
        if any(r['criterion'] == 'family_diversity' for r in reasons):
            recommendation['method'] = 'by_skill_family'
            if 'skill_family' in member_skills.columns:
                families = member_skills['skill_family'].value_counts()
                recommendation['details'] = {
                    'families': families.to_dict(),
                    'description': f"Split into {len(families)} clusters by skill family"
                }
        
        elif any(r['criterion'] == 'action_diversity' for r in reasons):
            recommendation['method'] = 'by_root_verb'
            if 'root_verb' in member_skills.columns:
                verbs = member_skills['root_verb'].value_counts()
                recommendation['details'] = {
                    'verbs': verbs.to_dict(),
                    'description': f"Split into {len(verbs)} clusters by action verb"
                }
        
        elif any(r['criterion'] == 'low_coherence' for r in reasons):
            recommendation['method'] = 'by_semantic_subclusters'
            recommendation['details'] = {
                'description': "Use semantic clustering to identify natural sub-clusters",
                'suggested_clusters': max(2, len(member_skills) // 15)  # Aim for ~15 per cluster
            }
        
        else:
            recommendation['method'] = 'by_size'
            recommendation['details'] = {
                'description': "Split into smaller groups (manual review recommended)",
                'suggested_clusters': max(2, len(member_skills) // 20)  # Aim for ~20 per cluster
            }
        
        return recommendation
    
    def generate_merge_recommendation(self, skill_a: Dict, skill_b: Dict,
                                     reasons: List[Dict]) -> Dict:
        """Generate specific recommendation for how to merge two base skills."""
        if not reasons:
            return {'action': 'none'}
        
        recommendation = {
            'action': 'merge',
            'merged_name': None,
            'keep_skill_id': None,
            'details': {}
        }
        
        # Choose which name to keep (prefer longer, more specific name)
        name_a = skill_a.get('base_skill_name', '')
        name_b = skill_b.get('base_skill_name', '')
        
        if len(name_a) >= len(name_b):
            recommendation['merged_name'] = name_a
            recommendation['keep_skill_id'] = skill_a.get('base_skill_id')
        else:
            recommendation['merged_name'] = name_b
            recommendation['keep_skill_id'] = skill_b.get('base_skill_id')
        
        # Add details
        recommendation['details'] = {
            'primary_reason': reasons[0]['criterion'] if reasons else 'unknown',
            'member_count_combined': (len(skill_a.get('member_skill_ids', [])) + 
                                    len(skill_b.get('member_skill_ids', []))),
            'description': f"Merge into single base skill: '{recommendation['merged_name']}'"
        }
        
        return recommendation
    
    def generate_granularity_report(self, recommendations: Dict) -> Dict:
        """Generate summary report of granularity analysis."""
        report = {
            'total_split_recommendations': len(recommendations['split_recommendations']),
            'total_merge_recommendations': len(recommendations['merge_recommendations']),
            'optimal_skills_count': len(recommendations['optimal_skills']),
            'flagged_for_review_count': len(recommendations['flagged_for_review']),
            'high_confidence_splits': sum(1 for r in recommendations['split_recommendations'] 
                                         if r['confidence'] == 'high'),
            'high_confidence_merges': sum(1 for r in recommendations['merge_recommendations'] 
                                         if r['confidence'] == 'high'),
            'split_by_reason': {},
            'merge_by_reason': {}
        }
        
        # Group by primary reason
        for split_rec in recommendations['split_recommendations']:
            reason = split_rec.get('primary_reason', 'unknown')
            report['split_by_reason'][reason] = report['split_by_reason'].get(reason, 0) + 1
        
        for merge_rec in recommendations['merge_recommendations']:
            reason = merge_rec.get('primary_reason', 'unknown')
            report['merge_by_reason'][reason] = report['merge_by_reason'].get(reason, 0) + 1
        
        return report


def main():
    """Example usage of GranularityAnalyzer."""
    print("Granularity Criteria Module")
    print("=" * 50)
    print("\nThis module provides automated split/merge recommendations for base skills.")
    print("\nUsage:")
    print("  from granularity_criteria import GranularityAnalyzer")
    print("  analyzer = GranularityAnalyzer()")
    print("  recommendations = analyzer.analyze_base_skills(base_skills, metadata_df)")
    print("\nFor integration with pipelines, import the GranularityAnalyzer class.")


if __name__ == '__main__':
    main()

