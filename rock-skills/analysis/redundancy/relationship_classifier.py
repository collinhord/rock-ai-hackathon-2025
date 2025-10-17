"""
Relationship Classifier

Classifies skill relationships into 7 types using rule-based logic:
1. TRUE_DUPLICATE - Nearly identical skills
2. SPECIFICATION_VARIANT - Same base, different specifications
3. PREREQUISITE - One builds on another
4. PROGRESSION - Learning pathway across grades
5. COMPLEMENTARY - Related but distinct
6. AMBIGUOUS - Needs human/LLM review
7. DISTINCT - Different skills

Uses multi-dimensional similarity scores and metadata to make classifications.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path
import logging

try:
    from .similarity_engine import SimilarityScore
except ImportError:
    from similarity_engine import SimilarityScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Relationship types between skills."""
    TRUE_DUPLICATE = "TRUE_DUPLICATE"
    SPECIFICATION_VARIANT = "SPECIFICATION_VARIANT"
    PREREQUISITE = "PREREQUISITE"
    PROGRESSION = "PROGRESSION"
    COMPLEMENTARY = "COMPLEMENTARY"
    AMBIGUOUS = "AMBIGUOUS"
    DISTINCT = "DISTINCT"


@dataclass
class SkillRelationship:
    """Classified relationship between two skills."""
    relationship_id: str
    skill_a_id: str
    skill_b_id: str
    skill_a_name: str
    skill_b_name: str
    
    relationship_type: RelationshipType
    confidence: float
    
    similarity_scores: Dict[str, float]
    similarity_explanation: Dict[str, any]
    
    # Classification reasoning
    classification_method: str = "rule_based"
    rule_matched: Optional[str] = None
    confidence_factors: Dict[str, float] = field(default_factory=dict)
    
    # Metadata for decision support
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'relationship_id': self.relationship_id,
            'skill_a_id': str(self.skill_a_id),
            'skill_b_id': str(self.skill_b_id),
            'skill_a_name': str(self.skill_a_name),
            'skill_b_name': str(self.skill_b_name),
            'relationship_type': self.relationship_type.value,
            'confidence': float(self.confidence),
            'similarity_scores': {k: float(v) for k, v in self.similarity_scores.items()},
            'similarity_explanation': self.similarity_explanation,
            'classification_method': self.classification_method,
            'rule_matched': self.rule_matched,
            'confidence_factors': {k: float(v) for k, v in self.confidence_factors.items()},
            'metadata': self.metadata
        }


class RelationshipClassifier:
    """
    Classifies skill relationships using rule-based logic.
    
    Implements deterministic rules for each relationship type,
    with configurable thresholds and confidence scoring.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize relationship classifier.
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.thresholds = self.config['thresholds']
        self.grade_mapping = self.config['grade_mapping']
        self.cognitive_levels = self.config['cognitive_levels']
        
        logger.info("Relationship classifier initialized")
    
    def classify(self,
                similarity_score: SimilarityScore,
                skill_a: pd.Series,
                skill_b: pd.Series) -> SkillRelationship:
        """
        Classify relationship between two skills.
        
        Args:
            similarity_score: Pre-computed similarity scores
            skill_a: First skill with metadata
            skill_b: Second skill with metadata
            
        Returns:
            SkillRelationship with classification and confidence
        """
        # Try each classification rule in priority order
        classification = self._try_true_duplicate(similarity_score, skill_a, skill_b)
        if classification:
            return classification
        
        classification = self._try_specification_variant(similarity_score, skill_a, skill_b)
        if classification:
            return classification
        
        classification = self._try_prerequisite(similarity_score, skill_a, skill_b)
        if classification:
            return classification
        
        classification = self._try_progression(similarity_score, skill_a, skill_b)
        if classification:
            return classification
        
        classification = self._try_complementary(similarity_score, skill_a, skill_b)
        if classification:
            return classification
        
        # Check for ambiguous (high similarity but no clear match)
        if similarity_score.composite >= self.thresholds['ambiguous']['composite_min']:
            return self._create_ambiguous(similarity_score, skill_a, skill_b)
        
        # Default: DISTINCT
        return self._create_distinct(similarity_score, skill_a, skill_b)
    
    def _try_true_duplicate(self,
                           sim: SimilarityScore,
                           skill_a: pd.Series,
                           skill_b: pd.Series) -> Optional[SkillRelationship]:
        """
        Rule 1: TRUE_DUPLICATE
        
        Criteria:
        - Composite ≥ 0.90
        - Structural ≥ 0.85
        - Educational ≥ 0.80
        - Same grade or adjacent
        """
        thresholds = self.thresholds['true_duplicate']
        
        if (sim.composite >= thresholds['composite_min'] and
            sim.structural >= thresholds['structural_min'] and
            sim.educational >= thresholds['educational_min']):
            
            # Check grade compatibility
            grade_compat = sim.contextual_components.get('grade_compatibility', 0)
            if grade_compat >= 0.5:  # Same or adjacent
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    rule_match=True,
                    rule_confidence=thresholds['confidence'],
                    dimension_agreement=self._dimension_agreement(sim),
                    threshold_margin=sim.composite - thresholds['composite_min'],
                    metadata_completeness=self._metadata_completeness(skill_a, skill_b)
                )
                
                return SkillRelationship(
                    relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
                    skill_a_id=skill_a['SKILL_ID'],
                    skill_b_id=skill_b['SKILL_ID'],
                    skill_a_name=skill_a['SKILL_NAME'],
                    skill_b_name=skill_b['SKILL_NAME'],
                    relationship_type=RelationshipType.TRUE_DUPLICATE,
                    confidence=confidence,
                    similarity_scores=sim.to_dict()['scores'],
                    similarity_explanation={
                        'components': sim.to_dict()['components'],
                        'evidence': sim.evidence,
                        'weights': sim.weights
                    },
                    rule_matched="true_duplicate",
                    confidence_factors={
                        'dimension_agreement': self._dimension_agreement(sim),
                        'threshold_margin': sim.composite - thresholds['composite_min'],
                        'metadata_completeness': self._metadata_completeness(skill_a, skill_b)
                    },
                    metadata=self._extract_metadata(skill_a, skill_b)
                )
        
        return None
    
    def _try_specification_variant(self,
                                   sim: SimilarityScore,
                                   skill_a: pd.Series,
                                   skill_b: pd.Series) -> Optional[SkillRelationship]:
        """
        Rule 2: SPECIFICATION_VARIANT
        
        Criteria:
        - Composite ≥ 0.75
        - Structural ≥ 0.80
        - Educational ≥ 0.70
        - Contextual < 0.60 (differs in specifications)
        """
        thresholds = self.thresholds['specification_variant']
        
        if (sim.composite >= thresholds['composite_min'] and
            sim.structural >= thresholds['structural_min'] and
            sim.educational >= thresholds['educational_min'] and
            sim.contextual < thresholds['contextual_max']):
            
            # Identify which specifications differ
            spec_diffs = self._identify_specification_differences(skill_a, skill_b)
            
            if spec_diffs:  # Must have at least one spec difference
                confidence = self._calculate_confidence(
                    rule_match=True,
                    rule_confidence=thresholds['confidence'],
                    dimension_agreement=self._dimension_agreement(sim),
                    threshold_margin=sim.composite - thresholds['composite_min'],
                    metadata_completeness=self._metadata_completeness(skill_a, skill_b)
                )
                
                return SkillRelationship(
                    relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
                    skill_a_id=skill_a['SKILL_ID'],
                    skill_b_id=skill_b['SKILL_ID'],
                    skill_a_name=skill_a['SKILL_NAME'],
                    skill_b_name=skill_b['SKILL_NAME'],
                    relationship_type=RelationshipType.SPECIFICATION_VARIANT,
                    confidence=confidence,
                    similarity_scores=sim.to_dict()['scores'],
                    similarity_explanation={
                        'components': sim.to_dict()['components'],
                        'evidence': sim.evidence,
                        'weights': sim.weights,
                        'specification_differences': spec_diffs
                    },
                    rule_matched="specification_variant",
                    metadata=self._extract_metadata(skill_a, skill_b)
                )
        
        return None
    
    def _try_prerequisite(self,
                         sim: SimilarityScore,
                         skill_a: pd.Series,
                         skill_b: pd.Series) -> Optional[SkillRelationship]:
        """
        Rule 3: PREREQUISITE
        
        Criteria:
        - 0.60 ≤ Composite ≤ 0.75
        - Educational ≥ 0.60
        - Grade difference == 1
        - Cognitive demand difference ≤ 1
        """
        thresholds = self.thresholds['prerequisite']
        
        if (thresholds['composite_min'] <= sim.composite <= thresholds['composite_max'] and
            sim.educational >= thresholds['educational_min']):
            
            # Check grade progression (exactly 1 grade apart)
            grade_diff = self._grade_difference(skill_a, skill_b)
            if abs(grade_diff) == thresholds['grade_diff']:
                
                # Check cognitive demand progression
                cog_diff = self._cognitive_difference(skill_a, skill_b)
                if abs(cog_diff) <= 1:
                    
                    confidence = self._calculate_confidence(
                        rule_match=True,
                        rule_confidence=thresholds['confidence'],
                        dimension_agreement=self._dimension_agreement(sim),
                        threshold_margin=0.05,  # Lower margin for this type
                        metadata_completeness=self._metadata_completeness(skill_a, skill_b)
                    )
                    
                    return SkillRelationship(
                        relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
                        skill_a_id=skill_a['SKILL_ID'],
                        skill_b_id=skill_b['SKILL_ID'],
                        skill_a_name=skill_a['SKILL_NAME'],
                        skill_b_name=skill_b['SKILL_NAME'],
                        relationship_type=RelationshipType.PREREQUISITE,
                        confidence=confidence,
                        similarity_scores=sim.to_dict()['scores'],
                        similarity_explanation={
                            'components': sim.to_dict()['components'],
                            'evidence': sim.evidence,
                            'weights': sim.weights,
                            'grade_progression': grade_diff,
                            'cognitive_progression': cog_diff
                        },
                        rule_matched="prerequisite",
                        metadata=self._extract_metadata(skill_a, skill_b)
                    )
        
        return None
    
    def _try_progression(self,
                        sim: SimilarityScore,
                        skill_a: pd.Series,
                        skill_b: pd.Series) -> Optional[SkillRelationship]:
        """
        Rule 4: PROGRESSION
        
        Criteria:
        - 0.55 ≤ Composite ≤ 0.75
        - Same skill domain
        - Grade difference ≥ 1
        - Cognitive demand increases
        - Structural ≥ 0.65
        """
        thresholds = self.thresholds['progression']
        
        if (thresholds['composite_min'] <= sim.composite <= thresholds['composite_max'] and
            sim.structural >= thresholds['structural_min']):
            
            # Check same domain
            domain_a = skill_a.get('skill_domain', '')
            domain_b = skill_b.get('skill_domain', '')
            if domain_a == domain_b and domain_a:
                
                # Check grade progression
                grade_diff = self._grade_difference(skill_a, skill_b)
                if abs(grade_diff) >= thresholds['min_grade_diff']:
                    
                    # Check cognitive demand progression
                    cog_diff = self._cognitive_difference(skill_a, skill_b)
                    if cog_diff > 0:  # Must increase
                        
                        confidence = self._calculate_confidence(
                            rule_match=True,
                            rule_confidence=thresholds['confidence'],
                            dimension_agreement=self._dimension_agreement(sim),
                            threshold_margin=0.05,
                            metadata_completeness=self._metadata_completeness(skill_a, skill_b)
                        )
                        
                        return SkillRelationship(
                            relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
                            skill_a_id=skill_a['SKILL_ID'],
                            skill_b_id=skill_b['SKILL_ID'],
                            skill_a_name=skill_a['SKILL_NAME'],
                            skill_b_name=skill_b['SKILL_NAME'],
                            relationship_type=RelationshipType.PROGRESSION,
                            confidence=confidence,
                            similarity_scores=sim.to_dict()['scores'],
                            similarity_explanation={
                                'components': sim.to_dict()['components'],
                                'evidence': sim.evidence,
                                'weights': sim.weights,
                                'grade_span': grade_diff,
                                'cognitive_progression': cog_diff
                            },
                            rule_matched="progression",
                            metadata=self._extract_metadata(skill_a, skill_b)
                        )
        
        return None
    
    def _try_complementary(self,
                          sim: SimilarityScore,
                          skill_a: pd.Series,
                          skill_b: pd.Series) -> Optional[SkillRelationship]:
        """
        Rule 5: COMPLEMENTARY
        
        Criteria:
        - 0.50 ≤ Composite ≤ 0.70
        - Same skill domain
        """
        thresholds = self.thresholds['complementary']
        
        if (thresholds['composite_min'] <= sim.composite <= thresholds['composite_max']):
            
            # Check same domain
            domain_a = skill_a.get('skill_domain', '')
            domain_b = skill_b.get('skill_domain', '')
            if domain_a == domain_b and domain_a:
                
                confidence = self._calculate_confidence(
                    rule_match=True,
                    rule_confidence=thresholds['confidence'],
                    dimension_agreement=self._dimension_agreement(sim),
                    threshold_margin=0.05,
                    metadata_completeness=self._metadata_completeness(skill_a, skill_b)
                )
                
                return SkillRelationship(
                    relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
                    skill_a_id=skill_a['SKILL_ID'],
                    skill_b_id=skill_b['SKILL_ID'],
                    skill_a_name=skill_a['SKILL_NAME'],
                    skill_b_name=skill_b['SKILL_NAME'],
                    relationship_type=RelationshipType.COMPLEMENTARY,
                    confidence=confidence,
                    similarity_scores=sim.to_dict()['scores'],
                    similarity_explanation={
                        'components': sim.to_dict()['components'],
                        'evidence': sim.evidence,
                        'weights': sim.weights
                    },
                    rule_matched="complementary",
                    metadata=self._extract_metadata(skill_a, skill_b)
                )
        
        return None
    
    def _create_ambiguous(self,
                         sim: SimilarityScore,
                         skill_a: pd.Series,
                         skill_b: pd.Series) -> SkillRelationship:
        """Create AMBIGUOUS relationship (needs human/LLM review)."""
        thresholds = self.thresholds['ambiguous']
        
        return SkillRelationship(
            relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
            skill_a_id=skill_a['SKILL_ID'],
            skill_b_id=skill_b['SKILL_ID'],
            skill_a_name=skill_a['SKILL_NAME'],
            skill_b_name=skill_b['SKILL_NAME'],
            relationship_type=RelationshipType.AMBIGUOUS,
            confidence=thresholds['confidence'],
            similarity_scores=sim.to_dict()['scores'],
            similarity_explanation={
                'components': sim.to_dict()['components'],
                'evidence': sim.evidence,
                'weights': sim.weights,
                'reason': 'No clear rule match despite high similarity'
            },
            rule_matched="ambiguous",
            metadata=self._extract_metadata(skill_a, skill_b)
        )
    
    def _create_distinct(self,
                        sim: SimilarityScore,
                        skill_a: pd.Series,
                        skill_b: pd.Series) -> SkillRelationship:
        """Create DISTINCT relationship."""
        thresholds = self.thresholds['distinct']
        
        return SkillRelationship(
            relationship_id=self._generate_id(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
            skill_a_id=skill_a['SKILL_ID'],
            skill_b_id=skill_b['SKILL_ID'],
            skill_a_name=skill_a['SKILL_NAME'],
            skill_b_name=skill_b['SKILL_NAME'],
            relationship_type=RelationshipType.DISTINCT,
            confidence=thresholds['confidence'],
            similarity_scores=sim.to_dict()['scores'],
            similarity_explanation={
                'components': sim.to_dict()['components'],
                'evidence': sim.evidence,
                'weights': sim.weights
            },
            rule_matched="distinct",
            metadata=self._extract_metadata(skill_a, skill_b)
        )
    
    def _calculate_confidence(self,
                             rule_match: bool,
                             rule_confidence: float,
                             dimension_agreement: float,
                             threshold_margin: float,
                             metadata_completeness: float) -> float:
        """
        Calculate classification confidence.
        
        Factors:
        - Rule match and base confidence
        - Dimension agreement (all pointing same way?)
        - Threshold margin (how far above threshold?)
        - Metadata completeness
        """
        base_confidence = rule_confidence if rule_match else 0.5
        
        # Boost for aligned dimensions
        if dimension_agreement > 0.8:
            base_confidence *= 1.1
        elif dimension_agreement < 0.5:
            base_confidence *= 0.8
        
        # Boost for clear threshold separation
        if threshold_margin > 0.15:
            base_confidence *= 1.05
        elif threshold_margin < 0.05:
            base_confidence *= 0.9
        
        # Penalize incomplete metadata
        base_confidence *= metadata_completeness
        
        return min(1.0, base_confidence)
    
    def _dimension_agreement(self, sim: SimilarityScore) -> float:
        """
        Calculate how well dimensions agree.
        
        High agreement = all dimensions similar scores
        Low agreement = contradictory signals
        """
        scores = [sim.structural, sim.educational, sim.semantic, sim.contextual]
        mean = np.mean(scores)
        std = np.std(scores)
        
        # Agreement inversely proportional to std deviation
        # std=0 -> agreement=1.0, std=0.5 -> agreement=0.0
        agreement = max(0.0, 1.0 - (std * 2.0))
        
        return agreement
    
    def _metadata_completeness(self, skill_a: pd.Series, skill_b: pd.Series) -> float:
        """Calculate metadata completeness for both skills."""
        key_fields = [
            'actions', 'targets', 'key_concepts',
            'cognitive_demand', 'task_complexity', 'skill_domain',
            'support_level', 'scope'
        ]
        
        def completeness(skill):
            filled = sum(1 for field in key_fields if field in skill and skill[field])
            return filled / len(key_fields)
        
        return (completeness(skill_a) + completeness(skill_b)) / 2
    
    def _grade_difference(self, skill_a: pd.Series, skill_b: pd.Series) -> int:
        """Calculate numeric grade difference."""
        grade_a = skill_a.get('GRADE_LEVEL_SHORT_NAME', '') or skill_a.get('GRADE_LEVEL_NAME', '')
        grade_b = skill_b.get('GRADE_LEVEL_SHORT_NAME', '') or skill_b.get('GRADE_LEVEL_NAME', '')
        
        num_a = self.grade_mapping.get(grade_a, 0)
        num_b = self.grade_mapping.get(grade_b, 0)
        
        return num_b - num_a  # Positive if b is higher grade
    
    def _cognitive_difference(self, skill_a: pd.Series, skill_b: pd.Series) -> int:
        """Calculate cognitive demand difference."""
        cog_a = skill_a.get('cognitive_demand', '')
        cog_b = skill_b.get('cognitive_demand', '')
        
        try:
            idx_a = self.cognitive_levels.index(cog_a)
            idx_b = self.cognitive_levels.index(cog_b)
            return idx_b - idx_a  # Positive if b is higher level
        except ValueError:
            return 0
    
    def _identify_specification_differences(self,
                                           skill_a: pd.Series,
                                           skill_b: pd.Series) -> Dict[str, List[str]]:
        """Identify which specifications differ between skills."""
        spec_fields = ['support_level', 'text_type', 'complexity_band', 'scope', 'text_mode']
        differences = {}
        
        for field in spec_fields:
            val_a = skill_a.get(field, '')
            val_b = skill_b.get(field, '')
            
            if val_a and val_b and val_a != val_b:
                differences[field] = [val_a, val_b]
        
        return differences
    
    def _extract_metadata(self, skill_a: pd.Series, skill_b: pd.Series) -> Dict:
        """Extract relevant metadata for decision support."""
        return {
            'skill_a': {
                'grade': skill_a.get('GRADE_LEVEL_SHORT_NAME', 'Unknown'),
                'cognitive_demand': skill_a.get('cognitive_demand', 'Unknown'),
                'support_level': skill_a.get('support_level', 'Unknown'),
                'complexity': skill_a.get('task_complexity', 'Unknown')
            },
            'skill_b': {
                'grade': skill_b.get('GRADE_LEVEL_SHORT_NAME', 'Unknown'),
                'cognitive_demand': skill_b.get('cognitive_demand', 'Unknown'),
                'support_level': skill_b.get('support_level', 'Unknown'),
                'complexity': skill_b.get('task_complexity', 'Unknown')
            }
        }
    
    def _generate_id(self, skill_a_id: str, skill_b_id: str) -> str:
        """Generate unique relationship ID."""
        # Sort to ensure consistency regardless of order
        ids = sorted([skill_a_id, skill_b_id])
        return f"REL-{ids[0]}-{ids[1]}"


if __name__ == "__main__":
    # Simple test
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from similarity_engine import SimilarityEngine
    
    print("Relationship Classifier Test")
    print("=" * 50)
    
    # Create sample skills
    skill_a = pd.Series({
        'SKILL_ID': 'SKILL-001',
        'SKILL_NAME': 'Determine main idea with support',
        'actions': 'determine|identify',
        'targets': 'main idea|central idea',
        'key_concepts': 'main idea|comprehension',
        'cognitive_demand': 'comprehension',
        'task_complexity': 'basic',
        'skill_domain': 'reading',
        'text_type': 'informational',
        'GRADE_LEVEL_SHORT_NAME': 'K',
        'scope': 'sentence',
        'support_level': 'with_support'
    })
    
    skill_b = pd.Series({
        'SKILL_ID': 'SKILL-002',
        'SKILL_NAME': 'Identify main idea independently',
        'actions': 'identify|find',
        'targets': 'main idea',
        'key_concepts': 'main idea|comprehension',
        'cognitive_demand': 'comprehension',
        'task_complexity': 'basic',
        'skill_domain': 'reading',
        'text_type': 'informational',
        'GRADE_LEVEL_SHORT_NAME': 'Grade 3',
        'scope': 'paragraph',
        'support_level': 'independent'
    })
    
    # Calculate similarity
    engine = SimilarityEngine()
    sim_score = engine.calculate_similarity(skill_a, skill_b, semantic_similarity=0.88)
    
    # Classify relationship
    classifier = RelationshipClassifier()
    relationship = classifier.classify(sim_score, skill_a, skill_b)
    
    print(f"\nSkill A: {skill_a['SKILL_NAME']}")
    print(f"Skill B: {skill_b['SKILL_NAME']}")
    print(f"\nRelationship: {relationship.relationship_type.value}")
    print(f"Confidence: {relationship.confidence:.3f}")
    print(f"Rule Matched: {relationship.rule_matched}")
    
    print("\n" + "=" * 50)
    print("✓ Test complete!")

