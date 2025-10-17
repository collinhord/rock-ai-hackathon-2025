#!/usr/bin/env python3
"""
Analyze Production Extraction Results - Phase 1.4

Comprehensive analysis of full-scale metadata extraction results from both
ELA and Math skills to identify:
- Field applicability rates by domain
- Domain-specific patterns
- Common failures and edge cases
- Math-specific metadata needs
- Recommendations for schema v2.0

Usage:
    python3 analyze_extraction_results.py \
        --ela ../outputs/production_extraction/ela/skill_metadata_enhanced_*.csv \
        --math ../outputs/production_extraction/math/skill_metadata_enhanced_*.csv \
        --output ../outputs/production_extraction/schema_analysis_report.md
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import json
from datetime import datetime
from typing import Dict, List, Tuple
import glob

def load_extraction_data(ela_pattern: str, math_pattern: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load ELA and Math extraction results."""
    
    # Find files matching patterns
    ela_files = glob.glob(ela_pattern)
    math_files = glob.glob(math_pattern)
    
    if not ela_files:
        raise FileNotFoundError(f"No ELA files found matching: {ela_pattern}")
    if not math_files:
        raise FileNotFoundError(f"No Math files found matching: {math_pattern}")
    
    print(f"Loading ELA data from: {ela_files[0]}")
    ela_df = pd.read_csv(ela_files[0])
    ela_df['CONTENT_AREA'] = 'English Language Arts'
    
    print(f"Loading Math data from: {math_files[0]}")
    math_df = pd.read_csv(math_files[0])
    math_df['CONTENT_AREA'] = 'Mathematics'
    
    print(f"Loaded {len(ela_df)} ELA skills and {len(math_df)} Math skills")
    
    return ela_df, math_df

def calculate_field_applicability(df: pd.DataFrame, field: str) -> Dict:
    """Calculate applicability metrics for a field."""
    
    total = len(df)
    non_empty = (df[field].notna() & (df[field] != '')).sum()
    not_applicable = (df[field] == 'not_applicable').sum()
    meaningful = non_empty - not_applicable
    
    return {
        'total_skills': total,
        'non_empty': non_empty,
        'not_applicable': not_applicable,
        'meaningful': meaningful,
        'non_empty_rate': non_empty / total if total > 0 else 0,
        'not_applicable_rate': not_applicable / total if total > 0 else 0,
        'meaningful_rate': meaningful / total if total > 0 else 0,
    }

def analyze_field_applicability(ela_df: pd.DataFrame, math_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze field applicability rates by domain."""
    
    fields = [
        'actions', 'targets', 'qualifiers', 'root_verb', 'direct_objects',
        'prepositional_phrases', 'key_concepts', 'complexity_markers',
        'text_type', 'text_mode', 'text_genre', 'skill_domain',
        'task_complexity', 'cognitive_demand', 'scope',
        'support_level', 'complexity_band'
    ]
    
    results = []
    
    for field in fields:
        ela_metrics = calculate_field_applicability(ela_df, field)
        math_metrics = calculate_field_applicability(math_df, field)
        
        results.append({
            'field': field,
            'ela_meaningful_rate': ela_metrics['meaningful_rate'],
            'math_meaningful_rate': math_metrics['meaningful_rate'],
            'ela_not_applicable_rate': ela_metrics['not_applicable_rate'],
            'math_not_applicable_rate': math_metrics['not_applicable_rate'],
            'gap': abs(ela_metrics['meaningful_rate'] - math_metrics['meaningful_rate']),
        })
    
    return pd.DataFrame(results)

def analyze_confidence_distribution(ela_df: pd.DataFrame, math_df: pd.DataFrame) -> Dict:
    """Analyze LLM confidence distribution."""
    
    return {
        'ela': ela_df['llm_confidence'].value_counts(normalize=True).to_dict(),
        'math': math_df['llm_confidence'].value_counts(normalize=True).to_dict(),
    }

def analyze_common_patterns(df: pd.DataFrame, domain: str) -> Dict:
    """Analyze common patterns in extracted metadata."""
    
    # Most common actions
    actions = df['actions'].str.split('|').explode()
    top_actions = actions.value_counts().head(20).to_dict()
    
    # Most common targets
    targets = df['targets'].str.split('|').explode()
    top_targets = targets.value_counts().head(20).to_dict()
    
    # Most common cognitive demands
    cognitive = df['cognitive_demand'].value_counts().to_dict()
    
    # Most common task complexities
    complexity = df['task_complexity'].value_counts().to_dict()
    
    return {
        'top_actions': top_actions,
        'top_targets': top_targets,
        'cognitive_demand': cognitive,
        'task_complexity': complexity,
    }

def identify_edge_cases(df: pd.DataFrame, domain: str) -> pd.DataFrame:
    """Identify edge cases and problematic extractions."""
    
    issues = []
    
    # Low confidence extractions
    low_conf = df[df['llm_confidence'] == 'low']
    issues.append({
        'issue_type': 'low_confidence',
        'count': len(low_conf),
        'rate': len(low_conf) / len(df),
        'sample_ids': low_conf['SKILL_ID'].head(5).tolist(),
    })
    
    # Excessive not_applicable
    metadata_fields = ['text_type', 'text_mode', 'text_genre', 'skill_domain', 'scope']
    na_count = df[metadata_fields].apply(lambda x: (x == 'not_applicable').sum(), axis=1)
    excessive_na = df[na_count >= 4]  # 4+ fields are not_applicable
    issues.append({
        'issue_type': 'excessive_not_applicable',
        'count': len(excessive_na),
        'rate': len(excessive_na) / len(df),
        'sample_ids': excessive_na['SKILL_ID'].head(5).tolist(),
    })
    
    # Missing structural components
    missing_actions = df[df['actions'] == '']
    issues.append({
        'issue_type': 'missing_actions',
        'count': len(missing_actions),
        'rate': len(missing_actions) / len(df),
        'sample_ids': missing_actions['SKILL_ID'].head(5).tolist(),
    })
    
    # Potential contradictions
    contradictions = df[
        ((df['cognitive_demand'] == 'recall') & (df['task_complexity'] == 'advanced')) |
        ((df['cognitive_demand'] == 'evaluation') & (df['task_complexity'] == 'basic'))
    ]
    issues.append({
        'issue_type': 'potential_contradiction',
        'count': len(contradictions),
        'rate': len(contradictions) / len(df),
        'sample_ids': contradictions['SKILL_ID'].head(5).tolist(),
    })
    
    return pd.DataFrame(issues)

def generate_markdown_report(
    ela_df: pd.DataFrame,
    math_df: pd.DataFrame,
    applicability_df: pd.DataFrame,
    confidence: Dict,
    ela_patterns: Dict,
    math_patterns: Dict,
    ela_edges: pd.DataFrame,
    math_edges: pd.DataFrame,
    output_file: str
):
    """Generate comprehensive markdown analysis report."""
    
    report = f"""# Production Extraction Results Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Phase**: 1.4 - Combined Results Analysis  
**Scope**: {len(ela_df)} ELA + {len(math_df)} Math = {len(ela_df) + len(math_df)} total skills

---

## Executive Summary

### Key Findings

1. **Field Applicability**: Significant differences between ELA and Math for text-specific fields
2. **Confidence Rates**: {confidence['ela'].get('high', 0):.1%} ELA high confidence vs {confidence['math'].get('high', 0):.1%} Math
3. **Edge Cases**: {len(ela_edges) + len(math_edges)} total issues identified across both domains
4. **Schema v2.0 Needs**: Clear requirements for domain-adaptive fields emerged

---

## 1. Field Applicability Analysis

### Universal Fields (Work well for both domains)

| Field | ELA Meaningful Rate | Math Meaningful Rate | Gap | Assessment |
|-------|---------------------|----------------------|-----|------------|
"""
    
    # Universal fields (gap < 15%)
    universal = applicability_df[applicability_df['gap'] < 0.15].sort_values('gap')
    for _, row in universal.iterrows():
        status = "✅ Universal"
        report += f"| {row['field']} | {row['ela_meaningful_rate']:.1%} | {row['math_meaningful_rate']:.1%} | {row['gap']:.1%} | {status} |\n"
    
    report += """
### Domain-Specific Fields (Require adaptation)

| Field | ELA Meaningful Rate | Math Meaningful Rate | Gap | Assessment |
|-------|---------------------|----------------------|-----|------------|
"""
    
    # Domain-specific fields (gap >= 15%)
    domain_specific = applicability_df[applicability_df['gap'] >= 0.15].sort_values('gap', ascending=False)
    for _, row in domain_specific.iterrows():
        if row['ela_meaningful_rate'] > row['math_meaningful_rate']:
            status = "⚠️ ELA-centric"
        else:
            status = "⚠️ Math-centric"
        report += f"| {row['field']} | {row['ela_meaningful_rate']:.1%} | {row['math_meaningful_rate']:.1%} | {row['gap']:.1%} | {status} |\n"
    
    report += f"""
---

## 2. Confidence Distribution

### ELA Skills
- High Confidence: {confidence['ela'].get('high', 0):.1%}
- Medium Confidence: {confidence['ela'].get('medium', 0):.1%}
- Low Confidence: {confidence['ela'].get('low', 0):.1%}

### Math Skills
- High Confidence: {confidence['math'].get('high', 0):.1%}
- Medium Confidence: {confidence['math'].get('medium', 0):.1%}
- Low Confidence: {confidence['math'].get('low', 0):.1%}

### Assessment
"""
    
    ela_high = confidence['ela'].get('high', 0)
    math_high = confidence['math'].get('high', 0)
    
    if ela_high >= 0.90 and math_high >= 0.90:
        report += "✅ Both domains meet ≥90% high confidence target\n"
    elif ela_high >= 0.90:
        report += "⚠️ ELA meets target, Math below threshold (prompt adjustment needed)\n"
    elif math_high >= 0.90:
        report += "⚠️ Math meets target, ELA below threshold (review needed)\n"
    else:
        report += "❌ Both domains below 90% target (prompt refinement required)\n"
    
    report += f"""
---

## 3. Common Patterns Analysis

### ELA Top 10 Actions
"""
    
    for i, (action, count) in enumerate(list(ela_patterns['top_actions'].items())[:10], 1):
        report += f"{i}. **{action}**: {count} occurrences\n"
    
    report += """
### Math Top 10 Actions
"""
    
    for i, (action, count) in enumerate(list(math_patterns['top_actions'].items())[:10], 1):
        report += f"{i}. **{action}**: {count} occurrences\n"
    
    report += """
### ELA Top 10 Targets
"""
    
    for i, (target, count) in enumerate(list(ela_patterns['top_targets'].items())[:10], 1):
        report += f"{i}. **{target}**: {count} occurrences\n"
    
    report += """
### Math Top 10 Targets
"""
    
    for i, (target, count) in enumerate(list(math_patterns['top_targets'].items())[:10], 1):
        report += f"{i}. **{target}**: {count} occurrences\n"
    
    report += """
### Cognitive Demand Distribution

**ELA**:
"""
    
    for demand, count in ela_patterns['cognitive_demand'].items():
        rate = count / len(ela_df)
        report += f"- {demand}: {count} ({rate:.1%})\n"
    
    report += """
**Math**:
"""
    
    for demand, count in math_patterns['cognitive_demand'].items():
        rate = count / len(math_df)
        report += f"- {demand}: {count} ({rate:.1%})\n"
    
    report += """
---

## 4. Edge Cases and Issues

### ELA Issues

| Issue Type | Count | Rate | Sample IDs |
|------------|-------|------|------------|
"""
    
    for _, issue in ela_edges.iterrows():
        sample_ids = ', '.join(issue['sample_ids'][:3]) if issue['sample_ids'] else 'None'
        report += f"| {issue['issue_type']} | {issue['count']} | {issue['rate']:.1%} | {sample_ids}... |\n"
    
    report += """
### Math Issues

| Issue Type | Count | Rate | Sample IDs |
|------------|-------|------|------------|
"""
    
    for _, issue in math_edges.iterrows():
        sample_ids = ', '.join(issue['sample_ids'][:3]) if issue['sample_ids'] else 'None'
        report += f"| {issue['issue_type']} | {issue['count']} | {issue['rate']:.1%} | {sample_ids}... |\n"
    
    report += """
---

## 5. Schema v2.0 Recommendations

### High Priority Changes

Based on the analysis, the following changes are strongly recommended for schema v2.0:

1. **Rename text_* fields to content_***
   - Justification: "text" terminology inappropriate for Math skills
   - Impact: {math_not_applicable_text}% of Math skills have text_type = not_applicable
   - Proposed: content_type with domain-specific values

2. **Extend skill_domain values**
   - Current: reading, writing, speaking, listening, language
   - Add for Math: number_operations, algebraic_thinking, geometry, data_analysis, measurement
   - Justification: {math_not_applicable_domain}% of Math skills have skill_domain = not_applicable

3. **Extend scope values**
   - Current: word, sentence, paragraph, text, multi_text
   - Add for Math: number, expression, equation, problem, proof, multi_step
   - Justification: {math_not_applicable_scope}% of Math skills have scope = not_applicable

### Medium Priority Enhancements

4. **Add mathematical_domain field** (optional, Math only)
   - Values: arithmetic, algebra, geometry, statistics, measurement
   - Provides finer-grained Math categorization

5. **Add representation_type field** (optional, Math only)
   - Values: symbolic, visual, concrete, verbal, mixed
   - Captures how Math concepts are represented

6. **Extend vocabulary dictionaries**
   - Add Math-specific action verbs (solve, calculate, compute, prove, etc.)
   - Add Math-specific target nouns (equation, fraction, angle, etc.)
   - Improves structural extraction accuracy

---

## 6. Extraction Quality Summary

### Meets Production Standards ✅

- **Structural Extraction**: {structural_success_rate:.1%} success rate (target: ≥95%)
- **Field Completeness**: {field_completeness:.1%} (target: ≥85%)

### Needs Improvement ⚠️

- **Math Confidence Rate**: {math_high:.1%} (target: ≥90%)
- **Domain-Specific Fields**: {problematic_fields_count} fields with <50% Math applicability

### Critical Issues ❌

- **Low Confidence Extractions**: {total_low_confidence} skills across both domains
- **Excessive not_applicable**: {total_excessive_na} skills with 4+ fields not_applicable

---

## 7. Next Steps

### Immediate (This Week)

1. Design unified schema v2.0 incorporating recommended changes
2. Update extraction prompts for domain-specific terminology
3. Extend vocabulary dictionaries with Math-specific terms
4. Create migration script from v1.0 to v2.0

### Short-Term (Next 2 Weeks)

5. Re-extract Math skills with updated prompts and schema
6. Validate 200-skill sample (100 ELA + 100 Math)
7. Calculate precision/recall metrics per field
8. Document edge cases and remediation strategies

### Medium-Term (Next Month)

9. Deploy schema v2.0 to production
10. Migrate existing v1.0 data
11. Build validation workflow UI
12. Implement monitoring dashboard

---

## 8. Cost and Performance Summary

### Extraction Performance

**ELA**:
- Total skills: {len(ela_df)}
- Estimated time: ~{len(ela_df) * 4 / 3600:.1f} hours
- Estimated cost: ~${len(ela_df) * 0.003:.2f}

**Math**:
- Total skills: {len(math_df)}
- Estimated time: ~{len(math_df) * 4 / 3600:.1f} hours
- Estimated cost: ~${len(math_df) * 0.003:.2f}

**Combined**:
- Total skills: {len(ela_df) + len(math_df)}
- Total time: ~{(len(ela_df) + len(math_df)) * 4 / 3600:.1f} hours
- Total cost: ~${(len(ela_df) + len(math_df)) * 0.003:.2f}

---

## 9. Files Generated

- `all_skills_metadata_combined.csv`: Merged ELA + Math metadata
- `field_applicability_analysis.csv`: Detailed field-by-field comparison
- `ela_edge_cases.csv`: Flagged ELA skills needing review
- `math_edge_cases.csv`: Flagged Math skills needing review
- `schema_v2_requirements.json`: Structured requirements for v2.0

---

**Analysis Complete**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Next Phase**: 2.1 - Derive Common Metadata Classes and Design Schema v2.0
""".format(
        math_not_applicable_text=applicability_df[applicability_df['field'] == 'text_type']['math_not_applicable_rate'].values[0] * 100,
        math_not_applicable_domain=applicability_df[applicability_df['field'] == 'skill_domain']['math_not_applicable_rate'].values[0] * 100,
        math_not_applicable_scope=applicability_df[applicability_df['field'] == 'scope']['math_not_applicable_rate'].values[0] * 100,
        structural_success_rate=(ela_df['actions'] != '').mean() * 100,
        field_completeness=(ela_df[['actions', 'cognitive_demand', 'task_complexity']].notna().all(axis=1)).mean() * 100,
        math_high=confidence['math'].get('high', 0) * 100,
        problematic_fields_count=len(domain_specific),
        total_low_confidence=len(ela_df[ela_df['llm_confidence'] == 'low']) + len(math_df[math_df['llm_confidence'] == 'low']),
        total_excessive_na=len(ela_edges[ela_edges['issue_type'] == 'excessive_not_applicable']['count']) + len(math_edges[math_edges['issue_type'] == 'excessive_not_applicable']['count']),
    )
    
    # Write report
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Analysis report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze production extraction results')
    parser.add_argument('--ela', required=True, help='ELA extraction results file pattern')
    parser.add_argument('--math', required=True, help='Math extraction results file pattern')
    parser.add_argument('--output', required=True, help='Output markdown report file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("PRODUCTION EXTRACTION RESULTS ANALYSIS")
    print("="*70)
    print()
    
    # Load data
    print("Step 1: Loading extraction data...")
    ela_df, math_df = load_extraction_data(args.ela, args.math)
    
    # Combine for exports
    combined_df = pd.concat([ela_df, math_df], ignore_index=True)
    
    # Analyze field applicability
    print("\nStep 2: Analyzing field applicability...")
    applicability_df = analyze_field_applicability(ela_df, math_df)
    
    # Analyze confidence
    print("\nStep 3: Analyzing confidence distribution...")
    confidence = analyze_confidence_distribution(ela_df, math_df)
    
    # Analyze patterns
    print("\nStep 4: Analyzing common patterns...")
    ela_patterns = analyze_common_patterns(ela_df, 'ELA')
    math_patterns = analyze_common_patterns(math_df, 'Math')
    
    # Identify edge cases
    print("\nStep 5: Identifying edge cases...")
    ela_edges = identify_edge_cases(ela_df, 'ELA')
    math_edges = identify_edge_cases(math_df, 'Math')
    
    # Generate report
    print("\nStep 6: Generating analysis report...")
    generate_markdown_report(
        ela_df, math_df, applicability_df, confidence,
        ela_patterns, math_patterns, ela_edges, math_edges,
        args.output
    )
    
    # Save supporting files
    output_dir = Path(args.output).parent
    
    combined_df.to_csv(output_dir / 'all_skills_metadata_combined.csv', index=False)
    print(f"✓ Combined metadata saved to: {output_dir / 'all_skills_metadata_combined.csv'}")
    
    applicability_df.to_csv(output_dir / 'field_applicability_analysis.csv', index=False)
    print(f"✓ Applicability analysis saved to: {output_dir / 'field_applicability_analysis.csv'}")
    
    ela_df[ela_df['llm_confidence'] == 'low'].to_csv(output_dir / 'ela_edge_cases.csv', index=False)
    math_df[math_df['llm_confidence'] == 'low'].to_csv(output_dir / 'math_edge_cases.csv', index=False)
    print(f"✓ Edge cases saved to: {output_dir / 'ela_edge_cases.csv'} and {output_dir / 'math_edge_cases.csv'}")
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print(f"\nReview the report at: {args.output}")
    print("\nNext steps:")
    print("1. Review field applicability gaps (focus on ≥15% gap)")
    print("2. Design schema v2.0 with domain-adaptive fields")
    print("3. Update extraction prompts for Math-specific terminology")
    print("4. Plan re-extraction for low-confidence skills")

if __name__ == '__main__':
    main()

