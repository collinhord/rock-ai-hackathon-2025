"""
Recommendation Engine

Generates actionable recommendations and prioritization for skill relationships.

For each relationship type, provides:
- Specific action recommendations
- Priority scoring
- Impact analysis
- Decision support information
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path
import logging

try:
    from .relationship_classifier import SkillRelationship, RelationshipType
except ImportError:
    from relationship_classifier import SkillRelationship, RelationshipType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Recommended action types."""
    MERGE = "MERGE"
    CREATE_BASE_SKILL = "CREATE_BASE_SKILL"
    ADD_SPECIFICATION = "ADD_SPECIFICATION"
    CAPTURE_DEPENDENCY = "CAPTURE_DEPENDENCY"
    CREATE_PROGRESSION = "CREATE_PROGRESSION"
    CAPTURE_RELATIONSHIP = "CAPTURE_RELATIONSHIP"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    NO_ACTION = "NO_ACTION"


@dataclass
class Recommendation:
    """Actionable recommendation for a skill relationship."""
    relationship_id: str
    relationship_type: RelationshipType
    
    action: ActionType
    priority: str  # P0, P1, P2, P3
    priority_score: float
    
    rationale: str
    specific_steps: List[str]
    
    # Impact analysis
    impact: Dict[str, any] = field(default_factory=dict)
    
    # Decision support
    quality_comparison: Optional[Dict] = None
    suggested_base_skill_name: Optional[str] = None
    specification_tags: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'relationship_id': self.relationship_id,
            'relationship_type': self.relationship_type.value,
            'action': self.action.value,
            'priority': self.priority,
            'priority_score': float(self.priority_score),
            'rationale': self.rationale,
            'specific_steps': self.specific_steps,
            'impact': self.impact,
            'quality_comparison': {k: float(v) if isinstance(v, (int, float)) else v 
                                  for k, v in self.quality_comparison.items()} if self.quality_comparison else None,
            'suggested_base_skill_name': self.suggested_base_skill_name,
            'specification_tags': self.specification_tags
        }


class RecommendationEngine:
    """
    Generates actionable recommendations for skill relationships.
    
    Implements decision trees for each relationship type with
    priority scoring and impact analysis.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize recommendation engine.
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.priority_weights = self.config['priority_weights']
        self.priority_buckets = self.config['priority_buckets']
        
        logger.info("Recommendation engine initialized")
    
    def generate_recommendation(self,
                               relationship: SkillRelationship,
                               skill_a: pd.Series,
                               skill_b: pd.Series,
                               metadata_df: Optional[pd.DataFrame] = None) -> Recommendation:
        """
        Generate recommendation for a skill relationship.
        
        Args:
            relationship: Classified skill relationship
            skill_a: First skill with full metadata
            skill_b: Second skill with full metadata
            metadata_df: Full metadata DataFrame (for impact analysis)
            
        Returns:
            Recommendation with action, priority, and rationale
        """
        # Route to appropriate decision tree
        if relationship.relationship_type == RelationshipType.TRUE_DUPLICATE:
            return self._recommend_true_duplicate(relationship, skill_a, skill_b, metadata_df)
        
        elif relationship.relationship_type == RelationshipType.SPECIFICATION_VARIANT:
            return self._recommend_specification_variant(relationship, skill_a, skill_b)
        
        elif relationship.relationship_type == RelationshipType.PREREQUISITE:
            return self._recommend_prerequisite(relationship, skill_a, skill_b)
        
        elif relationship.relationship_type == RelationshipType.PROGRESSION:
            return self._recommend_progression(relationship, skill_a, skill_b)
        
        elif relationship.relationship_type == RelationshipType.COMPLEMENTARY:
            return self._recommend_complementary(relationship, skill_a, skill_b)
        
        elif relationship.relationship_type == RelationshipType.AMBIGUOUS:
            return self._recommend_ambiguous(relationship, skill_a, skill_b)
        
        else:  # DISTINCT
            return self._recommend_distinct(relationship, skill_a, skill_b)
    
    def _recommend_true_duplicate(self,
                                  rel: SkillRelationship,
                                  skill_a: pd.Series,
                                  skill_b: pd.Series,
                                  metadata_df: Optional[pd.DataFrame]) -> Recommendation:
        """
        Decision tree for TRUE_DUPLICATE.
        
        Logic:
        - If same state: Merge, keep higher quality
        - If different states: Create base skill, keep both as variants
        - If one clearly higher quality: Keep high quality, deprecate other
        """
        quality_a = self._calculate_quality_score(skill_a, metadata_df)
        quality_b = self._calculate_quality_score(skill_b, metadata_df)
        
        quality_comparison = {
            'skill_a_quality': quality_a,
            'skill_b_quality': quality_b,
            'difference': abs(quality_a - quality_b)
        }
        
        # Determine action
        if quality_comparison['difference'] > 0.2:
            # Clear quality winner
            if quality_a > quality_b:
                action = ActionType.MERGE
                steps = [
                    f"Keep Skill A ({skill_a['SKILL_ID']}) as canonical",
                    f"Deprecate Skill B ({skill_b['SKILL_ID']})",
                    "Create migration mapping for content",
                    "Update all references to point to Skill A"
                ]
                rationale = f"Skill A has significantly higher quality ({quality_a:.2f} vs {quality_b:.2f})"
            else:
                action = ActionType.MERGE
                steps = [
                    f"Keep Skill B ({skill_b['SKILL_ID']}) as canonical",
                    f"Deprecate Skill A ({skill_a['SKILL_ID']})",
                    "Create migration mapping for content",
                    "Update all references to point to Skill B"
                ]
                rationale = f"Skill B has significantly higher quality ({quality_b:.2f} vs {quality_a:.2f})"
        else:
            # Similar quality - create base skill
            action = ActionType.CREATE_BASE_SKILL
            base_name = self._suggest_base_skill_name(skill_a, skill_b)
            steps = [
                f"Create new base skill: '{base_name}'",
                "Keep both skills as state/context variants",
                "Tag variants with appropriate specifications",
                "Link content to base skill for cross-state discovery"
            ]
            rationale = "Both skills have similar quality; create unified base skill for better taxonomy"
        
        # Calculate priority
        priority_score = self._calculate_priority_score(
            confidence=rel.confidence,
            impact=self._estimate_impact(skill_a, skill_b, metadata_df),
            taxonomy_importance=0.9,  # Duplicates are high importance
            data_quality_concern=1.0 - min(quality_a, quality_b)
        )
        
        priority = self._score_to_bucket(priority_score)
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=action,
            priority=priority,
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, metadata_df),
            quality_comparison=quality_comparison,
            suggested_base_skill_name=self._suggest_base_skill_name(skill_a, skill_b) if action == ActionType.CREATE_BASE_SKILL else None
        )
    
    def _recommend_specification_variant(self,
                                         rel: SkillRelationship,
                                         skill_a: pd.Series,
                                         skill_b: pd.Series) -> Recommendation:
        """
        Decision tree for SPECIFICATION_VARIANT.
        
        Logic:
        - Create base skill with specification tags
        - Identify which specifications differentiate the variants
        """
        spec_diffs = rel.similarity_explanation.get('specification_differences', {})
        base_name = self._suggest_base_skill_name(skill_a, skill_b)
        
        steps = [
            f"Create base skill: '{base_name}'",
            "Consolidate both skills under this base",
            f"Apply specification tags: {', '.join(spec_diffs.keys())}",
            "Enable querying by specification combinations"
        ]
        
        rationale = f"Same core competency with {len(spec_diffs)} specification differences: {', '.join(spec_diffs.keys())}"
        
        priority_score = self._calculate_priority_score(
            confidence=rel.confidence,
            impact=self._estimate_impact(skill_a, skill_b, None),
            taxonomy_importance=0.85,
            data_quality_concern=0.2
        )
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.CREATE_BASE_SKILL,
            priority=self._score_to_bucket(priority_score),
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, None),
            suggested_base_skill_name=base_name,
            specification_tags=spec_diffs
        )
    
    def _recommend_prerequisite(self,
                               rel: SkillRelationship,
                               skill_a: pd.Series,
                               skill_b: pd.Series) -> Recommendation:
        """
        Decision tree for PREREQUISITE.
        
        Logic:
        - Capture dependency relationship
        - Create learning pathway
        """
        grade_prog = rel.similarity_explanation.get('grade_progression', 0)
        direction = "A → B" if grade_prog > 0 else "B → A"
        
        steps = [
            f"Create prerequisite relationship: Skill {direction}",
            "Add prerequisite_skill_id field to dependent skill",
            "Flag for content sequencing system",
            "Consider in learning pathway generation"
        ]
        
        rationale = f"Skills form prerequisite relationship across grade progression ({direction})"
        
        priority_score = self._calculate_priority_score(
            confidence=rel.confidence,
            impact=self._estimate_impact(skill_a, skill_b, None),
            taxonomy_importance=0.7,
            data_quality_concern=0.1
        )
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.CAPTURE_DEPENDENCY,
            priority=self._score_to_bucket(priority_score),
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, None)
        )
    
    def _recommend_progression(self,
                              rel: SkillRelationship,
                              skill_a: pd.Series,
                              skill_b: pd.Series) -> Recommendation:
        """
        Decision tree for PROGRESSION.
        
        Logic:
        - Organize into vertical learning pathway
        - Create progression strand
        """
        grade_span = rel.similarity_explanation.get('grade_span', 0)
        
        steps = [
            "Create progression_strand_id to group skills",
            f"Order by grade level (span: {abs(grade_span)} grades)",
            "Order by cognitive demand within grade",
            "Identify cross-grade content alignment opportunities"
        ]
        
        rationale = f"Skills form learning progression across {abs(grade_span)} grades in same domain"
        
        priority_score = self._calculate_priority_score(
            confidence=rel.confidence,
            impact=self._estimate_impact(skill_a, skill_b, None),
            taxonomy_importance=0.6,
            data_quality_concern=0.1
        )
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.CREATE_PROGRESSION,
            priority=self._score_to_bucket(priority_score),
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, None)
        )
    
    def _recommend_complementary(self,
                                rel: SkillRelationship,
                                skill_a: pd.Series,
                                skill_b: pd.Series) -> Recommendation:
        """Decision tree for COMPLEMENTARY."""
        steps = [
            "Create related_skill_ids field",
            "Capture bidirectional relationship",
            "Flag for co-teaching opportunities",
            "Consider for content bundling"
        ]
        
        rationale = "Related skills that support each other but remain distinct"
        
        priority_score = self._calculate_priority_score(
            confidence=rel.confidence,
            impact=self._estimate_impact(skill_a, skill_b, None),
            taxonomy_importance=0.4,
            data_quality_concern=0.0
        )
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.CAPTURE_RELATIONSHIP,
            priority=self._score_to_bucket(priority_score),
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, None)
        )
    
    def _recommend_ambiguous(self,
                            rel: SkillRelationship,
                            skill_a: pd.Series,
                            skill_b: pd.Series) -> Recommendation:
        """Decision tree for AMBIGUOUS."""
        steps = [
            "Review similarity scores and evidence",
            "Examine all 23 metadata fields side-by-side",
            "Consider LLM analysis for nuanced judgment",
            "Make manual classification decision",
            "Document rationale for future reference"
        ]
        
        rationale = "High similarity but no clear rule match; requires human judgment"
        
        # High priority for review
        priority_score = self._calculate_priority_score(
            confidence=0.5,  # Low confidence
            impact=self._estimate_impact(skill_a, skill_b, None),
            taxonomy_importance=0.7,  # Important to resolve
            data_quality_concern=0.5
        )
        
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.HUMAN_REVIEW,
            priority=self._score_to_bucket(priority_score),
            priority_score=priority_score,
            rationale=rationale,
            specific_steps=steps,
            impact=self._estimate_impact(skill_a, skill_b, None)
        )
    
    def _recommend_distinct(self,
                           rel: SkillRelationship,
                           skill_a: pd.Series,
                           skill_b: pd.Series) -> Recommendation:
        """Decision tree for DISTINCT."""
        return Recommendation(
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            action=ActionType.NO_ACTION,
            priority="P3",
            priority_score=0.1,
            rationale="Skills are distinct with low similarity; no action needed",
            specific_steps=["No action required"],
            impact={'negligible': True}
        )
    
    def _calculate_quality_score(self,
                                skill: pd.Series,
                                metadata_df: Optional[pd.DataFrame]) -> float:
        """
        Calculate skill quality score.
        
        Factors:
        - Metadata completeness
        - Taxonomic alignment (if available)
        - LLM confidence
        """
        # Metadata completeness
        key_fields = [
            'actions', 'targets', 'key_concepts',
            'cognitive_demand', 'task_complexity', 'skill_domain',
            'text_type', 'support_level', 'scope'
        ]
        filled = sum(1 for field in key_fields if field in skill and skill[field])
        completeness = filled / len(key_fields)
        
        # LLM confidence
        llm_confidence_map = {'high': 1.0, 'medium': 0.7, 'low': 0.3}
        llm_conf = llm_confidence_map.get(skill.get('llm_confidence', 'medium'), 0.7)
        
        # Clarity (length and specificity heuristic)
        skill_name = skill.get('SKILL_NAME', '')
        clarity = min(1.0, len(skill_name.split()) / 10)  # Optimal ~10 words
        
        # Weighted score
        quality = (
            0.4 * completeness +
            0.3 * llm_conf +
            0.3 * clarity
        )
        
        return quality
    
    def _calculate_priority_score(self,
                                  confidence: float,
                                  impact: Dict,
                                  taxonomy_importance: float,
                                  data_quality_concern: float) -> float:
        """Calculate priority score using configured weights."""
        impact_score = impact.get('impact_score', 0.5)
        
        score = (
            self.priority_weights['confidence_score'] * confidence +
            self.priority_weights['impact_score'] * impact_score +
            self.priority_weights['taxonomy_importance'] * taxonomy_importance +
            self.priority_weights['data_quality_concern'] * data_quality_concern
        )
        
        return score
    
    def _score_to_bucket(self, score: float) -> str:
        """Convert priority score to bucket (P0, P1, P2, P3)."""
        if score >= self.priority_buckets['P0']:
            return 'P0'
        elif score >= self.priority_buckets['P1']:
            return 'P1'
        elif score >= self.priority_buckets['P2']:
            return 'P2'
        else:
            return 'P3'
    
    def _estimate_impact(self,
                        skill_a: pd.Series,
                        skill_b: pd.Series,
                        metadata_df: Optional[pd.DataFrame]) -> Dict:
        """
        Estimate impact of resolving this relationship.
        
        Factors:
        - Number of states affected
        - Student reach (if data available)
        - Content tagged (if data available)
        """
        # Placeholder implementation (would need actual content/usage data)
        impact_score = 0.5  # Default medium impact
        
        # Boost for cross-state relationships
        # (In real implementation, would check state field)
        
        return {
            'impact_score': impact_score,
            'estimated_states_affected': 2,  # Placeholder
            'estimated_content_affected': 10,  # Placeholder
            'migration_effort': 'LOW'
        }
    
    def _suggest_base_skill_name(self, skill_a: pd.Series, skill_b: pd.Series) -> str:
        """
        Suggest base skill name from two similar skills.
        
        Strategy:
        - Extract common root verb
        - Extract common target
        - Remove qualifiers and specifications
        """
        # Get actions
        actions_a = set(str(skill_a.get('actions', '')).split('|'))
        actions_b = set(str(skill_b.get('actions', '')).split('|'))
        common_actions = actions_a & actions_b
        
        # Get targets
        targets_a = set(str(skill_a.get('targets', '')).split('|'))
        targets_b = set(str(skill_b.get('targets', '')).split('|'))
        common_targets = targets_a & targets_b
        
        # Construct name
        if common_actions and common_targets:
            action = list(common_actions)[0].strip().capitalize()
            target = list(common_targets)[0].strip()
            return f"{action} {target}"
        
        # Fallback: use root verb
        root_a = skill_a.get('root_verb', '')
        if root_a:
            return f"{root_a.capitalize()} Core Concept"
        
        return "Unnamed Base Skill"


if __name__ == "__main__":
    # Simple test
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from similarity_engine import SimilarityEngine
    from relationship_classifier import RelationshipClassifier
    
    print("Recommendation Engine Test")
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
        'support_level': 'with_support',
        'llm_confidence': 'high',
        'root_verb': 'determine'
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
        'support_level': 'independent',
        'llm_confidence': 'high',
        'root_verb': 'identify'
    })
    
    # Calculate similarity and classify
    engine = SimilarityEngine()
    sim_score = engine.calculate_similarity(skill_a, skill_b, semantic_similarity=0.88)
    
    classifier = RelationshipClassifier()
    relationship = classifier.classify(sim_score, skill_a, skill_b)
    
    # Generate recommendation
    rec_engine = RecommendationEngine()
    recommendation = rec_engine.generate_recommendation(relationship, skill_a, skill_b)
    
    print(f"\nRelationship: {relationship.relationship_type.value}")
    print(f"Confidence: {relationship.confidence:.3f}")
    print(f"\nRecommended Action: {recommendation.action.value}")
    print(f"Priority: {recommendation.priority} (score: {recommendation.priority_score:.3f})")
    print(f"\nRationale: {recommendation.rationale}")
    print(f"\nSpecific Steps:")
    for i, step in enumerate(recommendation.specific_steps, 1):
        print(f"  {i}. {step}")
    
    if recommendation.suggested_base_skill_name:
        print(f"\nSuggested Base Skill: {recommendation.suggested_base_skill_name}")
    
    print("\n" + "=" * 50)
    print("✓ Test complete!")

