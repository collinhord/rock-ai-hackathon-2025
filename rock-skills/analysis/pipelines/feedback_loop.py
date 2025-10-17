#!/usr/bin/env python3
"""
Feedback Loop System

Logs human curation decisions and uses them to improve future extractions
through threshold calibration and parameter tuning.

Usage:
    from feedback_loop import FeedbackLogger, ThresholdCalibrator
    
    # Log decisions
    logger = FeedbackLogger()
    logger.log_decision('merge', base_skill_a, base_skill_b, 'semantic_similarity', curator='user123')
    
    # Calibrate thresholds
    calibrator = ThresholdCalibrator()
    new_thresholds = calibrator.calibrate_from_decisions(logger.get_decisions())
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict


class FeedbackLogger:
    """Log and manage human curation decisions."""
    
    def __init__(self, log_dir: str = '../../taxonomy/decisions'):
        """
        Initialize feedback logger.
        
        Args:
            log_dir: Directory to store decision logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_file = self.log_dir / 'curation_decisions.jsonl'
    
    def log_decision(self, action: str, entity_a: Dict, entity_b: Optional[Dict] = None,
                    reason: str = '', curator: str = 'unknown', metadata: Dict = None):
        """
        Log a curation decision.
        
        Args:
            action: Type of decision (merge, split, approve, reject, clarify, create_spec)
            entity_a: First entity (base skill, ROCK skill, conflict)
            entity_b: Second entity (for merge operations)
            reason: Reason for decision
            curator: Name/ID of curator making decision
            metadata: Additional metadata about decision
        """
        decision = {
            'decision_id': f"DEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{np.random.randint(1000, 9999)}",
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'action': action,
            'curator': curator,
            'reason': reason,
            'entity_a': {
                'id': entity_a.get('base_skill_id') or entity_a.get('SKILL_ID') or entity_a.get('conflict_id'),
                'name': entity_a.get('base_skill_name') or entity_a.get('SKILL_NAME'),
                'type': self._infer_entity_type(entity_a)
            },
            'entity_b': None if entity_b is None else {
                'id': entity_b.get('base_skill_id') or entity_b.get('SKILL_ID') or entity_b.get('conflict_id'),
                'name': entity_b.get('base_skill_name') or entity_b.get('SKILL_NAME'),
                'type': self._infer_entity_type(entity_b)
            },
            'metadata': metadata or {}
        }
        
        # Append to JSONL file
        with open(self.decisions_file, 'a') as f:
            f.write(json.dumps(decision) + '\n')
        
        return decision['decision_id']
    
    def get_decisions(self, action: Optional[str] = None, 
                     curator: Optional[str] = None,
                     since: Optional[str] = None) -> List[Dict]:
        """
        Retrieve logged decisions with optional filtering.
        
        Args:
            action: Filter by action type
            curator: Filter by curator
            since: Filter by timestamp (ISO format)
            
        Returns:
            List of decision dictionaries
        """
        if not self.decisions_file.exists():
            return []
        
        decisions = []
        with open(self.decisions_file, 'r') as f:
            for line in f:
                if line.strip():
                    decision = json.loads(line)
                    
                    # Apply filters
                    if action and decision['action'] != action:
                        continue
                    if curator and decision['curator'] != curator:
                        continue
                    if since and decision['timestamp'] < since:
                        continue
                    
                    decisions.append(decision)
        
        return decisions
    
    def get_decision_summary(self) -> Dict:
        """Generate summary statistics of decisions."""
        decisions = self.get_decisions()
        
        if not decisions:
            return {
                'total_decisions': 0,
                'by_action': {},
                'by_curator': {},
                'first_decision': None,
                'last_decision': None
            }
        
        summary = {
            'total_decisions': len(decisions),
            'by_action': defaultdict(int),
            'by_curator': defaultdict(int),
            'first_decision': decisions[0]['timestamp'],
            'last_decision': decisions[-1]['timestamp']
        }
        
        for decision in decisions:
            summary['by_action'][decision['action']] += 1
            summary['by_curator'][decision['curator']] += 1
        
        summary['by_action'] = dict(summary['by_action'])
        summary['by_curator'] = dict(summary['by_curator'])
        
        return summary
    
    def _infer_entity_type(self, entity: Dict) -> str:
        """Infer entity type from keys."""
        if 'base_skill_id' in entity or 'base_skill_name' in entity:
            return 'base_skill'
        elif 'SKILL_ID' in entity or 'SKILL_NAME' in entity:
            return 'rock_skill'
        elif 'conflict_id' in entity:
            return 'conflict'
        else:
            return 'unknown'


class ThresholdCalibrator:
    """Calibrate clustering and similarity thresholds from human decisions."""
    
    def __init__(self):
        """Initialize threshold calibrator."""
        self.default_thresholds = {
            'clustering_threshold': 0.75,
            'merge_threshold': 0.85,
            'split_coherence_threshold': 0.50,
            'spec_variant_threshold': 0.75,
            'overlap_threshold': 0.70
        }
    
    def calibrate_from_decisions(self, decisions: List[Dict]) -> Dict:
        """
        Calibrate thresholds based on human decisions.
        
        Args:
            decisions: List of logged decisions
            
        Returns:
            Dictionary of calibrated thresholds with confidence scores
        """
        print("\n=== THRESHOLD CALIBRATION ===\n")
        
        if not decisions:
            print("⚠ No decisions available for calibration, using defaults")
            return {
                'thresholds': self.default_thresholds,
                'confidence': 'none',
                'decisions_used': 0
            }
        
        calibration_results = {
            'thresholds': self.default_thresholds.copy(),
            'confidence': 'low',
            'decisions_used': len(decisions),
            'adjustments': []
        }
        
        # Analyze merge decisions
        merge_decisions = [d for d in decisions if d['action'] == 'merge']
        if len(merge_decisions) >= 5:
            merge_adjustment = self._calibrate_merge_threshold(merge_decisions)
            if merge_adjustment:
                calibration_results['thresholds']['merge_threshold'] = merge_adjustment['new_threshold']
                calibration_results['adjustments'].append(merge_adjustment)
                print(f"✓ Calibrated merge threshold: {merge_adjustment['new_threshold']:.3f} "
                      f"(was {self.default_thresholds['merge_threshold']:.3f})")
        
        # Analyze split decisions
        split_decisions = [d for d in decisions if d['action'] == 'split']
        if len(split_decisions) >= 5:
            split_adjustment = self._calibrate_split_threshold(split_decisions)
            if split_adjustment:
                calibration_results['thresholds']['split_coherence_threshold'] = split_adjustment['new_threshold']
                calibration_results['adjustments'].append(split_adjustment)
                print(f"✓ Calibrated split threshold: {split_adjustment['new_threshold']:.3f} "
                      f"(was {self.default_thresholds['split_coherence_threshold']:.3f})")
        
        # Analyze approve/reject on overlaps
        overlap_decisions = [d for d in decisions if d['action'] in ['approve', 'reject'] 
                           and d.get('metadata', {}).get('overlap_score')]
        if len(overlap_decisions) >= 5:
            overlap_adjustment = self._calibrate_overlap_threshold(overlap_decisions)
            if overlap_adjustment:
                calibration_results['thresholds']['overlap_threshold'] = overlap_adjustment['new_threshold']
                calibration_results['adjustments'].append(overlap_adjustment)
                print(f"✓ Calibrated overlap threshold: {overlap_adjustment['new_threshold']:.3f} "
                      f"(was {self.default_thresholds['overlap_threshold']:.3f})")
        
        # Determine overall confidence
        if len(calibration_results['adjustments']) >= 3:
            calibration_results['confidence'] = 'high'
        elif len(calibration_results['adjustments']) >= 1:
            calibration_results['confidence'] = 'medium'
        
        print(f"\n✓ Calibration complete: {len(calibration_results['adjustments'])} adjustments made")
        print(f"  Confidence: {calibration_results['confidence']}")
        
        return calibration_results
    
    def _calibrate_merge_threshold(self, merge_decisions: List[Dict]) -> Optional[Dict]:
        """Calibrate merge threshold from merge decisions."""
        # Extract similarity scores from metadata
        similarity_scores = []
        for decision in merge_decisions:
            score = decision.get('metadata', {}).get('similarity_score')
            if score is not None:
                similarity_scores.append(score)
        
        if len(similarity_scores) < 5:
            return None
        
        # Calculate optimal threshold (25th percentile of approved merges)
        new_threshold = np.percentile(similarity_scores, 25)
        
        # Clamp to reasonable range
        new_threshold = max(0.70, min(0.90, new_threshold))
        
        return {
            'threshold_type': 'merge_threshold',
            'old_threshold': self.default_thresholds['merge_threshold'],
            'new_threshold': float(new_threshold),
            'based_on': len(similarity_scores),
            'reasoning': f"25th percentile of {len(similarity_scores)} approved merges"
        }
    
    def _calibrate_split_threshold(self, split_decisions: List[Dict]) -> Optional[Dict]:
        """Calibrate split threshold from split decisions."""
        # Extract coherence scores from metadata
        coherence_scores = []
        for decision in split_decisions:
            score = decision.get('metadata', {}).get('coherence_score')
            if score is not None:
                coherence_scores.append(score)
        
        if len(coherence_scores) < 5:
            return None
        
        # Calculate optimal threshold (75th percentile of split decisions)
        new_threshold = np.percentile(coherence_scores, 75)
        
        # Clamp to reasonable range
        new_threshold = max(0.30, min(0.70, new_threshold))
        
        return {
            'threshold_type': 'split_coherence_threshold',
            'old_threshold': self.default_thresholds['split_coherence_threshold'],
            'new_threshold': float(new_threshold),
            'based_on': len(coherence_scores),
            'reasoning': f"75th percentile of {len(coherence_scores)} approved splits"
        }
    
    def _calibrate_overlap_threshold(self, overlap_decisions: List[Dict]) -> Optional[Dict]:
        """Calibrate overlap threshold from approve/reject decisions."""
        # Separate approved and rejected overlaps
        approved_scores = []
        rejected_scores = []
        
        for decision in overlap_decisions:
            score = decision.get('metadata', {}).get('overlap_score')
            if score is not None:
                if decision['action'] == 'approve':
                    approved_scores.append(score)
                else:
                    rejected_scores.append(score)
        
        if len(approved_scores) < 3 or len(rejected_scores) < 3:
            return None
        
        # Find optimal threshold (midpoint between median approved and median rejected)
        median_approved = np.median(approved_scores)
        median_rejected = np.median(rejected_scores)
        new_threshold = (median_approved + median_rejected) / 2
        
        # Clamp to reasonable range
        new_threshold = max(0.60, min(0.85, new_threshold))
        
        return {
            'threshold_type': 'overlap_threshold',
            'old_threshold': self.default_thresholds['overlap_threshold'],
            'new_threshold': float(new_threshold),
            'based_on': len(approved_scores) + len(rejected_scores),
            'reasoning': f"Midpoint between approved ({median_approved:.3f}) and rejected ({median_rejected:.3f})"
        }
    
    def save_calibrated_thresholds(self, calibration_results: Dict, 
                                   output_file: str = '../../taxonomy/calibrated_thresholds.json'):
        """Save calibrated thresholds to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(calibration_results, f, indent=2)
        
        print(f"✓ Saved calibrated thresholds to {output_path}")


class ImprovementTracker:
    """Track system improvements over time."""
    
    def __init__(self, metrics_dir: str = '../../taxonomy/metrics'):
        """Initialize improvement tracker."""
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.metrics_dir / 'improvement_metrics.jsonl'
    
    def log_metrics(self, mece_score: float, quality_score: float, 
                   base_skill_count: int, metadata: Dict = None):
        """
        Log system metrics for tracking improvement.
        
        Args:
            mece_score: MECE validation score
            quality_score: Average quality score
            base_skill_count: Number of base skills
            metadata: Additional metadata
        """
        metric_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'mece_score': float(mece_score),
            'quality_score': float(quality_score),
            'base_skill_count': int(base_skill_count),
            'metadata': metadata or {}
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric_entry) + '\n')
    
    def get_improvement_trend(self, metric: str = 'mece_score', 
                             window: int = 10) -> Dict:
        """
        Get improvement trend for a metric.
        
        Args:
            metric: Metric to analyze (mece_score, quality_score, base_skill_count)
            window: Number of recent entries to analyze
            
        Returns:
            Trend analysis dictionary
        """
        if not self.metrics_file.exists():
            return {'trend': 'no_data', 'entries': 0}
        
        metrics = []
        with open(self.metrics_file, 'r') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
        
        if len(metrics) < 2:
            return {'trend': 'insufficient_data', 'entries': len(metrics)}
        
        # Take last N entries
        recent_metrics = metrics[-window:] if len(metrics) > window else metrics
        
        values = [m[metric] for m in recent_metrics if metric in m]
        
        if len(values) < 2:
            return {'trend': 'insufficient_data', 'entries': len(values)}
        
        # Calculate trend
        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])
        
        change = second_half - first_half
        percent_change = (change / first_half * 100) if first_half > 0 else 0
        
        if percent_change > 5:
            trend = 'improving'
        elif percent_change < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'percent_change': float(percent_change),
            'first_half_avg': float(first_half),
            'second_half_avg': float(second_half),
            'latest_value': float(values[-1]),
            'entries': len(values)
        }


def main():
    """Example usage of feedback loop system."""
    print("Feedback Loop System")
    print("=" * 50)
    print("\nThis module provides decision logging and threshold calibration.")
    print("\nUsage:")
    print("  from feedback_loop import FeedbackLogger, ThresholdCalibrator")
    print("  logger = FeedbackLogger()")
    print("  logger.log_decision('merge', base_skill_a, base_skill_b, 'high_similarity')")
    print("\nFor integration with UI, import the FeedbackLogger class.")


if __name__ == '__main__':
    main()

