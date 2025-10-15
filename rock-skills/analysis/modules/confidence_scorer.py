#!/usr/bin/env python3
"""
Multi-Signal Confidence Scorer

Calculates composite confidence scores using multiple signals:
- Semantic similarity
- LLM confidence
- Grade alignment
- SoR pillar alignment
- Taxonomy depth/specificity
"""

import re
from typing import Tuple, Optional


class ConfidenceScorer:
    """
    Composite confidence scorer for taxonomy mappings.
    """
    
    # Weight configuration
    WEIGHTS = {
        'semantic': 0.40,      # Semantic similarity (embedding-based)
        'llm': 0.30,           # LLM confidence assessment
        'grade': 0.15,         # Grade-level alignment
        'pillar': 0.10,        # SoR pillar alignment
        'depth': 0.05          # Taxonomy specificity
    }
    
    # LLM confidence to numeric mapping
    LLM_SCORES = {
        'High': 1.0,
        'Medium': 0.6,
        'Low': 0.3
    }
    
    # Grade level normalization
    GRADE_MAP = {
        'Pre-K': -1,
        'Kindergarten': 0,
        'Grade K': 0,
        'Grade 1': 1,
        'Grade 2': 2,
        'Grade 3': 3,
        'Grade 4': 4,
        'Grade 5': 5,
        'Grade 6': 6,
        'Grade 7': 7,
        'Grade 8': 8,
        'Grade 9': 9,
        'Grade 10': 10,
        'Grade 11': 11,
        'Grade 12': 12,
        'High School': 11,  # Average
        'Middle School': 7   # Average
    }
    
    # SoR Pillars (from taxonomy)
    SOR_PILLARS = [
        'Phonological Awareness',
        'Phonics',
        'Fluency',
        'Vocabulary',
        'Comprehension',
        'Word Recognition',
        'Reading'
    ]
    
    def __init__(self, taxonomy_df=None):
        """
        Initialize confidence scorer.
        
        Args:
            taxonomy_df: Optional taxonomy DataFrame for pillar validation
        """
        self.taxonomy_df = taxonomy_df
    
    def normalize_grade(self, grade_str: str) -> Optional[float]:
        """
        Convert grade string to numeric value.
        
        Args:
            grade_str: Grade level string
            
        Returns:
            Numeric grade or None if invalid
        """
        if not grade_str or grade_str == 'N/A':
            return None
        
        # Direct lookup
        if grade_str in self.GRADE_MAP:
            return self.GRADE_MAP[grade_str]
        
        # Extract numeric grade
        match = re.search(r'(\d+)', grade_str)
        if match:
            return int(match.group(1))
        
        return None
    
    def check_grade_alignment(
        self,
        rock_grade: str,
        taxonomy_path: str,
        tolerance: int = 3
    ) -> bool:
        """
        Check if ROCK skill grade aligns with typical grade for taxonomy node.
        
        Note: Many skills are grade-agnostic (e.g., "decode CVC words", "use context clues")
        and should not be penalized for grade differences. This check is lenient to avoid
        false negatives for grade-agnostic skills.
        
        Args:
            rock_grade: ROCK skill grade level
            taxonomy_path: Taxonomy node path
            tolerance: Acceptable grade difference (default: ±3 grades, lenient)
            
        Returns:
            True if grades align within tolerance OR skill appears grade-agnostic
        """
        rock_grade_num = self.normalize_grade(rock_grade)
        
        if rock_grade_num is None:
            return True  # Can't verify, assume OK
        
        path_lower = taxonomy_path.lower()
        
        # Identify grade-agnostic skills (skill is same across grades)
        grade_agnostic_indicators = [
            'decoding', 'decode', 'phoneme', 'phonics', 'blend', 'segment',
            'word family', 'syllable', 'context clues', 'vocabulary',
            'fluency', 'letter', 'sound', 'morphology', 'affix'
        ]
        
        # Check if this appears to be a grade-agnostic skill
        if any(indicator in path_lower for indicator in grade_agnostic_indicators):
            return True  # Grade-agnostic skills - grade doesn't matter
        
        # For grade-dependent skills (e.g., comprehension of grade-level text),
        # check developmental appropriateness with lenient tolerance
        
        # Identify grade-dependent comprehension skills
        if 'theme' in path_lower or 'main idea' in path_lower or 'inference' in path_lower:
            # These can be grade-dependent if tied to text complexity
            # But use lenient tolerance (±3 grades) since many are still grade-agnostic
            taxonomy_grade = rock_grade_num  # Assume aligned unless specific indicators
        # Pre-K/Kindergarten foundations
        elif 'foundation' in path_lower or 'emergent' in path_lower or 'alphabet' in path_lower:
            taxonomy_grade = 0
            tolerance = 2  # Stricter for foundational skills
        # Upper grades analysis
        elif 'analysis' in path_lower or 'synthesis' in path_lower or 'critique' in path_lower:
            taxonomy_grade = 8
            tolerance = 3  # Lenient - these skills span many grades
        else:
            # No clear indicator, assume grade-agnostic
            return True
        
        # Check alignment within tolerance
        grade_diff = abs(rock_grade_num - taxonomy_grade)
        return grade_diff <= tolerance
    
    def check_pillar_alignment(self, taxonomy_path: str) -> bool:
        """
        Check if taxonomy path contains a valid SoR pillar.
        
        Args:
            taxonomy_path: Full taxonomy path
            
        Returns:
            True if contains recognized SoR pillar
        """
        for pillar in self.SOR_PILLARS:
            if pillar in taxonomy_path:
                return True
        return False
    
    def get_taxonomy_depth(self, taxonomy_path: str) -> int:
        """
        Calculate taxonomy depth (number of hierarchy levels).
        
        Args:
            taxonomy_path: Full taxonomy path
            
        Returns:
            Number of levels (e.g., 6 for full path)
        """
        # Count separators (usually ' > ')
        if ' > ' in taxonomy_path:
            return len(taxonomy_path.split(' > '))
        elif '/' in taxonomy_path:
            return len(taxonomy_path.split('/'))
        elif '|' in taxonomy_path:
            return len(taxonomy_path.split('|'))
        else:
            # Single level
            return 1
    
    def calculate_composite_score(
        self,
        semantic_similarity: float,
        llm_confidence: str,
        rock_grade: str,
        taxonomy_path: str
    ) -> Tuple[float, str]:
        """
        Calculate composite confidence score from multiple signals.
        
        Args:
            semantic_similarity: Embedding similarity score (0-1)
            llm_confidence: LLM-assigned confidence ('High'/'Medium'/'Low')
            rock_grade: ROCK skill grade level
            taxonomy_path: Mapped taxonomy path
            
        Returns:
            Tuple of (composite_score, adjusted_confidence_label)
        """
        # Validate inputs
        if not (0 <= semantic_similarity <= 1):
            semantic_similarity = max(0, min(1, semantic_similarity))
        
        if llm_confidence not in self.LLM_SCORES:
            llm_confidence = 'Medium'  # Default
        
        # Calculate individual scores
        semantic_score = semantic_similarity
        llm_score = self.LLM_SCORES[llm_confidence]
        
        # Grade alignment
        grade_aligned = self.check_grade_alignment(rock_grade, taxonomy_path)
        grade_score = 1.0 if grade_aligned else 0.5
        
        # Pillar alignment
        pillar_aligned = self.check_pillar_alignment(taxonomy_path)
        pillar_score = 1.0 if pillar_aligned else 0.5
        
        # Taxonomy depth (specificity)
        depth = self.get_taxonomy_depth(taxonomy_path)
        depth_score = min(depth / 6.0, 1.0)  # Normalize to 0-1 (6 levels max)
        
        # Weighted composite
        composite = (
            semantic_score * self.WEIGHTS['semantic'] +
            llm_score * self.WEIGHTS['llm'] +
            grade_score * self.WEIGHTS['grade'] +
            pillar_score * self.WEIGHTS['pillar'] +
            depth_score * self.WEIGHTS['depth']
        )
        
        # Re-classify based on composite score
        if composite >= 0.80:
            confidence_label = 'High'
        elif composite >= 0.60:
            confidence_label = 'Medium'
        else:
            confidence_label = 'Low'
        
        return composite, confidence_label
    
    def get_score_breakdown(
        self,
        semantic_similarity: float,
        llm_confidence: str,
        rock_grade: str,
        taxonomy_path: str
    ) -> dict:
        """
        Get detailed breakdown of confidence score calculation.
        
        Returns:
            Dict with all component scores and weights
        """
        grade_aligned = self.check_grade_alignment(rock_grade, taxonomy_path)
        pillar_aligned = self.check_pillar_alignment(taxonomy_path)
        depth = self.get_taxonomy_depth(taxonomy_path)
        
        composite, label = self.calculate_composite_score(
            semantic_similarity, llm_confidence, rock_grade, taxonomy_path
        )
        
        return {
            'composite_score': composite,
            'confidence_label': label,
            'components': {
                'semantic_similarity': {
                    'value': semantic_similarity,
                    'weight': self.WEIGHTS['semantic'],
                    'contribution': semantic_similarity * self.WEIGHTS['semantic']
                },
                'llm_confidence': {
                    'value': llm_confidence,
                    'numeric': self.LLM_SCORES[llm_confidence],
                    'weight': self.WEIGHTS['llm'],
                    'contribution': self.LLM_SCORES[llm_confidence] * self.WEIGHTS['llm']
                },
                'grade_alignment': {
                    'aligned': grade_aligned,
                    'weight': self.WEIGHTS['grade'],
                    'contribution': (1.0 if grade_aligned else 0.5) * self.WEIGHTS['grade']
                },
                'pillar_alignment': {
                    'aligned': pillar_aligned,
                    'weight': self.WEIGHTS['pillar'],
                    'contribution': (1.0 if pillar_aligned else 0.5) * self.WEIGHTS['pillar']
                },
                'taxonomy_depth': {
                    'depth': depth,
                    'normalized': min(depth / 6.0, 1.0),
                    'weight': self.WEIGHTS['depth'],
                    'contribution': min(depth / 6.0, 1.0) * self.WEIGHTS['depth']
                }
            }
        }


def main():
    """
    Test confidence scorer with sample data.
    """
    print("=" * 70)
    print("CONFIDENCE SCORER TEST")
    print("=" * 70)
    
    scorer = ConfidenceScorer()
    
    # Test Case 1: High confidence mapping
    print("\nTest Case 1: High Confidence Mapping")
    print("-" * 70)
    breakdown1 = scorer.get_score_breakdown(
        semantic_similarity=0.92,
        llm_confidence='High',
        rock_grade='Grade 1',
        taxonomy_path='Word Recognition > Phonics > Phoneme Blending > CVC Words'
    )
    
    print(f"Composite Score: {breakdown1['composite_score']:.3f}")
    print(f"Confidence Label: {breakdown1['confidence_label']}")
    print("\nComponent Contributions:")
    for component, details in breakdown1['components'].items():
        contrib = details['contribution']
        print(f"  {component:20} {contrib:.3f}")
    
    # Test Case 2: Medium confidence mapping
    print("\nTest Case 2: Medium Confidence Mapping")
    print("-" * 70)
    breakdown2 = scorer.get_score_breakdown(
        semantic_similarity=0.68,
        llm_confidence='Medium',
        rock_grade='Grade 3',
        taxonomy_path='Comprehension > Context Clues'
    )
    
    print(f"Composite Score: {breakdown2['composite_score']:.3f}")
    print(f"Confidence Label: {breakdown2['confidence_label']}")
    
    # Test Case 3: Low confidence mapping
    print("\nTest Case 3: Low Confidence Mapping")
    print("-" * 70)
    breakdown3 = scorer.get_score_breakdown(
        semantic_similarity=0.42,
        llm_confidence='Low',
        rock_grade='Grade 8',
        taxonomy_path='Digital Literacy > Research'  # Outside traditional SoR
    )
    
    print(f"Composite Score: {breakdown3['composite_score']:.3f}")
    print(f"Confidence Label: {breakdown3['confidence_label']}")
    print(f"Grade Aligned: {breakdown3['components']['grade_alignment']['aligned']}")
    print(f"Pillar Aligned: {breakdown3['components']['pillar_alignment']['aligned']}")
    
    print("\n" + "=" * 70)
    print("✓ All test cases completed")
    print("=" * 70)


if __name__ == '__main__':
    main()

