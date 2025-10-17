"""
Multi-Dimensional Similarity Engine

Calculates similarity across four dimensions:
1. Structural (spaCy-based: actions, targets, concepts)
2. Educational (metadata: cognitive demand, complexity, domain)
3. Semantic (sentence-transformers: overall meaning)
4. Contextual (specifications: grade, scope, support)

Each dimension is explainable and contributes to a composite score.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimilarityScore:
    """Structured similarity score with full explainability."""
    skill_pair: Tuple[str, str]
    
    # Dimension scores
    structural: float
    educational: float
    semantic: float
    contextual: float
    composite: float
    
    # Dimension components
    structural_components: Dict[str, float] = field(default_factory=dict)
    educational_components: Dict[str, float] = field(default_factory=dict)
    contextual_components: Dict[str, float] = field(default_factory=dict)
    
    # Explainability
    weights: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'skill_pair': list(self.skill_pair),
            'scores': {
                'structural': float(self.structural),
                'educational': float(self.educational),
                'semantic': float(self.semantic),
                'contextual': float(self.contextual),
                'composite': float(self.composite)
            },
            'components': {
                'structural': {k: float(v) for k, v in self.structural_components.items()},
                'educational': {k: float(v) for k, v in self.educational_components.items()},
                'contextual': {k: float(v) for k, v in self.contextual_components.items()}
            },
            'weights': {k: float(v) for k, v in self.weights.items()},
            'evidence': self.evidence
        }


class SimilarityEngine:
    """
    Multi-dimensional similarity calculator for skills.
    
    Combines structural, educational, semantic, and contextual signals
    to produce explainable composite similarity scores.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize similarity engine.
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.weights = self.config['weights']
        self.structural_weights = self.config['structural_weights']
        self.educational_weights = self.config['educational_weights']
        self.contextual_weights = self.config['contextual_weights']
        self.grade_mapping = self.config['grade_mapping']
        self.cognitive_levels = self.config['cognitive_levels']
        self.complexity_levels = self.config['complexity_levels']
        
        logger.info("Similarity engine initialized")
    
    def calculate_similarity(self,
                           skill_a: pd.Series,
                           skill_b: pd.Series,
                           semantic_similarity: Optional[float] = None,
                           adaptive_mode: Optional[str] = None) -> SimilarityScore:
        """
        Calculate multi-dimensional similarity between two skills.
        
        Args:
            skill_a: First skill with metadata
            skill_b: Second skill with metadata
            semantic_similarity: Pre-computed semantic similarity (optional)
            adaptive_mode: Use adaptive weights for specific use case
            
        Returns:
            SimilarityScore with all dimensions and explanations
        """
        # Calculate each dimension
        structural, struct_comp = self._calculate_structural_similarity(skill_a, skill_b)
        educational, edu_comp = self._calculate_educational_similarity(skill_a, skill_b)
        contextual, ctx_comp = self._calculate_contextual_similarity(skill_a, skill_b)
        
        # Use provided semantic similarity or calculate placeholder
        semantic = semantic_similarity if semantic_similarity is not None else 0.0
        
        # Get weights (adaptive or default)
        if adaptive_mode and adaptive_mode in self.config['adaptive_weights']:
            weights = self.config['adaptive_weights'][adaptive_mode]
        else:
            weights = self.weights
        
        # Calculate composite score
        composite = (
            weights['structural'] * structural +
            weights['educational'] * educational +
            weights['semantic'] * semantic +
            weights['contextual'] * contextual
        )
        
        # Apply boost factors if applicable
        boost_factors = self._calculate_boost_factors(skill_a, skill_b, 
                                                       structural, semantic, contextual)
        if boost_factors:
            composite = min(1.0, composite * (1.0 + sum(boost_factors.values())))
        
        # Generate evidence
        evidence = self._generate_evidence(
            skill_a, skill_b,
            struct_comp, edu_comp, ctx_comp,
            structural, educational, semantic, contextual
        )
        
        return SimilarityScore(
            skill_pair=(skill_a['SKILL_ID'], skill_b['SKILL_ID']),
            structural=structural,
            educational=educational,
            semantic=semantic,
            contextual=contextual,
            composite=composite,
            structural_components=struct_comp,
            educational_components=edu_comp,
            contextual_components=ctx_comp,
            weights=weights,
            evidence=evidence
        )
    
    def _calculate_structural_similarity(self,
                                        skill_a: pd.Series,
                                        skill_b: pd.Series) -> Tuple[float, Dict]:
        """
        Calculate structural similarity using spaCy-extracted features.
        
        Components:
        - Action match: Jaccard on action verbs
        - Target overlap: Jaccard on targets/objects
        - Concept similarity: Jaccard on key concepts
        """
        components = {}
        
        # Actions
        actions_a = self._parse_list_field(skill_a.get('actions', ''))
        actions_b = self._parse_list_field(skill_b.get('actions', ''))
        components['action_match'] = self._jaccard_similarity(actions_a, actions_b)
        
        # Targets
        targets_a = self._parse_list_field(skill_a.get('targets', ''))
        targets_b = self._parse_list_field(skill_b.get('targets', ''))
        components['target_overlap'] = self._jaccard_similarity(targets_a, targets_b)
        
        # Key concepts
        concepts_a = self._parse_list_field(skill_a.get('key_concepts', ''))
        concepts_b = self._parse_list_field(skill_b.get('key_concepts', ''))
        components['concept_similarity'] = self._jaccard_similarity(concepts_a, concepts_b)
        
        # Weighted average
        score = (
            self.structural_weights['action_match'] * components['action_match'] +
            self.structural_weights['target_overlap'] * components['target_overlap'] +
            self.structural_weights['concept_similarity'] * components['concept_similarity']
        )
        
        return score, components
    
    def _calculate_educational_similarity(self,
                                         skill_a: pd.Series,
                                         skill_b: pd.Series) -> Tuple[float, Dict]:
        """
        Calculate educational similarity using metadata.
        
        Components:
        - Cognitive demand match
        - Task complexity match (ordinal)
        - Skill domain match
        - Text type overlap
        """
        components = {}
        
        # Cognitive demand (binary match)
        cog_a = skill_a.get('cognitive_demand', '')
        cog_b = skill_b.get('cognitive_demand', '')
        components['cognitive_demand_match'] = 1.0 if cog_a == cog_b else 0.0
        
        # Task complexity (ordinal distance)
        task_a = skill_a.get('task_complexity', '')
        task_b = skill_b.get('task_complexity', '')
        components['task_complexity_match'] = self._ordinal_similarity(
            task_a, task_b, self.complexity_levels
        )
        
        # Skill domain (binary match)
        domain_a = skill_a.get('skill_domain', '')
        domain_b = skill_b.get('skill_domain', '')
        components['skill_domain_match'] = 1.0 if domain_a == domain_b else 0.0
        
        # Text type (Jaccard on list)
        text_type_a = self._parse_list_field(skill_a.get('text_type', ''))
        text_type_b = self._parse_list_field(skill_b.get('text_type', ''))
        components['text_type_match'] = self._jaccard_similarity(text_type_a, text_type_b)
        
        # Weighted average
        score = (
            self.educational_weights['cognitive_demand'] * components['cognitive_demand_match'] +
            self.educational_weights['task_complexity'] * components['task_complexity_match'] +
            self.educational_weights['skill_domain'] * components['skill_domain_match'] +
            self.educational_weights['text_type'] * components['text_type_match']
        )
        
        return score, components
    
    def _calculate_contextual_similarity(self,
                                        skill_a: pd.Series,
                                        skill_b: pd.Series) -> Tuple[float, Dict]:
        """
        Calculate contextual similarity (specifications).
        
        Components:
        - Grade compatibility (distance-based)
        - Scope match
        - Support level compatibility
        """
        components = {}
        
        # Grade compatibility
        grade_a = skill_a.get('GRADE_LEVEL_SHORT_NAME', '') or skill_a.get('GRADE_LEVEL_NAME', '')
        grade_b = skill_b.get('GRADE_LEVEL_SHORT_NAME', '') or skill_b.get('GRADE_LEVEL_NAME', '')
        components['grade_compatibility'] = self._grade_compatibility(grade_a, grade_b)
        
        # Scope match (binary)
        scope_a = skill_a.get('scope', '')
        scope_b = skill_b.get('scope', '')
        components['scope_match'] = 1.0 if scope_a == scope_b else 0.0
        
        # Support level compatibility
        support_a = skill_a.get('support_level', '')
        support_b = skill_b.get('support_level', '')
        components['support_compatibility'] = self._support_compatibility(support_a, support_b)
        
        # Weighted average
        score = (
            self.contextual_weights['grade_compatibility'] * components['grade_compatibility'] +
            self.contextual_weights['scope_match'] * components['scope_match'] +
            self.contextual_weights['support_compatibility'] * components['support_compatibility']
        )
        
        return score, components
    
    def _jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _ordinal_similarity(self, val_a: str, val_b: str, ordered_list: List[str]) -> float:
        """Calculate similarity for ordinal variables."""
        try:
            idx_a = ordered_list.index(val_a)
            idx_b = ordered_list.index(val_b)
            distance = abs(idx_a - idx_b)
            max_distance = len(ordered_list) - 1
            return 1.0 - (distance / max_distance) if max_distance > 0 else 1.0
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _grade_compatibility(self, grade_a: str, grade_b: str) -> float:
        """Calculate grade compatibility (1.0 = same, 0.5 = adjacent, 0.0 = distant)."""
        try:
            num_a = self.grade_mapping.get(grade_a, -999)
            num_b = self.grade_mapping.get(grade_b, -999)
            
            if num_a == -999 or num_b == -999:
                return 0.0
            
            distance = abs(num_a - num_b)
            
            if distance == 0:
                return 1.0
            elif distance == 1:
                return 0.5
            else:
                # Decay: 0.5 - (distance - 1) * 0.1, min 0.0
                return max(0.0, 0.5 - (distance - 1) * 0.1)
        except:
            return 0.0
    
    def _support_compatibility(self, support_a: str, support_b: str) -> float:
        """Calculate support level compatibility."""
        if not support_a or not support_b:
            return 0.5  # Unknown
        
        if support_a == support_b:
            return 1.0
        
        # Compatible pairs (different terminology, same meaning)
        compatible_pairs = [
            {'with_support', 'with_prompting', 'with_scaffolding'},
            {'independent', 'independently', 'without_support'}
        ]
        
        for pair_set in compatible_pairs:
            if support_a in pair_set and support_b in pair_set:
                return 0.7  # Compatible but different
        
        return 0.0  # Incompatible
    
    def _parse_list_field(self, field_value) -> Set[str]:
        """Parse pipe-separated or comma-separated field into set."""
        if pd.isna(field_value) or not field_value:
            return set()
        
        # Convert to string and clean
        field_str = str(field_value).strip()
        
        # Try pipe separator first, then comma
        if '|' in field_str:
            items = field_str.split('|')
        elif ',' in field_str:
            items = field_str.split(',')
        else:
            items = [field_str]
        
        # Clean and return
        return {item.strip().lower() for item in items if item.strip()}
    
    def _calculate_boost_factors(self,
                                 skill_a: pd.Series,
                                 skill_b: pd.Series,
                                 structural: float,
                                 semantic: float,
                                 contextual: float) -> Dict[str, float]:
        """Calculate boost factors for special conditions."""
        boosts = {}
        
        # Exact structural match
        if structural >= 0.95:
            boosts['exact_structural_match'] = 0.05
        
        # Same grade + high similarity
        grade_a = skill_a.get('GRADE_LEVEL_SHORT_NAME', '')
        grade_b = skill_b.get('GRADE_LEVEL_SHORT_NAME', '')
        if grade_a == grade_b and semantic >= 0.85:
            boosts['same_grade_high_sim'] = 0.03
        
        # Cross-state variant (different states, high similarity)
        # Note: Would need state field in metadata
        
        return boosts
    
    def _generate_evidence(self,
                          skill_a: pd.Series,
                          skill_b: pd.Series,
                          struct_comp: Dict,
                          edu_comp: Dict,
                          ctx_comp: Dict,
                          structural: float,
                          educational: float,
                          semantic: float,
                          contextual: float) -> List[str]:
        """Generate human-readable evidence for similarity."""
        evidence = []
        
        # Structural evidence
        if struct_comp.get('action_match', 0) >= 0.8:
            actions_a = self._parse_list_field(skill_a.get('actions', ''))
            actions_b = self._parse_list_field(skill_b.get('actions', ''))
            common = actions_a & actions_b
            if common:
                evidence.append(f"✓ Matching actions: {', '.join(list(common)[:3])}")
        
        if struct_comp.get('target_overlap', 0) >= 0.8:
            targets_a = self._parse_list_field(skill_a.get('targets', ''))
            targets_b = self._parse_list_field(skill_b.get('targets', ''))
            common = targets_a & targets_b
            if common:
                evidence.append(f"✓ Matching targets: {', '.join(list(common)[:3])}")
        
        # Educational evidence
        if edu_comp.get('cognitive_demand_match', 0) == 1.0:
            cog = skill_a.get('cognitive_demand', '')
            if cog:
                evidence.append(f"✓ Same cognitive demand: '{cog}'")
        
        if edu_comp.get('skill_domain_match', 0) == 1.0:
            domain = skill_a.get('skill_domain', '')
            if domain:
                evidence.append(f"✓ Same skill domain: '{domain}'")
        
        # Contextual differences
        if ctx_comp.get('grade_compatibility', 0) < 1.0:
            grade_a = skill_a.get('GRADE_LEVEL_SHORT_NAME', 'Unknown')
            grade_b = skill_b.get('GRADE_LEVEL_SHORT_NAME', 'Unknown')
            evidence.append(f"⚠ Different grades: {grade_a} vs {grade_b}")
        
        if ctx_comp.get('support_compatibility', 0) < 1.0:
            support_a = skill_a.get('support_level', 'Unknown')
            support_b = skill_b.get('support_level', 'Unknown')
            if support_a != 'Unknown' and support_b != 'Unknown':
                evidence.append(f"⚠ Different support: {support_a} vs {support_b}")
        
        # Overall assessment
        if structural >= 0.90 and educational >= 0.90:
            evidence.append("🔥 Very high structural and educational similarity")
        elif semantic >= 0.85:
            evidence.append("✓ High semantic similarity")
        
        return evidence
    
    def batch_calculate_similarities(self,
                                     skill_pairs: List[Tuple[pd.Series, pd.Series]],
                                     semantic_similarities: Optional[np.ndarray] = None) -> List[SimilarityScore]:
        """
        Calculate similarities for a batch of skill pairs.
        
        Args:
            skill_pairs: List of (skill_a, skill_b) tuples
            semantic_similarities: Optional pre-computed semantic similarities
            
        Returns:
            List of SimilarityScore objects
        """
        results = []
        
        for i, (skill_a, skill_b) in enumerate(skill_pairs):
            semantic_sim = semantic_similarities[i] if semantic_similarities is not None else None
            score = self.calculate_similarity(skill_a, skill_b, semantic_sim)
            results.append(score)
        
        logger.info(f"Calculated similarities for {len(results)} pairs")
        return results


def load_semantic_embeddings(embeddings_path: Path) -> np.ndarray:
    """Load pre-computed semantic embeddings from file."""
    if embeddings_path.suffix == '.npy':
        return np.load(embeddings_path)
    else:
        raise ValueError(f"Unsupported embedding format: {embeddings_path.suffix}")


def calculate_semantic_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Calculate pairwise cosine similarity matrix from embeddings.
    
    Args:
        embeddings: numpy array of shape (n_skills, embedding_dim)
        
    Returns:
        Similarity matrix of shape (n_skills, n_skills)
    """
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity(embeddings)


if __name__ == "__main__":
    # Simple test
    print("Similarity Engine Test")
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
    score = engine.calculate_similarity(skill_a, skill_b, semantic_similarity=0.88)
    
    print(f"\nSkill A: {skill_a['SKILL_NAME']}")
    print(f"Skill B: {skill_b['SKILL_NAME']}")
    print(f"\nSimilarity Scores:")
    print(f"  Structural:  {score.structural:.3f}")
    print(f"  Educational: {score.educational:.3f}")
    print(f"  Semantic:    {score.semantic:.3f}")
    print(f"  Contextual:  {score.contextual:.3f}")
    print(f"  Composite:   {score.composite:.3f}")
    
    print(f"\nEvidence:")
    for item in score.evidence:
        print(f"  {item}")
    
    print("\n" + "=" * 50)
    print("✓ Test complete!")

