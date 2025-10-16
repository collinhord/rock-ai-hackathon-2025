#!/usr/bin/env python3
"""
Prepare POC Data for Streamlit App

This script consolidates LLM-assisted mappings with ROCK skill data 
and exports a unified dataset for the Streamlit POC application.

Usage:
    python3 scripts/prepare_poc_data.py --mappings outputs/poc_mappings_200/llm_assisted_mappings_*.csv
"""

import sys
from pathlib import Path
import pandas as pd
import argparse
from glob import glob

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def extract_taxonomy_levels(taxonomy_path: str) -> dict:
    """
    Extract individual taxonomy levels from full path.
    
    Args:
        taxonomy_path: Full taxonomy path like "Literacy > Phonological Awareness > ..."
        
    Returns:
        Dictionary with strand, pillar, domain, skill_area, skill_subset
    """
    if pd.isna(taxonomy_path):
        return {
            'strand': None,
            'pillar': None,
            'domain': None,
            'skill_area': None,
            'skill_subset': None
        }
    
    parts = [p.strip() for p in str(taxonomy_path).split('>')]
    
    return {
        'strand': parts[0] if len(parts) > 0 else None,
        'pillar': parts[1] if len(parts) > 1 else None,
        'domain': parts[2] if len(parts) > 2 else None,
        'skill_area': parts[3] if len(parts) > 3 else None,
        'skill_subset': parts[4] if len(parts) > 4 else None
    }


def load_mappings(mapping_pattern: str) -> pd.DataFrame:
    """Load LLM mapping results from checkpoint files."""
    files = glob(mapping_pattern)
    
    if not files:
        raise FileNotFoundError(f"No mapping files found matching: {mapping_pattern}")
    
    print(f"Found {len(files)} mapping file(s)")
    
    dfs = []
    for file in files:
        print(f"  Loading {file}")
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Drop duplicates (in case of overlapping checkpoints)
    combined = combined.drop_duplicates(subset=['skill_id'], keep='last')
    
    print(f"✓ Loaded {len(combined)} unique skill mappings")
    
    return combined


def prepare_poc_dataset(
    mappings_df: pd.DataFrame,
    skills_path: Path,
    output_path: Path,
    min_confidence: str = None
) -> pd.DataFrame:
    """
    Prepare consolidated POC dataset.
    
    Args:
        mappings_df: LLM mapping results
        skills_path: Path to SKILLS.csv
        output_path: Where to save consolidated dataset
        min_confidence: Optional filter (High, Medium, Low)
    """
    
    print("\nPreparing POC dataset...")
    
    # Load SKILLS.csv (optimized columns)
    essential_columns = [
        'SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME', 'GRADE_LEVEL_SHORT_NAME'
    ]
    
    print(f"Loading {skills_path}")
    skills_df = pd.read_csv(skills_path, usecols=essential_columns)
    print(f"✓ Loaded {len(skills_df)} ROCK skills")
    
    # Standardize column names in mappings
    mappings_df = mappings_df.rename(columns={
        'skill_id': 'SKILL_ID',
        'skill_name': 'SKILL_NAME',
        'taxonomy_path': 'TAXONOMY_PATH',
        'confidence': 'CONFIDENCE',
        'semantic_similarity': 'SEMANTIC_SIMILARITY',
        'needs_review': 'NEEDS_REVIEW',
        'alternative_1': 'ALTERNATIVE_1',
        'alternative_2': 'ALTERNATIVE_2',
        'rationale': 'RATIONALE'
    })
    
    # Filter by confidence if specified
    if min_confidence:
        confidence_order = {'High': 3, 'Medium': 2, 'Low': 1}
        min_level = confidence_order.get(min_confidence, 0)
        
        mappings_df['confidence_level'] = mappings_df['CONFIDENCE'].map(confidence_order)
        mappings_df = mappings_df[mappings_df['confidence_level'] >= min_level]
        mappings_df = mappings_df.drop(columns=['confidence_level'])
        
        print(f"✓ Filtered to {len(mappings_df)} mappings with {min_confidence}+ confidence")
    
    # Extract taxonomy levels
    print("Extracting taxonomy hierarchy levels...")
    taxonomy_levels = mappings_df['TAXONOMY_PATH'].apply(extract_taxonomy_levels)
    taxonomy_df = pd.DataFrame(taxonomy_levels.tolist())
    
    mappings_with_levels = pd.concat([mappings_df, taxonomy_df], axis=1)
    
    # Merge with full ROCK skill data
    print("Merging with ROCK skill metadata...")
    poc_dataset = skills_df.merge(
        mappings_with_levels[[
            'SKILL_ID', 'TAXONOMY_PATH', 'CONFIDENCE', 'SEMANTIC_SIMILARITY',
            'NEEDS_REVIEW', 'ALTERNATIVE_1', 'ALTERNATIVE_2', 'RATIONALE',
            'strand', 'pillar', 'domain', 'skill_area', 'skill_subset'
        ]],
        on='SKILL_ID',
        how='inner'  # Only include mapped skills
    )
    
    print(f"✓ Created POC dataset with {len(poc_dataset)} skills")
    
    # Statistics
    print("\n" + "="*60)
    print("POC DATASET STATISTICS")
    print("="*60)
    print(f"Total Skills Mapped: {len(poc_dataset):,}")
    print(f"\nConfidence Distribution:")
    print(poc_dataset['CONFIDENCE'].value_counts().to_string())
    print(f"\nContent Area Distribution:")
    print(poc_dataset['CONTENT_AREA_NAME'].value_counts().to_string())
    print(f"\nGrade Level Distribution:")
    print(poc_dataset['GRADE_LEVEL_NAME'].value_counts().to_string())
    print(f"\nScience of Reading Pillar Distribution:")
    print(poc_dataset['pillar'].value_counts().to_string())
    print(f"\nAverage Semantic Similarity: {poc_dataset['SEMANTIC_SIMILARITY'].mean():.3f}")
    print(f"Needs Review: {poc_dataset['NEEDS_REVIEW'].sum():,} skills")
    print("="*60)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    poc_dataset.to_csv(output_path, index=False)
    print(f"\n✓ Saved POC dataset to: {output_path}")
    
    return poc_dataset


def main():
    parser = argparse.ArgumentParser(
        description="Prepare POC data from LLM mapping results"
    )
    parser.add_argument(
        '--mappings',
        required=True,
        help='Pattern for mapping CSV files (e.g., outputs/*/llm_assisted_mappings_*.csv)'
    )
    parser.add_argument(
        '--skills-path',
        default='../../rock_schemas/SKILLS.csv',
        help='Path to SKILLS.csv'
    )
    parser.add_argument(
        '--output',
        default='../llm_skill_mappings.csv',
        help='Output path for consolidated POC dataset'
    )
    parser.add_argument(
        '--min-confidence',
        choices=['High', 'Medium', 'Low'],
        help='Minimum confidence level to include'
    )
    
    args = parser.parse_args()
    
    # Convert to absolute paths
    script_dir = Path(__file__).parent
    mappings_pattern = str((script_dir / args.mappings).resolve())
    skills_path = (script_dir / args.skills_path).resolve()
    output_path = (script_dir / args.output).resolve()
    
    print("="*60)
    print("PREPARE POC DATASET FOR STREAMLIT APP")
    print("="*60)
    print(f"Mapping pattern: {mappings_pattern}")
    print(f"Skills path: {skills_path}")
    print(f"Output path: {output_path}")
    if args.min_confidence:
        print(f"Min confidence: {args.min_confidence}")
    print("="*60 + "\n")
    
    # Load mappings
    mappings_df = load_mappings(mappings_pattern)
    
    # Prepare dataset
    poc_dataset = prepare_poc_dataset(
        mappings_df,
        skills_path,
        output_path,
        args.min_confidence
    )
    
    print("\n✅ POC dataset preparation complete!")
    print(f"📊 Dataset ready for Streamlit at: {output_path}")


if __name__ == '__main__':
    main()

