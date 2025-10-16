#!/usr/bin/env python3
"""
Validate Data Pipeline Integrity

Validates that master concepts and skill mappings are correctly generated
and that all data relationships are intact.

Usage:
    python validate_data_pipeline.py
"""

import pandas as pd
from pathlib import Path
import sys

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def check_file_exists(filepath: Path, name: str) -> bool:
    """Check if a file exists and is readable."""
    if not filepath.exists():
        print(f"  ❌ {name}: File not found at {filepath}")
        return False
    
    try:
        # Try to read a few lines to ensure readability
        df = pd.read_csv(filepath, nrows=5)
        print(f"  ✓ {name}: File exists and is readable")
        return True
    except Exception as e:
        print(f"  ❌ {name}: File exists but cannot be read: {e}")
        return False


def validate_master_concepts(concepts_df: pd.DataFrame) -> bool:
    """Validate master concepts structure and content."""
    print("\nValidating Master Concepts...")
    all_valid = True
    
    # Check required columns
    required_cols = [
        'MASTER_CONCEPT_ID', 'MASTER_CONCEPT_NAME', 'SOR_STRAND', 
        'SOR_PILLAR', 'SOR_DOMAIN', 'DESCRIPTION', 'SKILL_COUNT',
        'AUTHORITY_COUNT', 'GRADE_RANGE', 'EQUIVALENCE_GROUP_ID',
        'TAXONOMY_CONFIDENCE'
    ]
    
    missing_cols = [col for col in required_cols if col not in concepts_df.columns]
    if missing_cols:
        print(f"  ❌ Missing columns: {missing_cols}")
        all_valid = False
    else:
        print(f"  ✓ All required columns present")
    
    # Check for null values in critical fields
    critical_fields = ['MASTER_CONCEPT_ID', 'MASTER_CONCEPT_NAME', 'SKILL_COUNT']
    for field in critical_fields:
        if field in concepts_df.columns:
            null_count = concepts_df[field].isna().sum()
            if null_count > 0:
                print(f"  ❌ {field} has {null_count} null values")
                all_valid = False
            else:
                print(f"  ✓ {field}: No null values")
    
    # Check ID uniqueness
    if 'MASTER_CONCEPT_ID' in concepts_df.columns:
        duplicates = concepts_df['MASTER_CONCEPT_ID'].duplicated().sum()
        if duplicates > 0:
            print(f"  ❌ Found {duplicates} duplicate MASTER_CONCEPT_IDs")
            all_valid = False
        else:
            print(f"  ✓ All MASTER_CONCEPT_IDs are unique")
    
    # Check skill counts are positive
    if 'SKILL_COUNT' in concepts_df.columns:
        invalid_counts = (concepts_df['SKILL_COUNT'] <= 0).sum()
        if invalid_counts > 0:
            print(f"  ❌ Found {invalid_counts} concepts with invalid skill counts")
            all_valid = False
        else:
            print(f"  ✓ All skill counts are positive")
    
    # Check confidence values are valid
    if 'TAXONOMY_CONFIDENCE' in concepts_df.columns:
        valid_confidences = {'High', 'Medium', 'Low'}
        invalid = concepts_df[~concepts_df['TAXONOMY_CONFIDENCE'].isin(valid_confidences)]
        if len(invalid) > 0:
            print(f"  ❌ Found {len(invalid)} concepts with invalid confidence values")
            all_valid = False
        else:
            print(f"  ✓ All confidence values are valid (High/Medium/Low)")
    
    return all_valid


def validate_skill_mappings(mappings_df: pd.DataFrame, 
                            concepts_df: pd.DataFrame,
                            skills_df: pd.DataFrame) -> bool:
    """Validate skill-to-master-concept mappings."""
    print("\nValidating Skill-to-Master-Concept Mappings...")
    all_valid = True
    
    # Check required columns
    required_cols = [
        'SKILL_ID', 'SKILL_NAME', 'MASTER_CONCEPT_ID', 
        'MASTER_CONCEPT_NAME', 'EQUIVALENCE_TYPE', 'TAXONOMY_PATH', 'CONFIDENCE'
    ]
    
    missing_cols = [col for col in required_cols if col not in mappings_df.columns]
    if missing_cols:
        print(f"  ❌ Missing columns: {missing_cols}")
        all_valid = False
    else:
        print(f"  ✓ All required columns present")
    
    # Check for null SKILL_IDs
    if 'SKILL_ID' in mappings_df.columns:
        null_count = mappings_df['SKILL_ID'].isna().sum()
        if null_count > 0:
            print(f"  ❌ SKILL_ID has {null_count} null values")
            all_valid = False
        else:
            print(f"  ✓ SKILL_ID: No null values")
    
    # Check SKILL_ID uniqueness
    if 'SKILL_ID' in mappings_df.columns:
        duplicates = mappings_df['SKILL_ID'].duplicated().sum()
        if duplicates > 0:
            print(f"  ⚠️  Warning: Found {duplicates} duplicate SKILL_IDs in mappings")
    
    # Check that all SKILL_IDs reference valid skills
    if 'SKILL_ID' in mappings_df.columns and not skills_df.empty:
        valid_skill_ids = set(skills_df['SKILL_ID'])
        invalid_refs = mappings_df[~mappings_df['SKILL_ID'].isin(valid_skill_ids)]
        if len(invalid_refs) > 0:
            print(f"  ❌ Found {len(invalid_refs)} skill IDs that don't exist in SKILLS.csv")
            all_valid = False
        else:
            print(f"  ✓ All skill IDs reference valid skills")
    
    # Check that mapped MASTER_CONCEPT_IDs reference valid concepts
    if 'MASTER_CONCEPT_ID' in mappings_df.columns and not concepts_df.empty:
        mapped_skills = mappings_df[mappings_df['MASTER_CONCEPT_ID'].notna()]
        valid_concept_ids = set(concepts_df['MASTER_CONCEPT_ID'])
        invalid_refs = mapped_skills[~mapped_skills['MASTER_CONCEPT_ID'].isin(valid_concept_ids)]
        if len(invalid_refs) > 0:
            print(f"  ❌ Found {len(invalid_refs)} skills with invalid MASTER_CONCEPT_ID references")
            all_valid = False
        else:
            print(f"  ✓ All mapped concept IDs reference valid master concepts")
    
    # Check equivalence types
    if 'EQUIVALENCE_TYPE' in mappings_df.columns:
        valid_types = {'state-variant', 'grade-progression', 'unique'}
        invalid = mappings_df[~mappings_df['EQUIVALENCE_TYPE'].isin(valid_types)]
        if len(invalid) > 0:
            print(f"  ❌ Found {len(invalid)} skills with invalid equivalence types")
            all_valid = False
        else:
            print(f"  ✓ All equivalence types are valid")
    
    return all_valid


def validate_data_relationships(mappings_df: pd.DataFrame,
                                concepts_df: pd.DataFrame) -> bool:
    """Validate relationships between data files."""
    print("\nValidating Data Relationships...")
    all_valid = True
    
    # Check that skill counts in concepts match actual mapped skills
    if not mappings_df.empty and not concepts_df.empty:
        for _, concept in concepts_df.iterrows():
            concept_id = concept['MASTER_CONCEPT_ID']
            expected_count = concept['SKILL_COUNT']
            
            # Count skills mapped to this concept via equivalence group
            equiv_group = concept['EQUIVALENCE_GROUP_ID']
            # Note: This only counts State A skills in the group
            # State B skills may also map via taxonomy similarity
            actual_count = len(mappings_df[
                (mappings_df['MASTER_CONCEPT_ID'] == concept_id) & 
                (mappings_df['EQUIVALENCE_TYPE'] == 'state-variant')
            ])
            
            if actual_count != expected_count and actual_count > 0:
                print(f"  ⚠️  Warning: Concept {concept_id} expected {expected_count} skills but found {actual_count} State A skills")
        
        print(f"  ✓ Checked skill count consistency")
    
    # Check for orphaned master concepts (no skills mapped)
    if not mappings_df.empty and not concepts_df.empty:
        for _, concept in concepts_df.iterrows():
            concept_id = concept['MASTER_CONCEPT_ID']
            mapped_count = len(mappings_df[mappings_df['MASTER_CONCEPT_ID'] == concept_id])
            if mapped_count == 0:
                print(f"  ⚠️  Warning: Concept {concept_id} ({concept['MASTER_CONCEPT_NAME']}) has no skills mapped")
    
    return all_valid


def generate_report(concepts_df: pd.DataFrame, 
                   mappings_df: pd.DataFrame,
                   output_path: Path) -> None:
    """Generate validation report."""
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("DATA PIPELINE VALIDATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # Master Concepts Summary
    report_lines.append("Master Concepts Summary:")
    report_lines.append(f"  Total concepts: {len(concepts_df)}")
    if 'TAXONOMY_CONFIDENCE' in concepts_df.columns:
        report_lines.append(f"  High confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'High').sum()}")
        report_lines.append(f"  Medium confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'Medium').sum()}")
        report_lines.append(f"  Low confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'Low').sum()}")
    report_lines.append("")
    
    # Skill Mappings Summary
    report_lines.append("Skill Mappings Summary:")
    report_lines.append(f"  Total skills: {len(mappings_df)}")
    report_lines.append(f"  Mapped to concepts: {mappings_df['MASTER_CONCEPT_ID'].notna().sum()}")
    report_lines.append(f"  Unmapped (unique): {mappings_df['MASTER_CONCEPT_ID'].isna().sum()}")
    if 'EQUIVALENCE_TYPE' in mappings_df.columns:
        report_lines.append(f"  State A (cross-state): {(mappings_df['EQUIVALENCE_TYPE'] == 'state-variant').sum()}")
        report_lines.append(f"  State B (progressions): {(mappings_df['EQUIVALENCE_TYPE'] == 'grade-progression').sum()}")
    report_lines.append("")
    
    # Coverage Statistics
    if 'SKILL_COUNT' in concepts_df.columns:
        report_lines.append("Fragmentation Statistics:")
        report_lines.append(f"  Average skills per concept: {concepts_df['SKILL_COUNT'].mean():.1f}")
        report_lines.append(f"  Max skills in one concept: {concepts_df['SKILL_COUNT'].max()}")
        report_lines.append(f"  Min skills in one concept: {concepts_df['SKILL_COUNT'].min()}")
    report_lines.append("")
    
    report_lines.append("=" * 70)
    
    report_text = "\n".join(report_lines)
    
    # Print to console
    print("\n" + report_text)
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\n✓ Validation report saved to {output_path}")


def main():
    """Main execution."""
    print("=" * 70)
    print("DATA PIPELINE VALIDATION")
    print("=" * 70)
    
    all_checks_passed = True
    
    # Check files exist
    print("\n1. Checking File Existence...")
    files_to_check = {
        'Master Concepts': BASE_DIR / 'analysis/master-concepts.csv',
        'Skill Mappings': BASE_DIR / 'analysis/skill_master_concept_mapping.csv',
        'Variant Classification': BASE_DIR / 'analysis/outputs/variant-classification-report.csv',
        'LLM Mappings': BASE_DIR / 'analysis/llm_skill_mappings.csv',
        'ROCK Skills': BASE_DIR / 'rock_schemas/SKILLS.csv'
    }
    
    for name, filepath in files_to_check.items():
        if not check_file_exists(filepath, name):
            all_checks_passed = False
    
    # If any files missing, abort
    if not all_checks_passed:
        print("\n❌ Validation failed: Required files missing")
        sys.exit(1)
    
    # Load data
    print("\n2. Loading Data...")
    concepts_df = pd.read_csv(files_to_check['Master Concepts'])
    mappings_df = pd.read_csv(files_to_check['Skill Mappings'])
    skills_df = pd.read_csv(files_to_check['ROCK Skills'], usecols=['SKILL_ID', 'SKILL_NAME'])
    print(f"  ✓ Loaded {len(concepts_df)} master concepts")
    print(f"  ✓ Loaded {len(mappings_df)} skill mappings")
    print(f"  ✓ Loaded {len(skills_df)} ROCK skills")
    
    # Validate master concepts
    print("\n" + "-" * 70)
    if not validate_master_concepts(concepts_df):
        all_checks_passed = False
    
    # Validate skill mappings
    print("\n" + "-" * 70)
    if not validate_skill_mappings(mappings_df, concepts_df, skills_df):
        all_checks_passed = False
    
    # Validate relationships
    print("\n" + "-" * 70)
    if not validate_data_relationships(mappings_df, concepts_df):
        all_checks_passed = False
    
    # Generate report
    print("\n" + "-" * 70)
    print("\n3. Generating Validation Report...")
    report_path = BASE_DIR / 'analysis/data_validation_report.txt'
    generate_report(concepts_df, mappings_df, report_path)
    
    # Final result
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✅ VALIDATION PASSED: All data integrity checks successful")
    else:
        print("⚠️  VALIDATION COMPLETED WITH WARNINGS: Review issues above")
    print("=" * 70)
    
    sys.exit(0 if all_checks_passed else 1)


if __name__ == '__main__':
    main()

