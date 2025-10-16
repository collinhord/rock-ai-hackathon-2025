#!/usr/bin/env python3
"""
Variant Classifier for ROCK Skills

Analyzes ROCK skills to identify:
- State A (cross-state variants): Same skill across different states
- State B (grade progressions): Same skill progressing through grades
- Unique skills: No detected variants

Generates: analysis/outputs/variant-classification-report.csv
"""

import pandas as pd
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher
import re
from collections import defaultdict
import sys

# Configuration
SIMILARITY_THRESHOLD = 0.75  # For name matching
MIN_GROUP_SIZE = 2  # Minimum skills per variant group
GRADE_ORDER = ['Pre-K', 'PK', 'K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']


def normalize_skill_name(name: str) -> str:
    """Normalize skill names for comparison."""
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common state-specific markers
    name = re.sub(r'\(.*?(texas|california|virginia|florida|ohio|ccss).*?\)', '', name, flags=re.IGNORECASE)
    
    # Remove grade references for cross-state comparison
    name = re.sub(r'\bgr(ade)?\.?\s*[pk\d-]+\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(pre-)?k(indergarten)?\b', '', name, flags=re.IGNORECASE)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name.strip()


def text_similarity(a: str, b: str) -> float:
    """Calculate text similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()


def calculate_complexity_level(grade_level_name: str) -> int:
    """
    Map grade level to complexity level for progression chains.
    
    Args:
        grade_level_name: Grade level name (e.g., "Pre-K", "Grade 1", "12")
        
    Returns:
        Complexity level (0-14)
    """
    grade_map = {
        'Pre-K': 0, 'PK': 0,
        'Kindergarten': 1, 'K': 1,
        'Grade 1': 2, '1': 2,
        'Grade 2': 3, '2': 3,
        'Grade 3': 4, '3': 4,
        'Grade 4': 5, '4': 5,
        'Grade 5': 6, '5': 6,
        'Grade 6': 7, '6': 7,
        'Grade 7': 8, '7': 8,
        'Grade 8': 9, '8': 9,
        'Grade 9': 10, '9': 10,
        'Grade 10': 11, '10': 11,
        'Grade 11': 12, '11': 12,
        'Grade 12': 13, '12': 13
    }
    return grade_map.get(str(grade_level_name).strip(), 0)


def load_skills_from_csv(base_path: Path) -> pd.DataFrame:
    """Load ROCK skills from CSV files."""
    # Load skills
    skills_path = base_path / 'rock_schemas' / 'SKILLS.csv'
    skills_df = pd.read_csv(skills_path, low_memory=False)
    
    # Load standard skills for linking
    standard_skills_path = base_path / 'rock_schemas' / 'STANDARD_SKILLS.csv'
    standard_skills_df = pd.read_csv(standard_skills_path, low_memory=False)
    
    # Load standards (has authority info embedded)
    standards_path = base_path / 'rock_schemas' / 'STANDARDS.csv'
    standards_df = pd.read_csv(standards_path, low_memory=False)
    
    # Merge to get authority information from standards
    merged = skills_df.merge(
        standard_skills_df[['SKILL_ID', 'STANDARD_ID']], 
        on='SKILL_ID', 
        how='left'
    )
    
    merged = merged.merge(
        standards_df[['STANDARD_ID', 'STANDARD_SET_AUTHORITY_NAME', 'STANDARD_SET_NAME']], 
        on='STANDARD_ID', 
        how='left'
    )
    
    # Rename for consistency
    merged = merged.rename(columns={'STANDARD_SET_AUTHORITY_NAME': 'AUTHORITY'})
    
    # Filter ELA skills only
    ela_skills = merged[merged['CONTENT_AREA_NAME'] == 'English Language Arts'].copy()
    
    # Drop duplicates (skills may link to multiple standards)
    ela_skills = ela_skills.drop_duplicates(subset=['SKILL_ID'])
    
    # Fill missing authorities with a default value
    ela_skills['AUTHORITY'] = ela_skills['AUTHORITY'].fillna('Unknown')
    
    return ela_skills


def identify_state_variants(skills_df: pd.DataFrame) -> dict:
    """Identify cross-state variants (State A)."""
    print("\n🔍 Identifying State A (Cross-State Variants)...")
    
    # Group by normalized name
    normalized = skills_df.copy()
    normalized['NORMALIZED_NAME'] = normalized['SKILL_NAME'].apply(normalize_skill_name)
    
    # Filter out empty normalized names
    normalized = normalized[normalized['NORMALIZED_NAME'].str.len() > 10]
    
    state_groups = defaultdict(list)
    group_id = 1
    processed = set()
    
    # Group similar skills across different authorities
    for idx1, skill1 in normalized.iterrows():
        if skill1['SKILL_ID'] in processed:
            continue
        
        group = [skill1['SKILL_ID']]
        processed.add(skill1['SKILL_ID'])
        
        # Find similar skills from different states
        for idx2, skill2 in normalized.iterrows():
            if skill2['SKILL_ID'] in processed:
                continue
            
            # Must be same grade level and different authority
            if (skill1['GRADE_LEVEL_NAME'] == skill2['GRADE_LEVEL_NAME'] and 
                skill1['AUTHORITY'] != skill2['AUTHORITY']):
                
                similarity = text_similarity(
                    skill1['NORMALIZED_NAME'],
                    skill2['NORMALIZED_NAME']
                )
                
                if similarity >= SIMILARITY_THRESHOLD:
                    group.append(skill2['SKILL_ID'])
                    processed.add(skill2['SKILL_ID'])
        
        # Only keep groups with multiple skills
        if len(group) >= MIN_GROUP_SIZE:
            for skill_id in group:
                state_groups[skill_id] = f"SA-{group_id:04d}"
            group_id += 1
            print(f"  Found State A group {group_id-1}: {len(group)} skills")
    
    print(f"✅ Identified {group_id-1} State A groups with {len(state_groups)} skills")
    return dict(state_groups)


def identify_grade_progressions(skills_df: pd.DataFrame) -> tuple:
    """
    Identify grade progressions (State B).
    
    Returns:
        Tuple of (grade_chains dict, progression_metadata dict)
        - grade_chains: {skill_id: (chain_id, complexity_level)}
        - progression_metadata: {skill_id: {'prerequisite_skill_id': str, 'is_spiral': bool}}
    """
    print("\n🔍 Identifying State B (Grade Progressions)...")
    
    normalized = skills_df.copy()
    normalized['NORMALIZED_NAME'] = normalized['SKILL_NAME'].apply(normalize_skill_name)
    normalized = normalized[normalized['NORMALIZED_NAME'].str.len() > 10]
    
    grade_chains = {}
    progression_metadata = {}
    chain_id = 1
    processed = set()
    chain_details = []  # Store full chain information
    
    # Group by authority and similar names across grades
    for authority in normalized['AUTHORITY'].unique():
        authority_skills = normalized[normalized['AUTHORITY'] == authority]
        
        for idx1, skill1 in authority_skills.iterrows():
            if skill1['SKILL_ID'] in processed:
                continue
            
            chain = [(skill1['SKILL_ID'], skill1['GRADE_LEVEL_NAME'], skill1['GRADE_LEVEL_SHORT_NAME'])]
            processed.add(skill1['SKILL_ID'])
            
            # Find similar skills from different grades (same authority)
            for idx2, skill2 in authority_skills.iterrows():
                if skill2['SKILL_ID'] in processed:
                    continue
                
                # Must be different grade, same authority
                if skill1['GRADE_LEVEL_NAME'] != skill2['GRADE_LEVEL_NAME']:
                    similarity = text_similarity(
                        skill1['NORMALIZED_NAME'],
                        skill2['NORMALIZED_NAME']
                    )
                    
                    if similarity >= SIMILARITY_THRESHOLD:
                        chain.append((skill2['SKILL_ID'], skill2['GRADE_LEVEL_NAME'], skill2['GRADE_LEVEL_SHORT_NAME']))
                        processed.add(skill2['SKILL_ID'])
            
            # Only keep chains with progression across grades
            if len(chain) >= MIN_GROUP_SIZE:
                # Sort by grade level (using short name for ordering)
                chain.sort(key=lambda x: GRADE_ORDER.index(x[2]) if x[2] in GRADE_ORDER else 999)
                
                current_chain_id = f"SB-{chain_id:04d}"
                
                # Store chain details for progression chains summary
                chain_details.append({
                    'chain_id': current_chain_id,
                    'skills': chain,
                    'length': len(chain),
                    'authority': authority
                })
                
                # Assign complexity levels and prerequisite relationships
                for idx, (skill_id, grade_level_name, _) in enumerate(chain):
                    complexity = calculate_complexity_level(grade_level_name)
                    grade_chains[skill_id] = (current_chain_id, complexity)
                    
                    # Track prerequisite (previous skill in chain)
                    prerequisite_id = chain[idx-1][0] if idx > 0 else None
                    
                    progression_metadata[skill_id] = {
                        'prerequisite_skill_id': prerequisite_id,
                        'is_spiral_skill': True
                    }
                
                chain_id += 1
                print(f"  Found State B chain {chain_id-1}: {len(chain)} grades")
    
    print(f"✅ Identified {chain_id-1} State B chains with {len(grade_chains)} skills")
    return grade_chains, progression_metadata, chain_details


def generate_classification_report(skills_df: pd.DataFrame, 
                                   state_groups: dict, 
                                   grade_chains: dict,
                                   progression_metadata: dict,
                                   output_path: Path):
    """Generate comprehensive variant classification report."""
    print("\n📊 Generating classification report...")
    
    results = []
    
    for _, skill in skills_df.iterrows():
        skill_id = skill['SKILL_ID']
        
        # Determine classification
        if skill_id in state_groups:
            equivalence_type = 'state-variant'
            group_id = state_groups[skill_id]
            complexity = calculate_complexity_level(skill['GRADE_LEVEL_NAME'])
            prerequisite = None
            is_spiral = False
        elif skill_id in grade_chains:
            equivalence_type = 'grade-progression'
            group_id, complexity = grade_chains[skill_id]
            prerequisite = progression_metadata.get(skill_id, {}).get('prerequisite_skill_id')
            is_spiral = progression_metadata.get(skill_id, {}).get('is_spiral_skill', False)
        else:
            equivalence_type = 'unique'
            group_id = None
            complexity = calculate_complexity_level(skill['GRADE_LEVEL_NAME'])
            prerequisite = None
            is_spiral = False
        
        results.append({
            'SKILL_ID': skill_id,
            'SKILL_NAME': skill['SKILL_NAME'],
            'GRADE_LEVEL_NAME': skill['GRADE_LEVEL_NAME'],
            'GRADE_LEVEL_SHORT_NAME': skill['GRADE_LEVEL_SHORT_NAME'],
            'SKILL_AREA_NAME': skill['SKILL_AREA_NAME'],
            'CONTENT_AREA_NAME': skill['CONTENT_AREA_NAME'],
            'AUTHORITY': skill['AUTHORITY'],
            'EQUIVALENCE_TYPE': equivalence_type,
            'EQUIVALENCE_GROUP_ID': group_id,
            'COMPLEXITY_LEVEL': complexity,
            'PREREQUISITE_SKILL_ID': prerequisite,
            'IS_SPIRAL_SKILL': is_spiral
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
    
    print(f"State A Groups:           {state_a_groups:,} (avg {state_a/state_a_groups:.1f} skills/group)")
    print(f"State B Chains:           {state_b_chains:,} (avg {state_b/state_b_chains:.1f} skills/chain)")
    print("="*60)
    print(f"\n✅ Report saved to: {output_path}")
    
    return report_df


def generate_progression_chains_summary(chain_details: list, skills_df: pd.DataFrame, output_path: Path):
    """Generate summary of progression chains for analysis."""
    print("\n📊 Generating progression chains summary...")
    
    summary_results = []
    
    for chain_info in chain_details:
        chain_id = chain_info['chain_id']
        skills = chain_info['skills']
        
        # Extract concept name from first skill (most basic form)
        first_skill_id = skills[0][0]
        first_skill = skills_df[skills_df['SKILL_ID'] == first_skill_id].iloc[0]
        concept_name = normalize_skill_name(first_skill['SKILL_NAME'])
        
        # Get grade range
        grades = [s[2] for s in skills]
        grade_range = f"{grades[0]}-{grades[-1]}"
        
        summary_results.append({
            'CHAIN_ID': chain_id,
            'CONCEPT_NAME': concept_name[:100],  # Truncate long names
            'CHAIN_LENGTH': len(skills),
            'GRADE_RANGE': grade_range,
            'AUTHORITY': chain_info['authority'],
            'EXAMPLE_SKILL_ID': first_skill_id,
            'EXAMPLE_SKILL_NAME': first_skill['SKILL_NAME'][:150]
        })
    
    # Create DataFrame and save
    summary_df = pd.DataFrame(summary_results)
    summary_df = summary_df.sort_values('CHAIN_LENGTH', ascending=False)
    summary_df.to_csv(output_path, index=False)
    
    print(f"✅ Progression chains summary saved to: {output_path}")
    print(f"   Total chains: {len(summary_df)}")
    print(f"   Longest chain: {summary_df['CHAIN_LENGTH'].max()} grades")
    print(f"   Avg chain length: {summary_df['CHAIN_LENGTH'].mean():.1f} grades")
    
    return summary_df


def main():
    """Main execution."""
    print("="*60)
    print("🔗 ROCK Skills Variant Classifier")
    print("="*60)
    
    # Paths
    base_path = Path(__file__).parent.parent
    output_path = base_path / 'analysis' / 'outputs' / 'variant-classification-report.csv'
    chains_summary_path = base_path / 'analysis' / 'outputs' / 'progression-chains-summary.csv'
    
    # Check CSV files
    skills_csv = base_path / 'rock_schemas' / 'SKILLS.csv'
    if not skills_csv.exists():
        print(f"❌ Error: SKILLS.csv not found at {skills_csv}")
        print(f"   Expected location: {skills_csv.absolute()}")
        sys.exit(1)
    
    print(f"\n📂 Loading ROCK skills from CSV files...")
    
    # Load skills
    skills_df = load_skills_from_csv(base_path)
    print(f"✅ Loaded {len(skills_df):,} ELA skills")
    
    # Classify variants
    state_groups = identify_state_variants(skills_df)
    grade_chains, progression_metadata, chain_details = identify_grade_progressions(skills_df)
    
    # Generate classification report
    report_df = generate_classification_report(
        skills_df, 
        state_groups, 
        grade_chains,
        progression_metadata,
        output_path
    )
    
    # Generate progression chains summary
    if chain_details:
        chains_summary_df = generate_progression_chains_summary(
            chain_details,
            skills_df,
            chains_summary_path
        )
    
    print("\n🎉 Classification complete!")
    print(f"\n💡 Next step: Refresh the Streamlit app to see variant analysis")


if __name__ == '__main__':
    main()

