"""
Redundancy Analyzer

Main orchestrator for the skill redundancy detection system.
Processes skills through the complete pipeline:
1. Pre-filtering
2. Multi-dimensional similarity calculation
3. Relationship classification
4. Recommendation generation
5. Prioritization and export
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import logging
from tqdm import tqdm


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

try:
    from .similarity_engine import SimilarityEngine, SimilarityScore
    from .relationship_classifier import RelationshipClassifier, SkillRelationship
    from .recommendation_engine import RecommendationEngine, Recommendation
except ImportError:
    from similarity_engine import SimilarityEngine, SimilarityScore
    from relationship_classifier import RelationshipClassifier, SkillRelationship
    from recommendation_engine import RecommendationEngine, Recommendation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RedundancyAnalyzer:
    """
    Main analyzer for detecting and managing skill redundancies.
    
    Orchestrates the complete pipeline from metadata to recommendations.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize redundancy analyzer.
        
        Args:
            config_path: Path to config.yaml file
        """
        self.similarity_engine = SimilarityEngine(config_path)
        self.classifier = RelationshipClassifier(config_path)
        self.recommender = RecommendationEngine(config_path)
        
        # Load config for filtering
        import yaml
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("Redundancy analyzer initialized")
    
    def analyze_skills(self,
                      metadata_df: pd.DataFrame,
                      semantic_embeddings: Optional[np.ndarray] = None,
                      output_dir: Optional[Path] = None,
                      max_pairs: Optional[int] = None) -> Tuple[List[SkillRelationship], List[Recommendation]]:
        """
        Analyze skills for redundancies and relationships.
        
        Args:
            metadata_df: DataFrame with enhanced metadata (23 fields)
            semantic_embeddings: Optional pre-computed embeddings
            output_dir: Directory to save results
            max_pairs: Maximum pairs to process (for testing)
            
        Returns:
            Tuple of (relationships, recommendations)
        """
        logger.info(f"Starting analysis of {len(metadata_df)} skills")
        
        # Step 1: Pre-filter pairs
        logger.info("Step 1: Pre-filtering skill pairs...")
        candidate_pairs = self._prefilter_pairs(metadata_df, max_pairs=max_pairs)
        logger.info(f"  Found {len(candidate_pairs)} candidate pairs")
        
        # Step 2: Calculate semantic similarities if not provided
        if semantic_embeddings is not None:
            logger.info("Step 2: Using provided semantic embeddings")
            semantic_sim_matrix = self._calculate_semantic_matrix(semantic_embeddings)
        else:
            logger.info("Step 2: Skipping semantic similarity (not provided)")
            semantic_sim_matrix = None
        
        # Step 3: Calculate multi-dimensional similarities
        logger.info("Step 3: Calculating multi-dimensional similarities...")
        similarity_scores = []
        for idx_a, idx_b in tqdm(candidate_pairs, desc="Calculating similarities"):
            skill_a = metadata_df.iloc[idx_a]
            skill_b = metadata_df.iloc[idx_b]
            
            # Get semantic similarity if available
            semantic_sim = None
            if semantic_sim_matrix is not None:
                semantic_sim = semantic_sim_matrix[idx_a, idx_b]
            
            sim_score = self.similarity_engine.calculate_similarity(
                skill_a, skill_b, semantic_similarity=semantic_sim
            )
            similarity_scores.append((idx_a, idx_b, sim_score))
        
        logger.info(f"  Calculated {len(similarity_scores)} similarity scores")
        
        # Step 4: Classify relationships
        logger.info("Step 4: Classifying relationships...")
        relationships = []
        for idx_a, idx_b, sim_score in tqdm(similarity_scores, desc="Classifying"):
            skill_a = metadata_df.iloc[idx_a]
            skill_b = metadata_df.iloc[idx_b]
            
            relationship = self.classifier.classify(sim_score, skill_a, skill_b)
            relationships.append(relationship)
        
        # Filter out DISTINCT relationships (too many, low value)
        from .relationship_classifier import RelationshipType
        filtered_relationships = [
            r for r in relationships 
            if r.relationship_type != RelationshipType.DISTINCT
        ]
        logger.info(f"  Classified {len(filtered_relationships)} non-DISTINCT relationships")
        
        # Step 5: Generate recommendations
        logger.info("Step 5: Generating recommendations...")
        recommendations = []
        for relationship in tqdm(filtered_relationships, desc="Generating recommendations"):
            skill_a = metadata_df[metadata_df['SKILL_ID'] == relationship.skill_a_id].iloc[0]
            skill_b = metadata_df[metadata_df['SKILL_ID'] == relationship.skill_b_id].iloc[0]
            
            recommendation = self.recommender.generate_recommendation(
                relationship, skill_a, skill_b, metadata_df
            )
            recommendations.append(recommendation)
        
        logger.info(f"  Generated {len(recommendations)} recommendations")
        
        # Step 6: Sort by priority
        recommendations.sort(key=lambda r: r.priority_score, reverse=True)
        
        # Step 7: Save results if output directory specified
        if output_dir:
            self._save_results(relationships, recommendations, output_dir)
        
        logger.info("Analysis complete!")
        return relationships, recommendations
    
    def _prefilter_pairs(self,
                        metadata_df: pd.DataFrame,
                        max_pairs: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Pre-filter skill pairs using fast structural similarity.
        
        Only returns pairs with structural similarity above threshold.
        This drastically reduces the number of pairs to analyze.
        """
        threshold = self.config['prefilter']['structural_threshold']
        max_per_skill = self.config['prefilter']['max_pairs_per_skill']
        
        candidate_pairs = []
        
        for i in range(len(metadata_df)):
            skill_i = metadata_df.iloc[i]
            
            # Get actions and targets for quick comparison
            actions_i = self._parse_field(skill_i.get('actions', ''))
            targets_i = self._parse_field(skill_i.get('targets', ''))
            
            if not actions_i or not targets_i:
                continue  # Skip skills without structural data
            
            candidates_for_i = []
            
            for j in range(i + 1, len(metadata_df)):
                skill_j = metadata_df.iloc[j]
                
                actions_j = self._parse_field(skill_j.get('actions', ''))
                targets_j = self._parse_field(skill_j.get('targets', ''))
                
                if not actions_j or not targets_j:
                    continue
                
                # Quick Jaccard on actions
                action_sim = self._jaccard(actions_i, actions_j)
                
                # Quick Jaccard on targets
                target_sim = self._jaccard(targets_i, targets_j)
                
                # Quick structural score
                quick_struct = (action_sim + target_sim) / 2
                
                if quick_struct >= threshold:
                    candidates_for_i.append((j, quick_struct))
            
            # Keep top N candidates for this skill
            candidates_for_i.sort(key=lambda x: x[1], reverse=True)
            for j, _ in candidates_for_i[:max_per_skill]:
                candidate_pairs.append((i, j))
            
            # Stop if we've hit max pairs limit
            if max_pairs and len(candidate_pairs) >= max_pairs:
                break
        
        # Remove duplicates
        candidate_pairs = list(set(candidate_pairs))
        
        # Limit to max_pairs if specified
        if max_pairs:
            candidate_pairs = candidate_pairs[:max_pairs]
        
        return candidate_pairs
    
    def _parse_field(self, field_value) -> set:
        """Parse pipe or comma-separated field."""
        if pd.isna(field_value) or not field_value:
            return set()
        
        field_str = str(field_value).strip()
        
        if '|' in field_str:
            items = field_str.split('|')
        elif ',' in field_str:
            items = field_str.split(',')
        else:
            items = [field_str]
        
        return {item.strip().lower() for item in items if item.strip()}
    
    def _jaccard(self, set_a: set, set_b: set) -> float:
        """Calculate Jaccard similarity."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0
    
    def _calculate_semantic_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate semantic similarity matrix from embeddings."""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity(embeddings)
    
    def _save_results(self,
                     relationships: List[SkillRelationship],
                     recommendations: List[Recommendation],
                     output_dir: Path):
        """Save results to JSON and CSV files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save relationships
        relationships_data = [r.to_dict() for r in relationships]
        rel_path = output_dir / f"relationships_{timestamp}.json"
        with open(rel_path, 'w') as f:
            json.dump(relationships_data, f, indent=2, cls=NumpyEncoder)
        logger.info(f"  Saved relationships to {rel_path}")
        
        # Save recommendations
        recommendations_data = [r.to_dict() for r in recommendations]
        rec_path = output_dir / f"recommendations_{timestamp}.json"
        with open(rec_path, 'w') as f:
            json.dump(recommendations_data, f, indent=2, cls=NumpyEncoder)
        logger.info(f"  Saved recommendations to {rec_path}")
        
        # Save CSV summary
        summary_data = []
        for rel, rec in zip(relationships, recommendations):
            summary_data.append({
                'relationship_id': rel.relationship_id,
                'skill_a_id': rel.skill_a_id,
                'skill_b_id': rel.skill_b_id,
                'skill_a_name': rel.skill_a_name,
                'skill_b_name': rel.skill_b_name,
                'relationship_type': rel.relationship_type.value,
                'confidence': rel.confidence,
                'composite_score': rel.similarity_scores['composite'],
                'recommended_action': rec.action.value,
                'priority': rec.priority,
                'priority_score': rec.priority_score,
                'rationale': rec.rationale
            })
        
        summary_df = pd.DataFrame(summary_data)
        csv_path = output_dir / f"summary_{timestamp}.csv"
        summary_df.to_csv(csv_path, index=False)
        logger.info(f"  Saved summary to {csv_path}")
        
        # Save statistics
        stats = self._generate_statistics(relationships, recommendations)
        stats_path = output_dir / f"statistics_{timestamp}.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2, cls=NumpyEncoder)
        logger.info(f"  Saved statistics to {stats_path}")
    
    def _generate_statistics(self,
                            relationships: List[SkillRelationship],
                            recommendations: List[Recommendation]) -> Dict:
        """Generate summary statistics."""
        from collections import Counter
        
        rel_types = Counter(r.relationship_type.value for r in relationships)
        actions = Counter(r.action.value for r in recommendations)
        priorities = Counter(r.priority for r in recommendations)
        
        avg_confidence = np.mean([r.confidence for r in relationships])
        avg_composite = np.mean([r.similarity_scores['composite'] for r in relationships])
        
        return {
            'total_relationships': len(relationships),
            'total_recommendations': len(recommendations),
            'relationship_types': dict(rel_types),
            'recommended_actions': dict(actions),
            'priority_distribution': dict(priorities),
            'average_confidence': float(avg_confidence),
            'average_composite_score': float(avg_composite),
            'high_priority_count': len([r for r in recommendations if r.priority in ['P0', 'P1']])
        }


def load_enhanced_metadata(metadata_path: Path) -> pd.DataFrame:
    """Load enhanced metadata CSV."""
    logger.info(f"Loading metadata from {metadata_path}")
    df = pd.read_csv(metadata_path)
    logger.info(f"  Loaded {len(df)} skills")
    
    # Validate required fields
    required_fields = ['SKILL_ID', 'SKILL_NAME', 'actions', 'targets']
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    
    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze skills for redundancies')
    parser.add_argument('--metadata', type=str, required=True,
                       help='Path to enhanced metadata CSV')
    parser.add_argument('--output', type=str, default='outputs/relationships',
                       help='Output directory for results')
    parser.add_argument('--max-pairs', type=int, default=None,
                       help='Maximum pairs to process (for testing)')
    parser.add_argument('--embeddings', type=str, default=None,
                       help='Path to semantic embeddings (.npy file)')
    
    args = parser.parse_args()
    
    # Load metadata
    metadata_df = load_enhanced_metadata(Path(args.metadata))
    
    # Load embeddings if provided
    embeddings = None
    if args.embeddings:
        embeddings = np.load(args.embeddings)
        logger.info(f"Loaded embeddings: shape {embeddings.shape}")
    
    # Run analysis
    analyzer = RedundancyAnalyzer()
    relationships, recommendations = analyzer.analyze_skills(
        metadata_df,
        semantic_embeddings=embeddings,
        output_dir=Path(args.output),
        max_pairs=args.max_pairs
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total relationships found: {len(relationships)}")
    print(f"Total recommendations: {len(recommendations)}")
    
    from collections import Counter
    rel_types = Counter(r.relationship_type.value for r in relationships)
    print(f"\nRelationship types:")
    for rtype, count in rel_types.most_common():
        print(f"  {rtype}: {count}")
    
    priorities = Counter(r.priority for r in recommendations)
    print(f"\nPriority distribution:")
    for priority in ['P0', 'P1', 'P2', 'P3']:
        print(f"  {priority}: {priorities.get(priority, 0)}")
    
    print(f"\nResults saved to: {args.output}")
    print("=" * 70)

