#!/usr/bin/env python3
"""
Enhanced Base Skill Extraction - Integration Test

Tests the complete improved pipeline:
1. Redundancy-seeded clustering
2. Specification discovery
3. Quality metrics calculation
4. Enhanced MECE validation

Usage:
    python3 test_enhanced_extraction.py --input ../../rock_data/skill_list_filtered_data_set.csv --limit 50
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract_base_skills import BaseSkillExtractor
from specification_discovery import SpecificationDiscoverer
from quality_metrics import QualityMetricsCalculator, ValidationSetManager
from validate_mece import MECEValidator


def test_enhanced_pipeline(skills_df: pd.DataFrame,
                           redundancy_results_path: str = None,
                           enhanced_metadata_path: str = None,
                           sor_taxonomy_path: str = None,
                           use_llm: bool = False) -> Dict:
    """
    Test the complete enhanced extraction pipeline.
    
    Args:
        skills_df: DataFrame with ROCK skills
        redundancy_results_path: Path to redundancy analysis results
        enhanced_metadata_path: Path to enhanced metadata CSV
        sor_taxonomy_path: Path to SoR taxonomy CSV
        use_llm: Whether to use LLM (requires AWS credentials)
        
    Returns:
        Test results dictionary
    """
    print("\n" + "="*80)
    print("ENHANCED BASE SKILL EXTRACTION - INTEGRATION TEST")
    print("="*80 + "\n")
    
    test_results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'total_skills': len(skills_df),
        'stages': {}
    }
    
    # STAGE 1: BASE SKILL EXTRACTION (with redundancy integration)
    print("\n" + "="*80)
    print("STAGE 1: BASE SKILL EXTRACTION")
    print("="*80)
    
    extractor = BaseSkillExtractor(
        use_llm=use_llm,
        use_clustering=True,
        redundancy_results_path=redundancy_results_path
    )
    
    skills_with_mappings, base_skills = extractor.extract_base_skills(skills_df)
    
    test_results['stages']['extraction'] = {
        'base_skills_generated': len(base_skills),
        'skills_mapped': skills_with_mappings['base_skill_id'].notna().sum(),
        'skills_unmapped': skills_with_mappings['base_skill_id'].isna().sum(),
        'avg_skills_per_base': len(skills_df) / len(base_skills) if base_skills else 0,
        'seed_clusters_used': sum(1 for bs in base_skills if bs.get('created_by') == 'redundancy_seeded')
    }
    
    print(f"\n✓ Extraction complete: {len(base_skills)} base skills generated")
    print(f"  - Mapped skills: {test_results['stages']['extraction']['skills_mapped']}")
    print(f"  - Seed clusters from redundancy: {test_results['stages']['extraction']['seed_clusters_used']}")
    
    # STAGE 2: SPECIFICATION DISCOVERY
    print("\n" + "="*80)
    print("STAGE 2: SPECIFICATION DISCOVERY")
    print("="*80)
    
    # Load enhanced metadata if available
    metadata_df = None
    if enhanced_metadata_path and Path(enhanced_metadata_path).exists():
        print(f"\nLoading enhanced metadata from {enhanced_metadata_path}...")
        metadata_df = pd.read_csv(enhanced_metadata_path)
        print(f"✓ Loaded enhanced metadata for {len(metadata_df)} skills")
    else:
        # Use basic metadata from skills_df
        print("\n⚠ Enhanced metadata not found, using basic metadata from skills")
        metadata_df = skills_df.copy()
    
    discoverer = SpecificationDiscoverer()
    discovered_specs = discoverer.discover_specifications(base_skills, metadata_df)
    spec_report = discoverer.generate_specification_report(discovered_specs)
    
    test_results['stages']['specification_discovery'] = {
        'total_specifications': len(discovered_specs),
        'by_level': spec_report['by_level'],
        'new_specifications': len(spec_report['new_specifications']),
        'top_3_specs': [
            {
                'spec_type': s['spec_type'],
                'discriminative_power': round(s['discriminative_power'], 3),
                'usage_count': s['usage_count']
            }
            for s in discovered_specs[:3]
        ]
    }
    
    print(f"\n✓ Specification discovery complete: {len(discovered_specs)} specifications found")
    print(f"  - Primary: {spec_report['by_level']['primary']}")
    print(f"  - Secondary: {spec_report['by_level']['secondary']}")
    print(f"  - Tertiary: {spec_report['by_level']['tertiary']}")
    print(f"  - New (not predefined): {len(spec_report['new_specifications'])}")
    
    # STAGE 3: QUALITY METRICS
    print("\n" + "="*80)
    print("STAGE 3: QUALITY METRICS CALCULATION")
    print("="*80)
    
    # Load SoR taxonomy if available
    sor_taxonomy = None
    if sor_taxonomy_path and Path(sor_taxonomy_path).exists():
        print(f"\nLoading SoR taxonomy from {sor_taxonomy_path}...")
        sor_taxonomy = pd.read_csv(sor_taxonomy_path)
        print(f"✓ Loaded SoR taxonomy with {len(sor_taxonomy)} concepts")
    else:
        print("\n⚠ SoR taxonomy not found, SoR alignment scores will be estimates")
    
    quality_calculator = QualityMetricsCalculator()
    quality_report = quality_calculator.generate_quality_report(base_skills, metadata_df, sor_taxonomy)
    
    test_results['stages']['quality_metrics'] = {
        'average_quality': round(quality_report['average_quality'], 3),
        'median_quality': round(quality_report['median_quality'], 3),
        'quality_distribution': quality_report['quality_distribution'],
        'flagged_for_review': len(quality_report['flagged_for_review']),
        'average_coherence': round(quality_report['average_metrics']['coherence'], 3),
        'average_granularity': round(quality_report['average_metrics']['granularity'], 3),
        'average_coverage': round(quality_report['average_metrics']['coverage'], 3),
        'average_sor_alignment': round(quality_report['average_metrics']['sor_alignment'], 3)
    }
    
    print(f"\n✓ Quality metrics calculated")
    print(f"  - Average Quality: {test_results['stages']['quality_metrics']['average_quality']}")
    print(f"  - Grade A: {quality_report['quality_distribution']['A']}")
    print(f"  - Grade B: {quality_report['quality_distribution']['B']}")
    print(f"  - Grade C: {quality_report['quality_distribution']['C']}")
    print(f"  - Flagged for review: {test_results['stages']['quality_metrics']['flagged_for_review']}")
    
    # STAGE 4: MECE VALIDATION
    print("\n" + "="*80)
    print("STAGE 4: MECE VALIDATION (ENHANCED)")
    print("="*80)
    
    validator = MECEValidator(use_llm=False)  # Disable LLM for faster testing
    mece_report = validator.generate_validation_report(base_skills, skills_with_mappings, skills_df)
    
    test_results['stages']['mece_validation'] = {
        'mece_score': round(mece_report['mece_score'], 3),
        'mutual_exclusivity_score': round(mece_report['mutual_exclusivity']['score'], 3),
        'collective_exhaustiveness_score': round(mece_report['collective_exhaustiveness']['score'], 3),
        'total_conflicts': mece_report['grooming_queue_summary']['total_conflicts'],
        'high_confidence_overlaps': sum(1 for c in mece_report['mutual_exclusivity']['base_skill_conflicts'] 
                                       if c.get('confidence') == 'high'),
        'unmapped_skills': mece_report['collective_exhaustiveness']['unmapped_rock_skills']
    }
    
    print(f"\n✓ MECE validation complete")
    print(f"  - MECE Score: {test_results['stages']['mece_validation']['mece_score']}")
    print(f"  - Mutual Exclusivity: {test_results['stages']['mece_validation']['mutual_exclusivity_score']}")
    print(f"  - Collective Exhaustiveness: {test_results['stages']['mece_validation']['collective_exhaustiveness_score']}")
    print(f"  - Total Conflicts: {test_results['stages']['mece_validation']['total_conflicts']}")
    print(f"  - High Confidence Overlaps: {test_results['stages']['mece_validation']['high_confidence_overlaps']}")
    
    # FINAL SUMMARY
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    test_results['success'] = True
    test_results['overall_assessment'] = {
        'base_skills_generated': len(base_skills),
        'mece_score': test_results['stages']['mece_validation']['mece_score'],
        'average_quality': test_results['stages']['quality_metrics']['average_quality'],
        'specifications_discovered': len(discovered_specs),
        'redundancy_integration': 'enabled' if redundancy_results_path else 'disabled',
        'enhanced_metadata': 'available' if enhanced_metadata_path and Path(enhanced_metadata_path).exists() else 'not_available',
        'sor_taxonomy': 'available' if sor_taxonomy and len(sor_taxonomy) > 0 else 'not_available'
    }
    
    # Determine if improvements are evident
    improvements = []
    if test_results['stages']['extraction']['seed_clusters_used'] > 0:
        improvements.append("Redundancy-seeded clustering active")
    if test_results['stages']['specification_discovery']['new_specifications'] > 0:
        improvements.append(f"Discovered {test_results['stages']['specification_discovery']['new_specifications']} new specification types")
    if test_results['stages']['mece_validation']['mece_score'] >= 0.85:
        improvements.append("MECE score ≥ 0.85 (target achieved)")
    if test_results['stages']['quality_metrics']['average_quality'] >= 0.70:
        improvements.append("Average quality ≥ 0.70 (good)")
    
    test_results['improvements'] = improvements
    
    print(f"\nTotal Skills Processed: {len(skills_df)}")
    print(f"Base Skills Generated: {len(base_skills)}")
    print(f"MECE Score: {test_results['stages']['mece_validation']['mece_score']:.3f}")
    print(f"Average Quality: {test_results['stages']['quality_metrics']['average_quality']:.3f}")
    print(f"Specifications Discovered: {len(discovered_specs)}")
    
    print("\nImprovements Detected:")
    for improvement in improvements:
        print(f"  ✓ {improvement}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    return test_results


def main():
    parser = argparse.ArgumentParser(description='Test enhanced base skill extraction pipeline')
    parser.add_argument('--input', default='../../rock_data/skill_list_filtered_data_set.csv',
                       help='Input CSV file with ROCK skills')
    parser.add_argument('--redundancy-results', type=str, default=None,
                       help='Path to redundancy analysis results JSON')
    parser.add_argument('--enhanced-metadata', type=str, default=None,
                       help='Path to enhanced metadata CSV')
    parser.add_argument('--sor-taxonomy', type=str, default='../../POC_science_of_reading_literacy_skills_taxonomy.csv',
                       help='Path to Science of Reading taxonomy CSV')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of skills to process (for quick testing)')
    parser.add_argument('--use-llm', action='store_true',
                       help='Use LLM for refinement (requires AWS credentials, slower)')
    parser.add_argument('--output', default='./test_outputs',
                       help='Output directory for test results')
    
    args = parser.parse_args()
    
    # Load ROCK skills
    print(f"Loading ROCK skills from {args.input}...")
    skills_df = pd.read_csv(args.input)
    
    if args.limit:
        skills_df = skills_df.head(args.limit)
        print(f"Limited to {args.limit} skills for testing")
    
    print(f"Loaded {len(skills_df)} ROCK skills")
    
    # Run test
    test_results = test_enhanced_pipeline(
        skills_df=skills_df,
        redundancy_results_path=args.redundancy_results,
        enhanced_metadata_path=args.enhanced_metadata,
        sor_taxonomy_path=args.sor_taxonomy,
        use_llm=args.use_llm
    )
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n✓ Test results saved to {output_file}")
    
    # Return success/failure based on MECE score
    mece_score = test_results['stages']['mece_validation']['mece_score']
    if mece_score >= 0.85:
        print(f"\n✅ SUCCESS: MECE score {mece_score:.3f} meets target (≥ 0.85)")
        return 0
    else:
        print(f"\n⚠️ WARNING: MECE score {mece_score:.3f} below target (< 0.85)")
        print("   Consider:")
        print("   - Running with redundancy results (--redundancy-results)")
        print("   - Using enhanced metadata (--enhanced-metadata)")
        print("   - Increasing sample size (remove --limit)")
        return 1


if __name__ == '__main__':
    sys.exit(main())

