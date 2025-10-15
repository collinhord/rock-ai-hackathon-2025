#!/usr/bin/env python3
"""
ROCK Skills Variant Classifier

Classifies ROCK skills into two types of relationships:
- State A: Cross-state variants (same concept, different states, same grade)
- State B: Grade progressions (related concepts, sequential grades, spiraling)

This enables:
- Content tagging once to State A groups (inherits all state variants)
- Learning progression navigation for State B (prerequisite chains)
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import uuid
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')


class VariantClassifier:
    """
    Classifier for detecting and categorizing skill variants.
    """
    
    def __init__(self, skills_df: pd.DataFrame, standard_skills_df: pd.DataFrame = None, standard_sets_df: pd.DataFrame = None):
        """
        Initialize classifier with ROCK skills data.
        
        Args:
            skills_df: DataFrame with SKILL_ID, SKILL_NAME, GRADE_LEVEL_NAME columns
            standard_skills_df: Optional DataFrame with skill-standard relationships
            standard_sets_df: Optional DataFrame with standard set metadata (includes EDUCATION_AUTHORITY)
        """
        self.skills_df = skills_df.copy()
        self.standard_skills_df = standard_skills_df
        self.standard_sets_df = standard_sets_df
        
        # Add normalized names
        self.skills_df['NORMALIZED_NAME'] = self.skills_df['SKILL_NAME'].apply(self.normalize_skill_name)
        
        # Extract grade numbers
        self.skills_df['GRADE_NUM'] = self.skills_df['GRADE_LEVEL_NAME'].apply(self.extract_grade_number)
        
        # Initialize results columns
        self.skills_df['EQUIVALENCE_TYPE'] = 'unclassified'
        self.skills_df['EQUIVALENCE_GROUP_ID'] = None
        self.skills_df['PREREQUISITE_SKILL_IDS'] = None
        self.skills_df['COMPLEXITY_LEVEL'] = None
        
        # If we have standard_skills and standard_sets, merge in education authority
        if standard_skills_df is not None and standard_sets_df is not None:
            # Join STANDARD_SKILLS with STANDARD_SETS to get EDUCATION_AUTHORITY
            skills_with_auth = standard_skills_df.merge(
                standard_sets_df[['STANDARD_SET_ID', 'EDUCATION_AUTHORITY']],
                on='STANDARD_SET_ID',
                how='left'
            )
            
            # Get unique authority per skill (handle multiple)
            skill_authorities = (skills_with_auth
                .groupby('SKILL_ID')['EDUCATION_AUTHORITY']
                .agg(lambda x: '|'.join(sorted(set(str(v) for v in x if pd.notna(v)))))
                .reset_index()
                .rename(columns={'EDUCATION_AUTHORITY': 'AUTHORITIES'}))
            
            self.skills_df = self.skills_df.merge(
                skill_authorities,
                on='SKILL_ID',
                how='left'
            )
        else:
            self.skills_df['AUTHORITIES'] = None
    
    @staticmethod
    def normalize_skill_name(name: str) -> str:
        """
        Normalize skill name for similarity comparison.
        
        Removes:
        - Common action verbs (identify, recognize, etc.)
        - Grade-specific qualifiers
        - Parenthetical examples
        - HTML tags
        - Extra whitespace
        """
        if pd.isna(name):
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(identify|recognize|understand|use|determine|analyze|demonstrate|explain|describe|know)\s+', '', name)
        
        # Remove grade-specific qualifiers
        name = re.sub(r'\s+(in|for|at)\s+grade\s+\d+', '', name)
        
        # Remove parenthetical examples
        name = re.sub(r'\s*\([^)]*\)', '', name)
        
        # Remove HTML tags
        name = re.sub(r'<[^>]+>', '', name)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name.strip()
    
    @staticmethod
    def extract_grade_number(grade_str: str) -> float:
        """
        Extract numeric grade from grade level string.
        
        Examples:
        - "Grade K" -> 0
        - "Grade 1" -> 1
        - "Grade 2-3" -> 2.5
        - "High School" -> 12
        """
        if pd.isna(grade_str):
            return np.nan
        
        grade_str = str(grade_str).upper()
        
        # Kindergarten
        if 'K' in grade_str and 'PRE' not in grade_str:
            return 0.0
        
        # Pre-K
        if 'PRE' in grade_str:
            return -1.0
        
        # High School
        if 'HIGH' in grade_str or 'HS' in grade_str:
            return 12.0
        
        # Middle School (approximate)
        if 'MIDDLE' in grade_str or 'MS' in grade_str:
            return 7.0
        
        # Elementary
        if 'ELEMENTARY' in grade_str:
            return 3.0
        
        # Extract numeric grades
        numbers = re.findall(r'\d+', grade_str)
        if numbers:
            nums = [int(n) for n in numbers]
            # If range (e.g., "2-3"), return midpoint
            return np.mean(nums)
        
        return np.nan
    
    def calculate_similarity_matrix(self, skills_subset: pd.DataFrame) -> np.ndarray:
        """
        Calculate text similarity matrix for a subset of skills.
        Uses TF-IDF + cosine similarity.
        """
        if len(skills_subset) < 2:
            return np.array([[1.0]])
        
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0
        )
        
        tfidf_matrix = vectorizer.fit_transform(skills_subset['NORMALIZED_NAME'])
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        return similarity_matrix
    
    def detect_state_a_variants(self, similarity_threshold: float = 0.85, max_grade_diff: int = 1) -> int:
        """
        Detect State A variants: cross-state redundancy.
        
        Criteria:
        - Normalized name similarity > threshold
        - Grade difference <= max_grade_diff
        - Different education authorities
        
        Returns:
            Number of State A groups found
        """
        print("Detecting State A (cross-state) variants...")
        
        # Group by normalized name (loose grouping)
        grouped = self.skills_df.groupby('NORMALIZED_NAME')
        
        state_a_count = 0
        
        for norm_name, group in grouped:
            if len(group) < 2:
                continue
            
            # Skip if all same authority (likely State B or unique)
            if self.skills_df.loc[group.index, 'AUTHORITIES'].notna().all():
                unique_auths = set()
                for auths in self.skills_df.loc[group.index, 'AUTHORITIES']:
                    if pd.notna(auths):
                        unique_auths.update(auths.split('|'))
                if len(unique_auths) < 2:
                    continue
            
            # Calculate similarity matrix
            similarity_matrix = self.calculate_similarity_matrix(group)
            
            # Find clusters of highly similar skills
            visited = set()
            
            for i, idx_i in enumerate(group.index):
                if idx_i in visited:
                    continue
                
                # Find all skills similar to this one
                similar_indices = []
                for j, idx_j in enumerate(group.index):
                    if i == j:
                        continue
                    
                    # Check similarity
                    if similarity_matrix[i, j] >= similarity_threshold:
                        # Check grade difference
                        grade_i = self.skills_df.loc[idx_i, 'GRADE_NUM']
                        grade_j = self.skills_df.loc[idx_j, 'GRADE_NUM']
                        
                        if pd.notna(grade_i) and pd.notna(grade_j):
                            if abs(grade_i - grade_j) <= max_grade_diff:
                                similar_indices.append(idx_j)
                
                # If we found similar skills across authorities, it's State A
                if similar_indices:
                    cluster_indices = [idx_i] + similar_indices
                    
                    # Check if different authorities
                    cluster_authorities = set()
                    for idx in cluster_indices:
                        auths = self.skills_df.loc[idx, 'AUTHORITIES']
                        if pd.notna(auths):
                            cluster_authorities.update(auths.split('|'))
                    
                    if len(cluster_authorities) >= 2:
                        # This is a State A group!
                        group_id = str(uuid.uuid4())
                        
                        for idx in cluster_indices:
                            self.skills_df.loc[idx, 'EQUIVALENCE_TYPE'] = 'state-variant'
                            self.skills_df.loc[idx, 'EQUIVALENCE_GROUP_ID'] = group_id
                            visited.add(idx)
                        
                        state_a_count += 1
        
        print(f"Found {state_a_count} State A groups")
        return state_a_count
    
    def detect_state_b_progressions(self, min_similarity: float = 0.6, max_similarity: float = 0.8) -> int:
        """
        Detect State B progressions: grade spiraling.
        
        Criteria:
        - Normalized name similarity between min and max (related but not identical)
        - Sequential grades (2→3→4, etc.)
        - Same authority or universal (CCSS)
        
        Returns:
            Number of State B chains found
        """
        print("Detecting State B (grade progression) patterns...")
        
        # Group by content area and rough topic (first 3 words of normalized name)
        def get_topic_key(name):
            words = name.split()[:3]
            return ' '.join(words) if words else ''
        
        self.skills_df['TOPIC_KEY'] = self.skills_df['NORMALIZED_NAME'].apply(get_topic_key)
        
        # Group by topic and authority
        if 'AUTHORITIES' in self.skills_df.columns:
            self.skills_df['PRIMARY_AUTH'] = self.skills_df['AUTHORITIES'].apply(
                lambda x: x.split('|')[0] if pd.notna(x) else None
            )
        else:
            self.skills_df['PRIMARY_AUTH'] = None
        
        grouped = self.skills_df.groupby(['CONTENT_AREA_NAME', 'TOPIC_KEY', 'PRIMARY_AUTH'])
        
        state_b_count = 0
        
        for (content_area, topic, auth), group in grouped:
            if len(group) < 2:
                continue
            
            # Skip if already classified as State A
            if (self.skills_df.loc[group.index, 'EQUIVALENCE_TYPE'] == 'state-variant').any():
                continue
            
            # Sort by grade
            group_sorted = group.sort_values('GRADE_NUM')
            
            # Look for sequential grade patterns
            grades = group_sorted['GRADE_NUM'].dropna().values
            if len(grades) < 2:
                continue
            
            # Check if grades are sequential (within 2 grade levels)
            is_sequential = True
            for i in range(len(grades) - 1):
                if grades[i+1] - grades[i] > 2:
                    is_sequential = False
                    break
            
            if not is_sequential:
                continue
            
            # Calculate similarity
            similarity_matrix = self.calculate_similarity_matrix(group_sorted)
            
            # Check if similarities are in the progression range
            avg_similarity = np.mean([similarity_matrix[i, i+1] for i in range(len(similarity_matrix)-1)])
            
            if min_similarity <= avg_similarity <= max_similarity:
                # This is a State B progression!
                group_id = str(uuid.uuid4())
                
                sorted_indices = group_sorted.index.tolist()
                
                for i, idx in enumerate(sorted_indices):
                    self.skills_df.loc[idx, 'EQUIVALENCE_TYPE'] = 'grade-progression'
                    self.skills_df.loc[idx, 'EQUIVALENCE_GROUP_ID'] = group_id
                    self.skills_df.loc[idx, 'COMPLEXITY_LEVEL'] = i + 1
                    
                    # Set prerequisites (previous skill in chain)
                    if i > 0:
                        prev_skill_id = self.skills_df.loc[sorted_indices[i-1], 'SKILL_ID']
                        self.skills_df.loc[idx, 'PREREQUISITE_SKILL_IDS'] = prev_skill_id
                
                state_b_count += 1
        
        print(f"Found {state_b_count} State B progression chains")
        return state_b_count
    
    def classify_unique_skills(self) -> int:
        """
        Mark remaining skills as 'unique' (not part of State A or B patterns).
        """
        unclassified_mask = self.skills_df['EQUIVALENCE_TYPE'] == 'unclassified'
        unique_count = unclassified_mask.sum()
        
        self.skills_df.loc[unclassified_mask, 'EQUIVALENCE_TYPE'] = 'unique'
        
        print(f"Marked {unique_count} skills as unique")
        return unique_count
    
    def run_full_classification(self) -> pd.DataFrame:
        """
        Run complete classification pipeline.
        
        Returns:
            Classified DataFrame with new columns
        """
        print("=" * 60)
        print("ROCK Skills Variant Classification")
        print("=" * 60)
        
        print(f"\nTotal skills to classify: {len(self.skills_df):,}")
        
        # Step 1: Detect State A
        state_a_count = self.detect_state_a_variants()
        
        # Step 2: Detect State B
        state_b_count = self.detect_state_b_progressions()
        
        # Step 3: Mark unique
        unique_count = self.classify_unique_skills()
        
        # Summary
        print("\n" + "=" * 60)
        print("CLASSIFICATION SUMMARY")
        print("=" * 60)
        
        type_counts = self.skills_df['EQUIVALENCE_TYPE'].value_counts()
        print(f"\nState A (cross-state variants): {type_counts.get('state-variant', 0):,} skills")
        print(f"State B (grade progressions): {type_counts.get('grade-progression', 0):,} skills")
        print(f"Unique skills: {type_counts.get('unique', 0):,} skills")
        
        print(f"\nState A groups: {state_a_count:,}")
        print(f"State B chains: {state_b_count:,}")
        
        return self.skills_df
    
    def generate_report(self, output_path: Path) -> None:
        """
        Generate comprehensive classification report CSV.
        """
        print(f"\nGenerating classification report: {output_path}")
        
        # Select relevant columns
        report_cols = [
            'SKILL_ID',
            'SKILL_NAME',
            'NORMALIZED_NAME',
            'CONTENT_AREA_NAME',
            'GRADE_LEVEL_NAME',
            'GRADE_NUM',
            'SKILL_AREA_NAME',
            'EQUIVALENCE_TYPE',
            'EQUIVALENCE_GROUP_ID',
            'PREREQUISITE_SKILL_IDS',
            'COMPLEXITY_LEVEL'
        ]
        
        if 'AUTHORITIES' in self.skills_df.columns:
            report_cols.append('AUTHORITIES')
        
        report_df = self.skills_df[report_cols].copy()
        
        # Sort by equivalence type and group ID
        report_df = report_df.sort_values([
            'EQUIVALENCE_TYPE',
            'EQUIVALENCE_GROUP_ID',
            'GRADE_NUM'
        ])
        
        report_df.to_csv(output_path, index=False)
        print(f"Report saved: {len(report_df):,} skills")
        
        # Generate group summary
        summary_path = output_path.parent / f"{output_path.stem}_summary.csv"
        
        state_a_groups = report_df[report_df['EQUIVALENCE_TYPE'] == 'state-variant'].groupby('EQUIVALENCE_GROUP_ID')
        state_b_groups = report_df[report_df['EQUIVALENCE_TYPE'] == 'grade-progression'].groupby('EQUIVALENCE_GROUP_ID')
        
        summaries = []
        
        # State A summaries
        for group_id, group in state_a_groups:
            summaries.append({
                'GROUP_ID': group_id,
                'TYPE': 'state-variant',
                'MEMBER_COUNT': len(group),
                'EXAMPLE_SKILL': group.iloc[0]['SKILL_NAME'],
                'CONTENT_AREA': group.iloc[0]['CONTENT_AREA_NAME'],
                'GRADE_RANGE': f"{group['GRADE_NUM'].min():.0f}-{group['GRADE_NUM'].max():.0f}",
                'AUTHORITIES': len(set(str(a) for a in group['AUTHORITIES'] if pd.notna(a)))
            })
        
        # State B summaries
        for group_id, group in state_b_groups:
            summaries.append({
                'GROUP_ID': group_id,
                'TYPE': 'grade-progression',
                'MEMBER_COUNT': len(group),
                'EXAMPLE_SKILL': group.iloc[0]['SKILL_NAME'],
                'CONTENT_AREA': group.iloc[0]['CONTENT_AREA_NAME'],
                'GRADE_RANGE': f"{group['GRADE_NUM'].min():.0f}-{group['GRADE_NUM'].max():.0f}",
                'AUTHORITIES': 'N/A (progression)'
            })
        
        summary_df = pd.DataFrame(summaries)
        summary_df.to_csv(summary_path, index=False)
        print(f"Summary saved: {len(summary_df):,} groups")


def main():
    """
    Main execution function.
    """
    print("ROCK Skills Variant Classifier")
    print("=" * 60)
    
    # Load data
    schema_dir = Path('../../rock_schemas')
    output_dir = Path('..')
    
    print("\nLoading SKILLS.csv...")
    # OPTIMIZATION: Load only essential columns
    essential_columns = [
        'SKILL_ID',
        'SKILL_NAME',
        'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME',
        'GRADE_LEVEL_NAME'
    ]
    skills_df = pd.read_csv(schema_dir / 'SKILLS.csv', usecols=essential_columns)
    print(f"Loaded {len(skills_df):,} skills (optimized: {len(essential_columns)} columns)")
    
    # Try to load STANDARD_SKILLS and STANDARD_SETS for authority information
    try:
        print("\nLoading STANDARD_SKILLS.csv (sampling first 2M rows)...")
        # OPTIMIZATION: Load only columns needed for authority lookup
        standard_skills_columns = ['SKILL_ID', 'STANDARD_SET_ID']
        standard_skills_chunks = []
        for i, chunk in enumerate(pd.read_csv(
            schema_dir / 'STANDARD_SKILLS.csv', 
            usecols=standard_skills_columns,
            chunksize=100000
        )):
            standard_skills_chunks.append(chunk)
            if i >= 19:  # 2M rows
                break
        standard_skills_df = pd.concat(standard_skills_chunks, ignore_index=True)
        print(f"Loaded {len(standard_skills_df):,} skill-standard relationships (optimized: {len(standard_skills_columns)} columns)")
        
        print("\nLoading STANDARD_SETS.csv...")
        standard_sets_df = pd.read_csv(schema_dir / 'STANDARD_SETS.csv')
        print(f"Loaded {len(standard_sets_df):,} standard sets")
    except Exception as e:
        print(f"Warning: Could not load STANDARD_SKILLS/SETS: {e}")
        standard_skills_df = None
        standard_sets_df = None
    
    # Run classification
    classifier = VariantClassifier(skills_df, standard_skills_df, standard_sets_df)
    classified_df = classifier.run_full_classification()
    
    # Generate report
    output_path = output_dir / 'variant-classification-report.csv'
    classifier.generate_report(output_path)
    
    print("\n" + "=" * 60)
    print("Classification complete!")
    print("=" * 60)
    
    return classified_df


if __name__ == '__main__':
    classified_df = main()

