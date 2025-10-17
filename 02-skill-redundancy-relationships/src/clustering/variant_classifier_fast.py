#!/usr/bin/env python3
"""
Fast Variant Classifier for ROCK Skills (Demo-Optimized)

Uses the existing LLM mappings to identify variants by taxonomy grouping.
Much faster than pairwise comparison - leverages work already done.

Generates: analysis/outputs/variant-classification-report.csv
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import sys

# Configuration
MIN_GROUP_SIZE = 2
GRADE_ORDER = ['Pre-K', 'PK', 'K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']


def load_data(base_path: Path):
    """Load necessary data files."""
    print("\n📂 Loading data...")
    
    # Load LLM mappings (skills already grouped by taxonomy)
    mappings_path = base_path / 'analysis' / 'llm_skill_mappings.csv'
    if not mappings_path.exists():
        print(f"❌ Error: LLM mappings not found at {mappings_path}")
        sys.exit(1)
    
    mappings_df = pd.read_csv(mappings_path)
    print(f"  ✅ Loaded {len(mappings_df):,} mapped skills")
    
    # Load full skills for unmapped ones
    skills_path = base_path / 'rock_schemas' / 'SKILLS.csv'
    skills_df = pd.read_csv(skills_path, low_memory=False)
    ela_skills = skills_df[skills_df['CONTENT_AREA_NAME'] == 'English Language Arts'].copy()
    print(f"  ✅ Loaded {len(ela_skills):,} total ELA skills")
    
    # Get authority info
    standard_skills_path = base_path / 'rock_schemas' / 'STANDARD_SKILLS.csv'
    standard_skills_df = pd.read_csv(standard_skills_path, low_memory=False)
    
    standards_path = base_path / 'rock_schemas' / 'STANDARDS.csv'
    standards_df = pd.read_csv(standards_path, low_memory=False)
    
    # Merge to get authority
    with_authority = ela_skills.merge(
        standard_skills_df[['SKILL_ID', 'STANDARD_ID']], 
        on='SKILL_ID', 
        how='left'
    ).merge(
        standards_df[['STANDARD_ID', 'STANDARD_SET_AUTHORITY_NAME', 'STANDARD_SET_NAME']], 
        on='STANDARD_ID', 
        how='left'
    ).rename(columns={'STANDARD_SET_AUTHORITY_NAME': 'AUTHORITY'})
    
    with_authority = with_authority.drop_duplicates(subset=['SKILL_ID'])
    with_authority['AUTHORITY'] = with_authority['AUTHORITY'].fillna('Unknown')
    
    return mappings_df, with_authority


def identify_state_variants_from_taxonomy(mappings_df: pd.DataFrame, skills_df: pd.DataFrame) -> dict:
    """
    Identify State A (cross-state variants) using taxonomy groupings.
    Skills mapped to the same taxonomy node from different authorities are variants.
    """
    print("\n🔍 Identifying State A (Cross-State Variants) via Taxonomy...")
    
    # Merge authority info into mappings
    mappings_with_auth = mappings_df.merge(
        skills_df[['SKILL_ID', 'AUTHORITY']], 
        on='SKILL_ID', 
        how='left'
    )
    
    state_groups = {}
    group_id = 1
    
    # Group by taxonomy path and grade level
    for taxonomy_path, group in mappings_with_auth.groupby('TAXONOMY_PATH'):
        for grade, grade_group in group.groupby('GRADE_LEVEL_NAME'):
            # Check if multiple authorities present
            authorities = grade_group['AUTHORITY'].dropna().nunique()
            
            if len(grade_group) >= MIN_GROUP_SIZE and authorities > 1:
                # This is a cross-state variant group
                for skill_id in grade_group['SKILL_ID']:
                    state_groups[skill_id] = f"SA-{group_id:04d}"
                group_id += 1
                if group_id % 10 == 0:
                    print(f"  Found {group_id} State A groups...")
    
    print(f"✅ Identified {group_id-1} State A groups with {len(state_groups)} skills")
    return state_groups


def identify_grade_progressions_from_taxonomy(mappings_df: pd.DataFrame) -> dict:
    """
    Identify State B (grade progressions) using taxonomy groupings.
    Skills mapped to the same taxonomy node across different grades are progressions.
    """
    print("\n🔍 Identifying State B (Grade Progressions) via Taxonomy...")
    
    grade_chains = {}
    chain_id = 1
    
    # Group by taxonomy path
    for taxonomy_path, group in mappings_df.groupby('TAXONOMY_PATH'):
        # Check if spans multiple grades
        unique_grades = group['GRADE_LEVEL_SHORT_NAME'].nunique()
        
        if len(group) >= MIN_GROUP_SIZE and unique_grades >= MIN_GROUP_SIZE:
            # Sort by grade level
            sorted_group = group.copy()
            sorted_group['grade_order'] = sorted_group['GRADE_LEVEL_SHORT_NAME'].apply(
                lambda x: GRADE_ORDER.index(x) if x in GRADE_ORDER else 999
            )
            sorted_group = sorted_group.sort_values('grade_order')
            
            # Assign complexity levels
            for idx, (_, row) in enumerate(sorted_group.iterrows()):
                grade_chains[row['SKILL_ID']] = (f"SB-{chain_id:04d}", idx + 1)
            
            chain_id += 1
            if chain_id % 10 == 0:
                print(f"  Found {chain_id} State B chains...")
    
    print(f"✅ Identified {chain_id-1} State B chains with {len(grade_chains)} skills")
    return grade_chains


def generate_classification_report(skills_df: pd.DataFrame, 
                                   mappings_df: pd.DataFrame,
                                   state_groups: dict, 
                                   grade_chains: dict,
                                   output_path: Path):
    """Generate comprehensive variant classification report."""
    print("\n📊 Generating classification report...")
    
    results = []
    
    # Get authority info for mapped skills
    mapped_with_info = mappings_df.copy()
    
    for _, skill in skills_df.iterrows():
        skill_id = skill['SKILL_ID']
        
        # Determine classification
        if skill_id in state_groups:
            equivalence_type = 'state-variant'
            group_id = state_groups[skill_id]
            complexity = None
        elif skill_id in grade_chains:
            equivalence_type = 'grade-progression'
            group_id, complexity = grade_chains[skill_id]
        else:
            equivalence_type = 'unique'
            group_id = None
            complexity = None
        
        results.append({
            'SKILL_ID': skill_id,
            'SKILL_NAME': skill['SKILL_NAME'],
            'GRADE_LEVEL_NAME': skill['GRADE_LEVEL_NAME'],
            'GRADE_LEVEL_SHORT_NAME': skill['GRADE_LEVEL_SHORT_NAME'],
            'SKILL_AREA_NAME': skill['SKILL_AREA_NAME'],
            'CONTENT_AREA_NAME': skill['CONTENT_AREA_NAME'],
            'AUTHORITY': skill.get('AUTHORITY', 'Unknown'),
            'EQUIVALENCE_TYPE': equivalence_type,
            'EQUIVALENCE_GROUP_ID': group_id,
            'COMPLEXITY_LEVEL': complexity
        })
    
    # Create DataFrame and save
    report_df = pd.DataFrame(results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_csv(output_path, index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 CLASSIFICATION SUMMARY")
    print("="*60)
    
    total = len(report_df)
    state_a = len(report_df[report_df['EQUIVALENCE_TYPE'] == 'state-variant'])
    state_b = len(report_df[report_df['EQUIVALENCE_TYPE'] == 'grade-progression'])
    unique = len(report_df[report_df['EQUIVALENCE_TYPE'] == 'unique'])
    
    print(f"Total Skills Analyzed:    {total:,}")
    print(f"")
    print(f"State A (Cross-State):    {state_a:,} ({state_a/total*100:.1f}%)")
    print(f"State B (Progressions):   {state_b:,} ({state_b/total*100:.1f}%)")
    print(f"Unique Skills:            {unique:,} ({unique/total*100:.1f}%)")
    print(f"")
    
    state_a_groups = report_df[report_df['EQUIVALENCE_TYPE'] == 'state-variant']['EQUIVALENCE_GROUP_ID'].nunique()
    state_b_chains = report_df[report_df['EQUIVALENCE_TYPE'] == 'grade-progression']['EQUIVALENCE_GROUP_ID'].nunique()
    
    if state_a_groups > 0:
        print(f"State A Groups:           {state_a_groups:,} (avg {state_a/state_a_groups:.1f} skills/group)")
    if state_b_chains > 0:
        print(f"State B Chains:           {state_b_chains:,} (avg {state_b/state_b_chains:.1f} skills/chain)")
    print("="*60)
    print(f"\n✅ Report saved to: {output_path}")
    
    return report_df


def main():
    """Main execution."""
    print("="*60)
    print("🔗 ROCK Skills Variant Classifier (Fast)")
    print("="*60)
    print("\n💡 Using taxonomy-based grouping (much faster!)")
    
    # Paths
    base_path = Path(__file__).parent.parent
    output_path = base_path / 'analysis' / 'outputs' / 'variant-classification-report.csv'
    
    # Load data
    mappings_df, skills_df = load_data(base_path)
    
    # Classify variants using taxonomy groupings
    state_groups = identify_state_variants_from_taxonomy(mappings_df, skills_df)
    grade_chains = identify_grade_progressions_from_taxonomy(mappings_df)
    
    # Generate report for ALL skills (including unmapped ones as "unique")
    report_df = generate_classification_report(
        skills_df, 
        mappings_df,
        state_groups, 
        grade_chains, 
        output_path
    )
    
    print("\n🎉 Classification complete!")
    print(f"\n💡 Next steps:")
    print(f"   1. Refresh Streamlit: pkill -f streamlit && cd poc && python3 -m streamlit run skill_bridge_app.py")
    print(f"   2. Navigate to '🔗 Variant Analysis' page")
    print(f"   3. Explore State A/B relationships!")


if __name__ == '__main__':
    main()

