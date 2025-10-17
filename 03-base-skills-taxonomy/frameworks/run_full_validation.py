#!/usr/bin/env python3
"""
Master Validation Suite

Runs complete taxonomy validation:
1. Semantic similarity analysis (detect duplicates)
2. Framework convergence analysis (assess scientific grounding)
3. Combined master report with prioritized recommendations
"""

import subprocess
import sys
from pathlib import Path
import pandas as pd

def run_semantic_validation(output_dir: str = 'validation_outputs'):
    """
    Run semantic similarity validation.
    
    Args:
        output_dir: Output directory for results
    """
    print("="*70)
    print("PHASE 1: SEMANTIC SIMILARITY VALIDATION")
    print("="*70)
    print()
    
    result = subprocess.run(
        [sys.executable, 'semantic_validator.py', '--output', output_dir],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("⚠ Semantic validation encountered errors")
        return False
    
    return True

def run_convergence_analysis(output_dir: str = 'validation_outputs'):
    """
    Run framework convergence analysis.
    
    Args:
        output_dir: Output directory for results
    """
    print("\n" + "="*70)
    print("PHASE 2: FRAMEWORK CONVERGENCE ANALYSIS")
    print("="*70)
    print()
    
    result = subprocess.run(
        [sys.executable, 'framework_tracker.py', '--output', output_dir],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("⚠ Convergence analysis encountered errors")
        return False
    
    return True

def generate_visualizations(output_dir: str = 'validation_outputs'):
    """
    Generate visualizations.
    
    Args:
        output_dir: Output directory for results
    """
    print("\n" + "="*70)
    print("PHASE 3: GENERATING VISUALIZATIONS")
    print("="*70)
    print()
    
    result = subprocess.run(
        [sys.executable, 'semantic_similarity_heatmap.py', '--input', output_dir],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("⚠ Visualization generation encountered errors")
        return False
    
    return True

def generate_master_report(output_dir: str = 'validation_outputs'):
    """
    Generate combined master validation report.
    
    Args:
        output_dir: Output directory
    """
    print("\n" + "="*70)
    print("PHASE 4: GENERATING MASTER REPORT")
    print("="*70)
    print()
    
    output_path = Path(output_dir)
    
    # Load results
    print("Loading validation results...")
    
    # Semantic validation
    duplicates_path = output_path / 'potential_duplicates.csv'
    semantic_report_path = output_path / 'semantic_validation_report.md'
    
    # Convergence analysis
    confidence_path = output_path / 'concept_confidence.csv'
    convergence_report_path = output_path / 'framework_convergence_summary.md'
    
    duplicates_df = None
    confidence_df = None
    
    if duplicates_path.exists():
        duplicates_df = pd.read_csv(duplicates_path)
        print(f"  ✓ Loaded {len(duplicates_df)} potential duplicates")
    
    if confidence_path.exists():
        confidence_df = pd.read_csv(confidence_path)
        print(f"  ✓ Loaded confidence data for {len(confidence_df)} concepts")
    
    # Generate master report
    report_lines = []
    
    report_lines.append("# Master Taxonomy Validation Report")
    report_lines.append(f"\n**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append("\n**Validation Suite**: Semantic Similarity + Framework Convergence")
    report_lines.append("\n---\n")
    
    # Executive Summary
    report_lines.append("## Executive Summary\n")
    
    if duplicates_df is not None:
        high_sim = len(duplicates_df[duplicates_df['similarity'] >= 0.90])
        med_sim = len(duplicates_df[(duplicates_df['similarity'] >= 0.85) & (duplicates_df['similarity'] < 0.90)])
        
        report_lines.append(f"### Semantic Analysis\n")
        report_lines.append(f"- **High-priority duplicates** (>0.90 similarity): {high_sim}")
        report_lines.append(f"- **Medium-priority overlaps** (0.85-0.90 similarity): {med_sim}")
        report_lines.append(f"- **Total flagged pairs**: {len(duplicates_df)}\n")
        
        if high_sim > 50:
            report_lines.append("⚠️ **Attention**: Significant number of potential duplicates detected\n")
        elif high_sim > 0:
            report_lines.append("✓ **Moderate**: Some duplicates found, review recommended\n")
        else:
            report_lines.append("✅ **Excellent**: No high-priority duplicates detected\n")
    
    if confidence_df is not None:
        strong = len(confidence_df[confidence_df['Evidence_Strength'] == 'strong'])
        moderate = len(confidence_df[confidence_df['Evidence_Strength'] == 'moderate'])
        weak = len(confidence_df[confidence_df['Evidence_Strength'] == 'weak'])
        unvalidated = len(confidence_df[confidence_df['Evidence_Strength'] == 'unvalidated'])
        
        report_lines.append(f"### Framework Convergence\n")
        report_lines.append(f"- **Strong evidence** (3+ frameworks): {strong} concepts")
        report_lines.append(f"- **Moderate evidence** (2 frameworks): {moderate} concepts")
        report_lines.append(f"- **Weak evidence** (1 framework): {weak} concepts")
        report_lines.append(f"- **Unvalidated** (0 frameworks): {unvalidated} concepts\n")
        
        validated_pct = 100 * (len(confidence_df) - unvalidated) / len(confidence_df) if len(confidence_df) > 0 else 0
        
        if validated_pct >= 80:
            report_lines.append(f"✅ **Excellent**: {validated_pct:.1f}% of concepts have framework support\n")
        elif validated_pct >= 60:
            report_lines.append(f"✓ **Good**: {validated_pct:.1f}% of concepts validated\n")
        else:
            report_lines.append(f"⚠️ **Moderate**: {validated_pct:.1f}% validated - consider adding more frameworks\n")
    
    # Combined Analysis
    report_lines.append("## Combined Analysis: High-Priority Issues\n")
    
    if duplicates_df is not None and confidence_df is not None:
        report_lines.append("### Concepts with BOTH High Similarity AND Low Confidence\n")
        report_lines.append("These require immediate attention:\n")
        
        # Find concepts that are similar AND have low framework support
        high_sim_concepts = set()
        for _, row in duplicates_df[duplicates_df['similarity'] >= 0.90].iterrows():
            high_sim_concepts.add(row['concept1_name'])
            high_sim_concepts.add(row['concept2_name'])
        
        low_conf_concepts = set(confidence_df[
            confidence_df['Evidence_Strength'].isin(['weak', 'unvalidated'])
        ]['Concept_Name'].values)
        
        critical_concepts = high_sim_concepts.intersection(low_conf_concepts)
        
        if critical_concepts:
            report_lines.append(f"Found {len(critical_concepts)} critical concepts:\n")
            for concept in list(critical_concepts)[:20]:
                report_lines.append(f"- {concept}")
            report_lines.append("\n**Recommendation**: These concepts are both similar to others AND lack framework validation.")
            report_lines.append("Consider consolidation or additional validation.\n")
        else:
            report_lines.append("✓ No concepts found with both high similarity and low confidence.\n")
        
        report_lines.append("### Concepts with High Similarity BUT Strong Framework Support\n")
        
        strong_conf_concepts = set(confidence_df[
            confidence_df['Evidence_Strength'].isin(['strong', 'moderate'])
        ]['Concept_Name'].values)
        
        validated_similar = high_sim_concepts.intersection(strong_conf_concepts)
        
        if validated_similar:
            report_lines.append(f"Found {len(validated_similar)} concepts:\n")
            report_lines.append("These are similar to other concepts but well-supported by frameworks.")
            report_lines.append("**Recommendation**: May represent legitimate distinct concepts. Review for clarification in annotations.\n")
        else:
            report_lines.append("No strongly-validated concepts with high similarity.\n")
    
    # Recommendations
    report_lines.append("## Prioritized Recommendations\n")
    
    report_lines.append("### Priority 1: Critical Issues (This Week)\n")
    if duplicates_df is not None and len(duplicates_df[duplicates_df['similarity'] >= 0.90]) > 0:
        report_lines.append("1. **Review high-similarity pairs** (>0.90) in `potential_duplicates.csv`")
        report_lines.append("   - Determine if concepts should be merged or disambiguated")
        report_lines.append("   - Update annotations to clarify distinctions\n")
    
    if confidence_df is not None and len(confidence_df[confidence_df['Evidence_Strength'] == 'unvalidated']) > 500:
        report_lines.append("2. **Address unvalidated concepts** - large number lack framework support")
        report_lines.append("   - Add more frameworks to validation suite")
        report_lines.append("   - Or document rationale for novel concepts\n")
    
    report_lines.append("### Priority 2: Improvements (This Month)\n")
    report_lines.append("1. **Optimize semantic organization** - review sibling conflicts")
    report_lines.append("2. **Validate single-source concepts** - seek additional framework support")
    report_lines.append("3. **Clarify high-similarity concepts** - improve annotations\n")
    
    report_lines.append("### Priority 3: Ongoing Maintenance\n")
    report_lines.append("1. **Re-run validation** after taxonomy changes")
    report_lines.append("2. **Add new frameworks** as they become available")
    report_lines.append("3. **Monitor convergence scores** for new concepts\n")
    
    # Link to detailed reports
    report_lines.append("## Detailed Reports\n")
    report_lines.append(f"- [Semantic Validation Report]({semantic_report_path.name})")
    report_lines.append(f"- [Framework Convergence Report]({convergence_report_path.name})")
    report_lines.append(f"- [Potential Duplicates CSV]({duplicates_path.name})")
    report_lines.append(f"- [Concept Confidence CSV]({confidence_path.name})")
    report_lines.append(f"- [Visualizations](visualizations/)\n")
    
    report_lines.append("---\n")
    report_lines.append("*Generated by Master Validation Suite*")
    
    # Save master report
    master_report_path = output_path / 'validation_master_report.md'
    with open(master_report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✓ Generated master report: {master_report_path}")
    
    # Generate recommendations CSV
    if duplicates_df is not None or confidence_df is not None:
        recommendations = []
        
        if duplicates_df is not None:
            for _, row in duplicates_df[duplicates_df['similarity'] >= 0.90].head(50).iterrows():
                recommendations.append({
                    'Priority': 1,
                    'Type': 'Semantic Duplicate',
                    'Concept_1': row['concept1_name'],
                    'Concept_2': row['concept2_name'],
                    'Issue': f"High similarity ({row['similarity']:.3f})",
                    'Recommendation': 'Review for consolidation or disambiguation',
                    'Complexity': 'Medium'
                })
        
        if confidence_df is not None:
            for _, row in confidence_df[confidence_df['Evidence_Strength'] == 'weak'].head(30).iterrows():
                recommendations.append({
                    'Priority': 2,
                    'Type': 'Low Framework Support',
                    'Concept_1': row['Concept_Name'],
                    'Concept_2': '',
                    'Issue': f"Only 1 framework: {row['Frameworks']}",
                    'Recommendation': 'Seek additional framework validation',
                    'Complexity': 'Low'
                })
        
        if recommendations:
            rec_df = pd.DataFrame(recommendations)
            rec_df = rec_df.sort_values('Priority')
            rec_path = output_path / 'recommendations_priority.csv'
            rec_df.to_csv(rec_path, index=False)
            print(f"✓ Generated prioritized recommendations: {rec_path}")
    
    return True

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Taxonomy Validation Suite")
    parser.add_argument('--output', '-o', type=str,
                        default='validation_outputs',
                        help='Output directory for all validation results')
    parser.add_argument('--skip-semantic', action='store_true',
                        help='Skip semantic similarity validation')
    parser.add_argument('--skip-convergence', action='store_true',
                        help='Skip framework convergence analysis')
    parser.add_argument('--skip-viz', action='store_true',
                        help='Skip visualization generation')
    
    args = parser.parse_args()
    
    print("="*70)
    print("MASTER TAXONOMY VALIDATION SUITE")
    print("="*70)
    print()
    print(f"Output directory: {args.output}")
    print()
    
    success = True
    
    # Run semantic validation
    if not args.skip_semantic:
        if not run_semantic_validation(args.output):
            success = False
    else:
        print("Skipping semantic validation (--skip-semantic)")
    
    # Run convergence analysis
    if not args.skip_convergence:
        if not run_convergence_analysis(args.output):
            success = False
    else:
        print("\nSkipping convergence analysis (--skip-convergence)")
    
    # Generate visualizations
    if not args.skip_viz:
        if not generate_visualizations(args.output):
            success = False
    else:
        print("\nSkipping visualizations (--skip-viz)")
    
    # Generate master report
    generate_master_report(args.output)
    
    # Final summary
    print("\n" + "="*70)
    if success:
        print("✅ VALIDATION SUITE COMPLETE")
    else:
        print("⚠️ VALIDATION SUITE COMPLETE WITH WARNINGS")
    print("="*70)
    print(f"\nAll outputs saved to: {args.output}/")
    print(f"\n📊 Key Reports:")
    print(f"   - validation_master_report.md (START HERE)")
    print(f"   - semantic_validation_report.md")
    print(f"   - framework_convergence_summary.md")
    print(f"   - recommendations_priority.csv")
    print(f"   - visualizations/")

if __name__ == '__main__':
    main()

