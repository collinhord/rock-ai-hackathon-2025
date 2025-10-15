#!/usr/bin/env python3
"""
Taxonomy Gap Report Generator

Generates comprehensive markdown report analyzing mapping results and taxonomy gaps.
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.taxonomy_gap_detector import TaxonomyGapDetector


def generate_executive_summary(summary_stats: dict) -> str:
    """Generate executive summary section."""
    total = summary_stats['total_skills_mapped']
    gaps = summary_stats['gap_candidates']
    gap_pct = summary_stats['gap_percentage']
    
    conf_dist = summary_stats['confidence_distribution']
    high = conf_dist.get('High', 0)
    medium = conf_dist.get('Medium', 0)
    low = conf_dist.get('Low', 0)
    
    text = f"""# Taxonomy Gap Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Executive Summary

### Mapping Results
- **Total Skills Mapped**: {total}
- **High Confidence**: {high} ({high/total*100:.1f}%)
- **Medium Confidence**: {medium} ({medium/total*100:.1f}%)
- **Low Confidence**: {low} ({low/total*100:.1f}%)

### Gap Analysis
- **Gap Candidates**: {gaps} skills ({gap_pct:.1f}%)
- **Taxonomy Extensions Suggested**: {summary_stats['suggested_extensions']}
- **High Priority Gaps**: {len(summary_stats['high_priority_suggestions'])} ({len(summary_stats['high_priority_suggestions'])/gaps*100 if gaps > 0 else 0:.1f}% of gaps)

### Success Rate
{"✅ **Excellent**: >80% high/medium confidence" if (high+medium)/total > 0.8 else ""}
{"⚠️ **Good**: 70-80% high/medium confidence" if 0.7 < (high+medium)/total <= 0.8 else ""}
{"❌ **Needs Improvement**: <70% high/medium confidence" if (high+medium)/total <= 0.7 else ""}

**Recommendation**: {"Proceed with scaling to larger batches" if (high+medium)/total > 0.75 else "Refine prompts and retry validation batch"}

---
"""
    return text


def generate_high_confidence_section(mappings_df: pd.DataFrame) -> str:
    """Generate section showcasing successful mappings."""
    high_conf = mappings_df[mappings_df['confidence'] == 'High'].copy()
    
    if len(high_conf) == 0:
        return "## High-Confidence Mappings\n\n*No high-confidence mappings found.*\n\n---\n\n"
    
    # Sort by semantic similarity
    high_conf = high_conf.sort_values('semantic_similarity', ascending=False)
    
    text = f"""## High-Confidence Mappings

Successfully mapped {len(high_conf)} skills with high confidence. These demonstrate the system working as intended.

### Top 5 Examples

"""
    
    for i, (_, row) in enumerate(high_conf.head(5).iterrows(), 1):
        sim = row.get('semantic_similarity', 0)
        text += f"""#### {i}. {row['skill_name']}
- **Grade**: {row.get('grade_level', 'N/A')}
- **Taxonomy**: `{row['taxonomy_path']}`
- **Semantic Similarity**: {sim:.3f}
- **Rationale**: {row.get('rationale', 'N/A')[:200]}...

"""
    
    text += "---\n\n"
    return text


def generate_low_confidence_section(gap_candidates_df: pd.DataFrame) -> str:
    """Generate section for skills needing review."""
    if len(gap_candidates_df) == 0:
        return "## Low-Confidence Mappings\n\n*No low-confidence mappings found. All skills mapped successfully!*\n\n---\n\n"
    
    # Sort by semantic similarity (lowest first = most problematic)
    gap_candidates_df = gap_candidates_df.sort_values('semantic_similarity')
    
    text = f"""## Low-Confidence Mappings

{len(gap_candidates_df)} skills require human review due to low confidence or poor semantic match.

### Review Queue (Top 10 Most Problematic)

"""
    
    for i, (_, row) in enumerate(gap_candidates_df.head(10).iterrows(), 1):
        sim = row.get('semantic_similarity', 0)
        conf = row.get('confidence', 'Unknown')
        rationale = row.get('rationale', 'N/A')
        if pd.isna(rationale):
            rationale = 'N/A'
        text += f"""#### {i}. {row['skill_name']}
- **Grade**: {row.get('grade_level', 'N/A')}
- **Best Match**: `{row.get('taxonomy_path', 'N/A')}`
- **Confidence**: {conf}
- **Semantic Similarity**: {sim:.3f}
- **Issue**: {str(rationale)[:150]}...
- **Action**: {"Manual review required" if conf == 'Low' else "Verify mapping accuracy"}

"""
    
    if len(gap_candidates_df) > 10:
        text += f"\n*...and {len(gap_candidates_df) - 10} more skills in review queue.*\n"
    
    text += "\n---\n\n"
    return text


def generate_gap_categories_section(categories: dict) -> str:
    """Generate section analyzing gap types."""
    if not categories or all(len(v) == 0 for v in categories.values()):
        return "## Identified Gaps by Category\n\n*No clear gap patterns identified.*\n\n---\n\n"
    
    text = """## Identified Gaps by Category

Skills that don't map well to the Science of Reading taxonomy, grouped by theme.

"""
    
    # Sort categories by count
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for gap_type, skills in sorted_categories:
        if len(skills) == 0:
            continue
        
        category_names = {
            'digital-literacy': 'Digital Literacy',
            'social-emotional': 'Social-Emotional Learning (SEL)',
            'metacognition': 'Metacognitive Strategies',
            'writing-conventions': 'Writing Conventions',
            'assessment-only': 'Assessment Procedures',
            'unknown': 'Uncategorized'
        }
        
        category_name = category_names.get(gap_type, gap_type.replace('-', ' ').title())
        
        text += f"""### {category_name}
**Count**: {len(skills)} skills

**Example Skills**:
"""
        for skill in skills[:5]:
            text += f"- {skill['skill_name']} ({skill.get('grade_level', 'N/A')})\n"
        
        if len(skills) > 5:
            text += f"\n*...and {len(skills) - 5} more.*\n"
        
        text += "\n"
    
    text += "---\n\n"
    return text


def generate_taxonomy_extensions_section(suggestions: list) -> str:
    """Generate section with suggested taxonomy extensions."""
    if not suggestions or len(suggestions) == 0:
        return "## Suggested Taxonomy Extensions\n\n*No taxonomy extensions suggested.*\n\n---\n\n"
    
    text = """## Suggested Taxonomy Extensions

Based on gap analysis, the following taxonomy extensions could improve coverage:

"""
    
    # Sort by skill count (highest impact first)
    sorted_suggestions = sorted(suggestions, key=lambda x: x.get('skill_count', 0), reverse=True)
    
    for i, sug in enumerate(sorted_suggestions, 1):
        priority = "🔴 HIGH" if sug.get('skill_count', 0) >= 5 else ("🟡 MEDIUM" if sug.get('skill_count', 0) >= 3 else "🟢 LOW")
        
        text += f"""### {i}. {sug['proposed_node']}
**Priority**: {priority} ({sug.get('skill_count', 0)} skills affected)

**Parent Location**: {sug.get('parent_pillar', 'TBD')}

**Justification**: {sug.get('justification', 'N/A')}

**Example Skills**:
"""
        for skill_name in sug.get('example_skills', []):
            text += f"- {skill_name}\n"
        
        if 'sub_nodes' in sug:
            text += f"\n**Potential Sub-Nodes**: {', '.join(sug['sub_nodes'])}\n"
        
        text += "\n"
    
    text += "---\n\n"
    return text


def generate_recommendations_section(summary_stats: dict, gap_candidates_df: pd.DataFrame) -> str:
    """Generate actionable recommendations."""
    total = summary_stats['total_skills_mapped']
    high_medium_rate = (summary_stats['confidence_distribution'].get('High', 0) + summary_stats['confidence_distribution'].get('Medium', 0)) / total
    gaps = len(gap_candidates_df)
    
    text = """## Recommendations for Manual Review

### Immediate Actions

"""
    
    # Prioritized recommendations based on results
    if high_medium_rate >= 0.80:
        text += """1. ✅ **System Validation**: Excellent performance (>80% high/medium confidence)
   - Review the {gaps} skills in the review queue
   - Validate 10-15 random high-confidence mappings for spot-checking
   - Proceed with scaling to 200-500 skill batches

""".format(gaps=gaps)
    elif high_medium_rate >= 0.70:
        text += """1. ⚠️ **Prompt Refinement Needed**: Good but improvable (70-80% high/medium confidence)
   - Analyze patterns in low-confidence mappings
   - Refine LLM prompts based on common failure modes
   - Add more specific guidance for ambiguous skill types
   - Re-run validation batch after refinements

"""
    else:
        text += """1. ❌ **Major Issues Detected**: Low success rate (<70% high/medium confidence)
   - Do NOT scale until issues are resolved
   - Deep analysis of why mappings are failing
   - Consider: Is the taxonomy appropriate for ROCK skills?
   - May need taxonomy restructuring or different mapping approach

"""
    
    # Grade distribution analysis
    if 'grade_distribution_of_gaps' in summary_stats and summary_stats['grade_distribution_of_gaps']:
        grade_dist = summary_stats['grade_distribution_of_gaps']
        top_grades = list(grade_dist.keys())[:3]
        if len(top_grades) > 0:
            text += f"""2. 🎯 **Grade-Level Focus**: Gaps concentrated in {', '.join(top_grades)}
   - Investigate why these grade levels have mapping challenges
   - May need grade-specific taxonomy nodes
   - Review developmental appropriateness of taxonomy for these grades

"""
    
    # Gap categories
    if summary_stats.get('high_priority_suggestions'):
        text += f"""3. 📋 **Taxonomy Extensions**: {len(summary_stats['high_priority_suggestions'])} high-priority gaps identified
   - Review suggested taxonomy extensions
   - Consult with literacy experts on gap validity
   - Decide: Accept gaps as "out of scope" or extend taxonomy?

"""
    
    text += """### Review Workflow

1. **High-Confidence Validation** (10% sample)
   - Randomly select 10% of high-confidence mappings
   - Expert review for accuracy
   - Calculate precision rate

2. **Review Queue Resolution** (100% review)
   - Process all low-confidence mappings
   - Correct or confirm each mapping
   - Document patterns in errors

3. **Gap Classification** (Expert judgment)
   - Review each gap category
   - Determine: True gap vs. mapping error vs. out-of-scope skill
   - Make taxonomy extension recommendations

### Success Metrics for Next Iteration

- Target: >85% high/medium confidence
- Target: <5% needs review
- Target: Clear categories for remaining gaps

---
"""
    
    return text


def generate_report(
    mappings_file: Path,
    output_file: Path
):
    """
    Generate comprehensive gap report.
    
    Args:
        mappings_file: Path to LLM mappings CSV
        output_file: Path for output markdown report
    """
    print(f"Generating gap report from: {mappings_file}")
    
    # Load mappings
    mappings_df = pd.read_csv(mappings_file)
    print(f"Loaded {len(mappings_df)} skill mappings")
    
    # Initialize detector
    detector = TaxonomyGapDetector()
    
    # Analyze gaps
    print("Analyzing unmappable skills...")
    gap_candidates = detector.analyze_unmappable_skills(mappings_df)
    
    print("Categorizing gaps...")
    categories = detector.categorize_gaps(gap_candidates)
    
    # Cluster for patterns
    print("Clustering gap patterns...")
    all_gap_skills = []
    for cat_skills in categories.values():
        all_gap_skills.extend(cat_skills)
    
    clusters = detector.cluster_gap_patterns(all_gap_skills) if all_gap_skills else {}
    
    print("Suggesting taxonomy extensions...")
    suggestions = detector.suggest_taxonomy_extensions(categories, clusters)
    
    print("Generating summary statistics...")
    summary_stats = detector.generate_gap_summary(mappings_df, gap_candidates, categories, suggestions)
    
    # Generate report sections
    print("Writing report...")
    report = ""
    report += generate_executive_summary(summary_stats)
    report += generate_high_confidence_section(mappings_df)
    report += generate_low_confidence_section(gap_candidates)
    report += generate_gap_categories_section(categories)
    report += generate_taxonomy_extensions_section(suggestions)
    report += generate_recommendations_section(summary_stats, gap_candidates)
    
    # Write report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report)
    
    print(f"\n✓ Report generated: {output_file}")
    print(f"  Total skills: {len(mappings_df)}")
    print(f"  Gap candidates: {len(gap_candidates)}")
    print(f"  Suggested extensions: {len(suggestions)}")


def main():
    parser = argparse.ArgumentParser(description='Generate taxonomy gap report from LLM mappings')
    parser.add_argument('--mappings', required=True, help='Path to LLM mappings CSV file')
    parser.add_argument('--output', required=True, help='Path for output markdown report')
    
    args = parser.parse_args()
    
    mappings_file = Path(args.mappings)
    output_file = Path(args.output)
    
    if not mappings_file.exists():
        print(f"Error: Mappings file not found: {mappings_file}")
        return 1
    
    generate_report(mappings_file, output_file)
    return 0


if __name__ == '__main__':
    exit(main())

