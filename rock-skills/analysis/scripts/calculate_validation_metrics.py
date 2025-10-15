#!/usr/bin/env python3
"""
Validation Metrics Calculator

Calculates accuracy and inter-rater reliability for LLM-assisted taxonomy mappings.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import Dict, Tuple


def calculate_agreement_rate(validation_df: pd.DataFrame) -> Dict:
    """
    Calculate agreement rate between LLM and human reviewers.
    
    Args:
        validation_df: DataFrame with validation results
        
    Returns:
        Dict with agreement metrics
    """
    # Filter to rows with reviewer 1 validation
    validated = validation_df[validation_df['reviewer_1_correct'].notna()].copy()
    
    if len(validated) == 0:
        return {'error': 'No validation data available'}
    
    # Calculate agreement
    total = len(validated)
    correct = (validated['reviewer_1_correct'] == True).sum()
    incorrect = (validated['reviewer_1_correct'] == False).sum()
    
    accuracy = correct / total
    
    return {
        'total_validated': total,
        'llm_correct': correct,
        'llm_incorrect': incorrect,
        'accuracy_rate': accuracy,
        'error_rate': 1 - accuracy
    }


def calculate_inter_rater_reliability(validation_df: pd.DataFrame) -> Dict:
    """
    Calculate inter-rater reliability (Cohen's Kappa) between two reviewers.
    
    Args:
        validation_df: DataFrame with validation results from 2+ reviewers
        
    Returns:
        Dict with inter-rater metrics
    """
    # Filter to rows with both reviewers
    dual_reviewed = validation_df[
        validation_df['reviewer_1_correct'].notna() &
        validation_df['reviewer_2_correct'].notna()
    ].copy()
    
    if len(dual_reviewed) == 0:
        return {'error': 'Need 2 reviewers for inter-rater reliability'}
    
    # Calculate agreement
    total = len(dual_reviewed)
    agreements = (dual_reviewed['reviewer_1_correct'] == dual_reviewed['reviewer_2_correct']).sum()
    
    # Simple agreement rate
    agreement_rate = agreements / total
    
    # Cohen's Kappa (accounting for chance agreement)
    r1_yes = (dual_reviewed['reviewer_1_correct'] == True).sum()
    r1_no = (dual_reviewed['reviewer_1_correct'] == False).sum()
    r2_yes = (dual_reviewed['reviewer_2_correct'] == True).sum()
    r2_no = (dual_reviewed['reviewer_2_correct'] == False).sum()
    
    # Expected agreement by chance
    p_yes = (r1_yes / total) * (r2_yes / total)
    p_no = (r1_no / total) * (r2_no / total)
    expected_agreement = p_yes + p_no
    
    # Cohen's Kappa
    if expected_agreement == 1.0:
        kappa = 1.0  # Perfect agreement
    else:
        kappa = (agreement_rate - expected_agreement) / (1 - expected_agreement)
    
    return {
        'total_dual_reviewed': total,
        'agreements': agreements,
        'disagreements': total - agreements,
        'agreement_rate': agreement_rate,
        'cohens_kappa': kappa,
        'interpretation': interpret_kappa(kappa)
    }


def interpret_kappa(kappa: float) -> str:
    """Interpret Cohen's Kappa value."""
    if kappa < 0:
        return "Poor (less than chance)"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    else:
        return "Almost Perfect"


def calculate_accuracy_by_confidence(validation_df: pd.DataFrame) -> Dict:
    """
    Calculate LLM accuracy stratified by confidence level.
    
    Args:
        validation_df: DataFrame with validation results
        
    Returns:
        Dict mapping confidence level to accuracy
    """
    validated = validation_df[validation_df['reviewer_1_correct'].notna()].copy()
    
    if len(validated) == 0:
        return {}
    
    results = {}
    for confidence in ['High', 'Medium', 'Low']:
        subset = validated[validated['llm_confidence'] == confidence]
        if len(subset) > 0:
            correct = (subset['reviewer_1_correct'] == True).sum()
            accuracy = correct / len(subset)
            results[confidence] = {
                'count': len(subset),
                'correct': correct,
                'accuracy': accuracy
            }
    
    return results


def calculate_accuracy_by_grade(validation_df: pd.DataFrame) -> Dict:
    """
    Calculate LLM accuracy stratified by grade band.
    
    Args:
        validation_df: DataFrame with validation results
        
    Returns:
        Dict mapping grade band to accuracy
    """
    validated = validation_df[validation_df['reviewer_1_correct'].notna()].copy()
    
    if len(validated) == 0 or 'grade_level' not in validated.columns:
        return {}
    
    # Define grade bands
    def get_grade_band(grade_str):
        if pd.isna(grade_str):
            return 'Unknown'
        grade_lower = str(grade_str).lower()
        if 'pre' in grade_lower or 'prek' in grade_lower:
            return 'Pre-K'
        elif 'k' in grade_lower or 'kindergarten' in grade_lower:
            return 'K'
        elif any(g in grade_lower for g in ['1', '2']):
            return 'Grades 1-2'
        elif any(g in grade_lower for g in ['3', '4', '5']):
            return 'Grades 3-5'
        elif any(g in grade_lower for g in ['6', '7', '8']):
            return 'Grades 6-8'
        elif any(g in grade_lower for g in ['9', '10', '11', '12', 'high']):
            return 'Grades 9-12'
        else:
            return 'Unknown'
    
    validated['grade_band'] = validated['grade_level'].apply(get_grade_band)
    
    results = {}
    for band in validated['grade_band'].unique():
        subset = validated[validated['grade_band'] == band]
        if len(subset) > 0:
            correct = (subset['reviewer_1_correct'] == True).sum()
            accuracy = correct / len(subset)
            results[band] = {
                'count': len(subset),
                'correct': correct,
                'accuracy': accuracy
            }
    
    return results


def calculate_gap_detection_accuracy(validation_df: pd.DataFrame) -> Dict:
    """
    Calculate how well the system identifies true taxonomy gaps.
    
    Args:
        validation_df: DataFrame with validation results
        
    Returns:
        Dict with gap detection metrics
    """
    # Skills flagged by LLM as low confidence (potential gaps)
    llm_flagged = validation_df[validation_df['llm_confidence'] == 'Low'].copy()
    
    if len(llm_flagged) == 0:
        return {'error': 'No skills flagged as low confidence by LLM'}
    
    # Check if reviewer confirmed these are gaps or found correct mappings
    validated_flags = llm_flagged[llm_flagged['reviewer_1_correct'].notna()]
    
    if len(validated_flags) == 0:
        return {'error': 'No validation data for low-confidence skills'}
    
    # True gaps: LLM said low confidence, reviewer agreed (marked incorrect)
    true_gaps = (validated_flags['reviewer_1_correct'] == False).sum()
    
    # False positives: LLM said low confidence, but reviewer found correct mapping
    false_positives = (validated_flags['reviewer_1_correct'] == True).sum()
    
    precision = true_gaps / len(validated_flags) if len(validated_flags) > 0 else 0
    
    return {
        'llm_flagged_count': len(llm_flagged),
        'validated_flags': len(validated_flags),
        'true_gaps': true_gaps,
        'false_positives': false_positives,
        'gap_detection_precision': precision
    }


def generate_validation_report(validation_file: Path, output_file: Path):
    """
    Generate comprehensive validation metrics report.
    
    Args:
        validation_file: Path to completed validation CSV
        output_file: Path for output report
    """
    print(f"Loading validation data from: {validation_file}")
    validation_df = pd.read_csv(validation_file)
    
    print(f"Calculating metrics for {len(validation_df)} skills...")
    
    # Calculate all metrics
    agreement = calculate_agreement_rate(validation_df)
    inter_rater = calculate_inter_rater_reliability(validation_df)
    by_confidence = calculate_accuracy_by_confidence(validation_df)
    by_grade = calculate_accuracy_by_grade(validation_df)
    gap_detection = calculate_gap_detection_accuracy(validation_df)
    
    # Generate report
    report = f"""# Validation Metrics Report

**Generated**: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}
**Validation File**: {validation_file.name}

---

## Overall Accuracy

"""
    
    if 'error' not in agreement:
        report += f"""- **Total Skills Validated**: {agreement['total_validated']}
- **LLM Correct**: {agreement['llm_correct']} ({agreement['accuracy_rate']:.1%})
- **LLM Incorrect**: {agreement['llm_incorrect']} ({agreement['error_rate']:.1%})

**Result**: {"✅ PASS" if agreement['accuracy_rate'] >= 0.75 else "⚠️ NEEDS IMPROVEMENT" if agreement['accuracy_rate'] >= 0.65 else "❌ FAIL"}

"""
    else:
        report += f"*{agreement['error']}*\n\n"
    
    report += "---\n\n## Inter-Rater Reliability\n\n"
    
    if 'error' not in inter_rater:
        report += f"""- **Skills Dual-Reviewed**: {inter_rater['total_dual_reviewed']}
- **Agreements**: {inter_rater['agreements']} ({inter_rater['agreement_rate']:.1%})
- **Disagreements**: {inter_rater['disagreements']}
- **Cohen's Kappa**: {inter_rater['cohens_kappa']:.3f} ({inter_rater['interpretation']})

**Interpretation**: {inter_rater['interpretation']} agreement between reviewers

"""
    else:
        report += f"*{inter_rater['error']}*\n\n"
    
    report += "---\n\n## Accuracy by Confidence Level\n\n"
    
    if by_confidence:
        report += "| Confidence | Count | Correct | Accuracy |\n"
        report += "|------------|-------|---------|----------|\n"
        for conf in ['High', 'Medium', 'Low']:
            if conf in by_confidence:
                stats = by_confidence[conf]
                report += f"| {conf} | {stats['count']} | {stats['correct']} | {stats['accuracy']:.1%} |\n"
        report += "\n"
        
        # Check if confidence correlates with accuracy
        if 'High' in by_confidence and 'Low' in by_confidence:
            high_acc = by_confidence['High']['accuracy']
            low_acc = by_confidence['Low']['accuracy']
            if high_acc > low_acc + 0.15:
                report += "✅ **Good calibration**: High confidence = higher accuracy\n\n"
            else:
                report += "⚠️ **Poor calibration**: Confidence doesn't predict accuracy\n\n"
    else:
        report += "*No confidence level data available*\n\n"
    
    report += "---\n\n## Accuracy by Grade Band\n\n"
    
    if by_grade:
        report += "| Grade Band | Count | Correct | Accuracy |\n"
        report += "|------------|-------|---------|----------|\n"
        for band in sorted(by_grade.keys()):
            stats = by_grade[band]
            report += f"| {band} | {stats['count']} | {stats['correct']} | {stats['accuracy']:.1%} |\n"
        report += "\n"
    else:
        report += "*No grade level data available*\n\n"
    
    report += "---\n\n## Gap Detection Performance\n\n"
    
    if 'error' not in gap_detection:
        report += f"""- **LLM Flagged as Low Confidence**: {gap_detection['llm_flagged_count']}
- **Validated Flags**: {gap_detection['validated_flags']}
- **True Gaps**: {gap_detection['true_gaps']}
- **False Positives**: {gap_detection['false_positives']}
- **Precision**: {gap_detection['gap_detection_precision']:.1%}

**Interpretation**: When LLM flags low confidence, it's a true gap {gap_detection['gap_detection_precision']:.0%} of the time

"""
    else:
        report += f"*{gap_detection['error']}*\n\n"
    
    report += """---

## Recommendations

"""
    
    # Generate recommendations based on metrics
    if 'error' not in agreement:
        if agreement['accuracy_rate'] >= 0.85:
            report += "1. ✅ **Excellent Performance**: System ready for production scaling\n"
        elif agreement['accuracy_rate'] >= 0.75:
            report += "1. ✅ **Good Performance**: Minor refinements suggested before scaling\n"
        elif agreement['accuracy_rate'] >= 0.65:
            report += "1. ⚠️ **Moderate Performance**: Significant prompt/system improvements needed\n"
        else:
            report += "1. ❌ **Poor Performance**: Major system redesign required\n"
    
    if by_confidence and 'High' in by_confidence and 'Low' in by_confidence:
        high_acc = by_confidence['High']['accuracy']
        low_acc = by_confidence['Low']['accuracy']
        if high_acc <= low_acc + 0.10:
            report += "2. ⚠️ **Improve Confidence Calibration**: LLM confidence doesn't correlate with accuracy\n"
    
    if 'error' not in gap_detection and gap_detection['gap_detection_precision'] < 0.60:
        report += "3. ⚠️ **Too Many False Positives**: Refine gap detection criteria\n"
    
    report += "\n---\n"
    
    # Write report
    output_file.write_text(report)
    print(f"\n✓ Validation report generated: {output_file}")
    
    # Print summary to console
    if 'error' not in agreement:
        print(f"\nValidation Summary:")
        print(f"  Accuracy: {agreement['accuracy_rate']:.1%}")
        if 'error' not in inter_rater:
            print(f"  Inter-Rater: {inter_rater['cohens_kappa']:.3f} ({inter_rater['interpretation']})")


def main():
    parser = argparse.ArgumentParser(description='Calculate validation metrics')
    parser.add_argument('--validation-file', required=True, help='Path to completed validation CSV')
    parser.add_argument('--output', required=True, help='Path for output report')
    
    args = parser.parse_args()
    
    validation_file = Path(args.validation_file)
    output_file = Path(args.output)
    
    if not validation_file.exists():
        print(f"Error: Validation file not found: {validation_file}")
        return 1
    
    generate_validation_report(validation_file, output_file)
    return 0


if __name__ == '__main__':
    exit(main())

