#!/usr/bin/env python3
"""
Generate Master Concepts from State A Variant Groups

Integrates variant classification (State A groups) with LLM taxonomy mappings
to produce master concepts that bridge fragmented ROCK skills.

Usage:
    python generate_master_concepts.py [--output OUTPUT_DIR]

Output:
    - master-concepts.csv: Master concept definitions
    - skill_master_concept_mapping.csv: Skill-to-concept bridge table
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import sys
import re
from typing import Dict, List, Tuple, Optional

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all required data files."""
    print("Loading data files...")
    
    # Variant classification
    variant_path = BASE_DIR / 'analysis/outputs/variant-classification-report.csv'
    variants_df = pd.read_csv(variant_path)
    print(f"  ✓ Loaded {len(variants_df):,} skills from variant classification")
    
    # LLM skill mappings
    mappings_path = BASE_DIR / 'analysis/llm_skill_mappings.csv'
    mappings_df = pd.read_csv(mappings_path)
    print(f"  ✓ Loaded {len(mappings_df):,} LLM skill mappings")
    
    # Science of Reading taxonomy
    taxonomy_path = BASE_DIR / 'POC_science_of_reading_literacy_skills_taxonomy.csv'
    taxonomy_df = pd.read_csv(taxonomy_path)
    print(f"  ✓ Loaded {len(taxonomy_df):,} taxonomy entries")
    
    # ROCK skills (for additional metadata)
    skills_path = BASE_DIR / 'rock_schemas/SKILLS.csv'
    skills_df = pd.read_csv(skills_path, usecols=['SKILL_ID', 'SKILL_NAME', 'GRADE_LEVEL_NAME', 'GRADE_LEVEL_SHORT_NAME'])
    print(f"  ✓ Loaded {len(skills_df):,} ROCK skills")
    
    return variants_df, mappings_df, taxonomy_df, skills_df


def extract_master_concept_name(taxonomy_path: str, taxonomy_df: pd.DataFrame) -> Optional[str]:
    """
    Extract master concept name from taxonomy path.
    Prioritize Skill Area or Skill Subset level.
    """
    if pd.isna(taxonomy_path) or not taxonomy_path:
        return None
    
    # Parse taxonomy path (format: "Strand > Pillar > Domain > Skill Area > ...")
    parts = [p.strip() for p in taxonomy_path.split('>')]
    
    # Try to get Skill Area (4th level) or last meaningful level
    if len(parts) >= 4:
        return parts[3]  # Skill Area
    elif len(parts) >= 3:
        return parts[2]  # Domain
    elif len(parts) >= 2:
        return parts[1]  # Pillar
    else:
        return parts[0] if parts else None


def extract_taxonomy_hierarchy(taxonomy_path: str) -> Dict[str, str]:
    """Extract strand, pillar, domain from taxonomy path."""
    hierarchy = {
        'strand': None,
        'pillar': None,
        'domain': None
    }
    
    if pd.isna(taxonomy_path) or not taxonomy_path:
        return hierarchy
    
    parts = [p.strip() for p in taxonomy_path.split('>')]
    
    if len(parts) >= 1:
        hierarchy['strand'] = parts[0]
    if len(parts) >= 2:
        hierarchy['pillar'] = parts[1]
    if len(parts) >= 3:
        hierarchy['domain'] = parts[2]
    
    return hierarchy


def get_taxonomy_description(concept_name: str, taxonomy_df: pd.DataFrame) -> Optional[str]:
    """Get description/annotation for a concept from taxonomy."""
    # Try to find matching row in taxonomy
    for col in ['Skill Area', 'Skill Subset', 'Domain', 'Pillar']:
        if col in taxonomy_df.columns:
            matches = taxonomy_df[taxonomy_df[col] == concept_name]
            if not matches.empty:
                # Look for annotation column
                for anno_col in ['Skill Subset Annotation', 'Skill Area Annotation', 'Description']:
                    if anno_col in matches.columns and pd.notna(matches.iloc[0][anno_col]):
                        return str(matches.iloc[0][anno_col])
    
    return None


def calculate_grade_range(grade_levels: List[str]) -> str:
    """Calculate grade range from list of grade levels."""
    if not grade_levels or all(pd.isna(g) for g in grade_levels):
        return "Unknown"
    
    # Filter out NaN values
    valid_grades = [g for g in grade_levels if pd.notna(g)]
    if not valid_grades:
        return "Unknown"
    
    # Define grade order
    grade_order = ['Pre-K', 'PK', 'K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    
    # Extract grades that match our order
    ordered_grades = []
    for g in valid_grades:
        g_str = str(g).strip()
        if g_str in grade_order:
            ordered_grades.append(g_str)
    
    if not ordered_grades:
        # Handle non-standard grades
        return f"{valid_grades[0]} to {valid_grades[-1]}" if len(valid_grades) > 1 else str(valid_grades[0])
    
    # Sort by grade order
    ordered_grades = sorted(set(ordered_grades), key=lambda x: grade_order.index(x))
    
    if len(ordered_grades) == 1:
        return ordered_grades[0]
    else:
        return f"{ordered_grades[0]} to {ordered_grades[-1]}"


def determine_confidence(confidence_values: List[str]) -> str:
    """Determine overall confidence from individual confidence values."""
    if not confidence_values:
        return "Low"
    
    # Count confidence levels
    counts = Counter(confidence_values)
    total = len(confidence_values)
    
    high_pct = counts.get('High', 0) / total
    
    if high_pct >= 0.7:
        return "High"
    elif high_pct >= 0.4:
        return "Medium"
    else:
        return "Low"


def determine_complexity_band(grade_levels: List[str]) -> str:
    """
    Determine complexity band from grade levels.
    
    Args:
        grade_levels: List of grade level names
        
    Returns:
        Complexity band: "K-2", "3-5", "6-8", "9-12", or "Mixed"
    """
    if not grade_levels:
        return "Unknown"
    
    # Define bands
    bands = {
        'K-2': ['Pre-K', 'PK', 'K', '1', '2'],
        '3-5': ['3', '4', '5'],
        '6-8': ['6', '7', '8'],
        '9-12': ['9', '10', '11', '12']
    }
    
    # Normalize grade levels
    normalized = [str(g).strip() for g in grade_levels if pd.notna(g)]
    
    # Count which bands are represented
    band_counts = {band: 0 for band in bands}
    for grade in normalized:
        for band_name, band_grades in bands.items():
            if grade in band_grades:
                band_counts[band_name] += 1
                break
    
    # Get primary band (most represented)
    if sum(band_counts.values()) == 0:
        return "Unknown"
    
    max_band = max(band_counts.items(), key=lambda x: x[1])
    
    # If multiple bands represented, return "Mixed"
    active_bands = [b for b, c in band_counts.items() if c > 0]
    if len(active_bands) > 1:
        return "Mixed"
    
    return max_band[0]


def enrich_concept_with_metadata(concept_skills: pd.DataFrame, 
                                 metadata_df: pd.DataFrame) -> Dict:
    """
    Add pedagogical metadata to master concept definition.
    
    Args:
        concept_skills: DataFrame of skills in this concept
        metadata_df: DataFrame with metadata enrichment
        
    Returns:
        Dictionary with aggregated metadata fields
    """
    enrichment = {
        'TEXT_TYPE': None,
        'TEXT_MODE': None,
        'SKILL_DOMAIN': None
    }
    
    # Return early if no metadata available
    if metadata_df is None or metadata_df.empty:
        return enrichment
    
    # Merge skills with metadata
    skill_ids = concept_skills['SKILL_ID'].tolist()
    skill_metadata = metadata_df[metadata_df['SKILL_ID'].isin(skill_ids)]
    
    if skill_metadata.empty:
        return enrichment
    
    # Find most common values for each field
    for field in ['text_type', 'text_mode', 'skill_domain']:
        values = skill_metadata[field].dropna()
        if not values.empty:
            # Get most common, exclude "not_applicable"
            value_counts = values.value_counts()
            non_na_values = value_counts[value_counts.index != 'not_applicable']
            if not non_na_values.empty:
                enrichment[field.upper()] = non_na_values.index[0]
    
    return enrichment


def generate_master_concepts(variants_df: pd.DataFrame, 
                             mappings_df: pd.DataFrame, 
                             taxonomy_df: pd.DataFrame,
                             skills_df: pd.DataFrame,
                             metadata_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Generate master concepts from State A variant groups.
    
    Args:
        variants_df: Variant classification data
        mappings_df: LLM skill mappings
        taxonomy_df: Science of Reading taxonomy
        skills_df: ROCK skills data
        metadata_df: Optional metadata enrichment data
        
    Returns:
        DataFrame of master concepts with complexity bands and metadata
    """
    print("\nGenerating master concepts from State A groups...")
    
    # Filter to State A (cross-state variants)
    state_a_skills = variants_df[variants_df['EQUIVALENCE_TYPE'] == 'state-variant'].copy()
    print(f"  Found {len(state_a_skills):,} State A skills in {state_a_skills['EQUIVALENCE_GROUP_ID'].nunique()} groups")
    
    if metadata_df is not None and not metadata_df.empty:
        print(f"  Using metadata enrichment from {len(metadata_df):,} skills")
    
    master_concepts = []
    concept_id_counter = 1
    
    # Group by equivalence group
    for group_id, group_skills in state_a_skills.groupby('EQUIVALENCE_GROUP_ID'):
        skill_ids = group_skills['SKILL_ID'].tolist()
        
        # Join with LLM mappings to get taxonomy paths
        group_mappings = mappings_df[mappings_df['SKILL_ID'].isin(skill_ids)]
        
        # group_skills already has GRADE_LEVEL_SHORT_NAME from variant classification
        group_with_grades = group_skills
        
        # Skip if no mappings found
        if group_mappings.empty:
            continue
        
        # Determine consensus taxonomy path (most common)
        taxonomy_paths = group_mappings['TAXONOMY_PATH'].dropna()
        if taxonomy_paths.empty:
            continue
        
        # Use most common taxonomy path
        consensus_path = taxonomy_paths.mode()[0] if not taxonomy_paths.mode().empty else taxonomy_paths.iloc[0]
        
        # Extract master concept name
        concept_name = extract_master_concept_name(consensus_path, taxonomy_df)
        if not concept_name:
            # Fallback to skill area from first skill
            concept_name = group_skills.iloc[0]['SKILL_AREA_NAME']
        
        # Extract taxonomy hierarchy
        hierarchy = extract_taxonomy_hierarchy(consensus_path)
        
        # Get description from taxonomy
        description = get_taxonomy_description(concept_name, taxonomy_df)
        if not description:
            # Fallback: use first skill name as description
            description = f"Skills related to {concept_name.lower()}"
        
        # Calculate metrics
        skill_count = len(skill_ids)
        authority_count = group_skills['AUTHORITY'].nunique()
        grade_range = calculate_grade_range(group_with_grades['GRADE_LEVEL_SHORT_NAME'].tolist())
        
        # Determine confidence
        confidences = group_mappings['CONFIDENCE'].dropna().tolist()
        taxonomy_confidence = determine_confidence(confidences)
        
        # Determine complexity band
        grade_levels = group_with_grades['GRADE_LEVEL_SHORT_NAME'].tolist()
        complexity_band = determine_complexity_band(grade_levels)
        
        # Enrich with metadata if available
        metadata_enrichment = enrich_concept_with_metadata(group_skills, metadata_df)
        
        # Create master concept
        master_concept = {
            'MASTER_CONCEPT_ID': f"MC-SA-{concept_id_counter:04d}",
            'MASTER_CONCEPT_NAME': concept_name,
            'SOR_STRAND': hierarchy['strand'],
            'SOR_PILLAR': hierarchy['pillar'],
            'SOR_DOMAIN': hierarchy['domain'],
            'DESCRIPTION': description,
            'SKILL_COUNT': skill_count,
            'AUTHORITY_COUNT': authority_count,
            'GRADE_RANGE': grade_range,
            'COMPLEXITY_BAND': complexity_band,
            'TEXT_TYPE': metadata_enrichment.get('TEXT_TYPE'),
            'TEXT_MODE': metadata_enrichment.get('TEXT_MODE'),
            'SKILL_DOMAIN': metadata_enrichment.get('SKILL_DOMAIN'),
            'PREREQUISITE_CONCEPT_ID': None,  # TODO: Implement prerequisite tracking
            'EQUIVALENCE_GROUP_ID': group_id,
            'TAXONOMY_CONFIDENCE': taxonomy_confidence
        }
        
        master_concepts.append(master_concept)
        concept_id_counter += 1
    
    concepts_df = pd.DataFrame(master_concepts)
    print(f"  ✓ Generated {len(concepts_df)} master concepts")
    
    return concepts_df


def generate_skill_mapping(variants_df: pd.DataFrame,
                           mappings_df: pd.DataFrame,
                           concepts_df: pd.DataFrame,
                           skills_df: pd.DataFrame) -> pd.DataFrame:
    """Generate skill-to-master-concept bridge table."""
    print("\nGenerating skill-to-master-concept mappings...")
    
    skill_mappings = []
    
    # Create lookup: equivalence_group_id -> master_concept_id
    group_to_concept = dict(zip(concepts_df['EQUIVALENCE_GROUP_ID'], concepts_df['MASTER_CONCEPT_ID']))
    concept_names = dict(zip(concepts_df['MASTER_CONCEPT_ID'], concepts_df['MASTER_CONCEPT_NAME']))
    
    # Process all skills
    for _, skill_row in variants_df.iterrows():
        skill_id = skill_row['SKILL_ID']
        equiv_type = skill_row['EQUIVALENCE_TYPE']
        equiv_group = skill_row['EQUIVALENCE_GROUP_ID']
        
        # Get skill name
        skill_info = skills_df[skills_df['SKILL_ID'] == skill_id]
        skill_name = skill_info.iloc[0]['SKILL_NAME'] if not skill_info.empty else skill_row['SKILL_NAME']
        
        # Get taxonomy path and confidence from LLM mappings
        mapping_info = mappings_df[mappings_df['SKILL_ID'] == skill_id]
        taxonomy_path = mapping_info.iloc[0]['TAXONOMY_PATH'] if not mapping_info.empty else None
        confidence = mapping_info.iloc[0]['CONFIDENCE'] if not mapping_info.empty else None
        
        # Determine master concept
        master_concept_id = None
        master_concept_name = None
        
        if equiv_type == 'state-variant' and equiv_group in group_to_concept:
            # State A: direct mapping via equivalence group
            master_concept_id = group_to_concept[equiv_group]
            master_concept_name = concept_names[master_concept_id]
        elif equiv_type == 'grade-progression' and not pd.isna(taxonomy_path):
            # State B: try to map via taxonomy similarity
            # Find concepts with similar taxonomy paths
            if not concepts_df.empty:
                for _, concept in concepts_df.iterrows():
                    concept_hierarchy = f"{concept['SOR_STRAND']} > {concept['SOR_PILLAR']} > {concept['SOR_DOMAIN']}"
                    if pd.notna(taxonomy_path) and concept_hierarchy in taxonomy_path:
                        master_concept_id = concept['MASTER_CONCEPT_ID']
                        master_concept_name = concept['MASTER_CONCEPT_NAME']
                        break
        # Unique skills: leave unmapped (master_concept_id = None)
        
        skill_mapping = {
            'SKILL_ID': skill_id,
            'SKILL_NAME': skill_name,
            'MASTER_CONCEPT_ID': master_concept_id,
            'MASTER_CONCEPT_NAME': master_concept_name,
            'EQUIVALENCE_TYPE': equiv_type,
            'TAXONOMY_PATH': taxonomy_path,
            'CONFIDENCE': confidence
        }
        
        skill_mappings.append(skill_mapping)
    
    mappings_df = pd.DataFrame(skill_mappings)
    
    mapped_count = mappings_df['MASTER_CONCEPT_ID'].notna().sum()
    print(f"  ✓ Generated {len(mappings_df):,} skill mappings ({mapped_count:,} mapped to master concepts)")
    
    return mappings_df


def save_outputs(concepts_df: pd.DataFrame, 
                skill_mappings_df: pd.DataFrame,
                output_dir: Path):
    """Save generated data files."""
    print("\nSaving outputs...")
    
    # Save master concepts
    concepts_path = output_dir / 'master-concepts.csv'
    concepts_df.to_csv(concepts_path, index=False)
    print(f"  ✓ Saved master concepts to {concepts_path}")
    
    # Save skill mappings
    mappings_path = output_dir / 'skill_master_concept_mapping.csv'
    skill_mappings_df.to_csv(mappings_path, index=False)
    print(f"  ✓ Saved skill mappings to {mappings_path}")
    
    return concepts_path, mappings_path


def print_summary(concepts_df: pd.DataFrame, skill_mappings_df: pd.DataFrame):
    """Print summary statistics."""
    print("\n" + "="*70)
    print("MASTER CONCEPTS GENERATION SUMMARY")
    print("="*70)
    
    print(f"\nMaster Concepts Generated: {len(concepts_df)}")
    print(f"  - High Confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'High').sum()}")
    print(f"  - Medium Confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'Medium').sum()}")
    print(f"  - Low Confidence: {(concepts_df['TAXONOMY_CONFIDENCE'] == 'Low').sum()}")
    
    print(f"\nSkill Coverage:")
    print(f"  - Total skills processed: {len(skill_mappings_df):,}")
    print(f"  - Mapped to master concepts: {skill_mappings_df['MASTER_CONCEPT_ID'].notna().sum():,}")
    print(f"  - State A (cross-state variants): {(skill_mappings_df['EQUIVALENCE_TYPE'] == 'state-variant').sum():,}")
    print(f"  - State B (grade progressions): {(skill_mappings_df['EQUIVALENCE_TYPE'] == 'grade-progression').sum():,}")
    print(f"  - Unique skills: {(skill_mappings_df['EQUIVALENCE_TYPE'] == 'unique').sum():,}")
    
    print(f"\nFragmentation Metrics:")
    print(f"  - Average skills per concept: {concepts_df['SKILL_COUNT'].mean():.1f}")
    print(f"  - Max skills in one concept: {concepts_df['SKILL_COUNT'].max()}")
    print(f"  - Average authorities per concept: {concepts_df['AUTHORITY_COUNT'].mean():.1f}")
    
    print(f"\nTop 10 Most Fragmented Concepts:")
    top_concepts = concepts_df.nlargest(10, 'SKILL_COUNT')[['MASTER_CONCEPT_NAME', 'SKILL_COUNT', 'AUTHORITY_COUNT']]
    for idx, row in top_concepts.iterrows():
        print(f"  {row['MASTER_CONCEPT_NAME'][:50]:50s} | {row['SKILL_COUNT']:2d} skills | {row['AUTHORITY_COUNT']:2d} states")
    
    print("\n" + "="*70)


def main():
    """Main execution."""
    print("="*70)
    print("MASTER CONCEPTS GENERATOR")
    print("="*70)
    
    # Load data
    variants_df, mappings_df, taxonomy_df, skills_df = load_data()
    
    # Try to load metadata enrichment (optional)
    metadata_df = None
    metadata_path = BASE_DIR / 'analysis' / 'outputs' / 'skill_metadata_enriched.csv'
    
    if metadata_path.exists():
        print(f"\n📊 Loading metadata enrichment from {metadata_path.name}...")
        metadata_df = pd.read_csv(metadata_path)
        print(f"   Found metadata for {len(metadata_df):,} skills")
    else:
        print(f"\n⚠️  No metadata enrichment found at {metadata_path}")
        print("   Master concepts will be generated without text_type/text_mode/skill_domain fields")
        print("   To add metadata: run `python analysis/scripts/metadata_extractor.py`")
    
    # Generate master concepts
    concepts_df = generate_master_concepts(variants_df, mappings_df, taxonomy_df, skills_df, metadata_df)
    
    # Generate skill mappings
    skill_mappings_df = generate_skill_mapping(variants_df, mappings_df, concepts_df, skills_df)
    
    # Save outputs
    output_dir = BASE_DIR / 'analysis'
    concepts_path, mappings_path = save_outputs(concepts_df, skill_mappings_df, output_dir)
    
    # Print summary
    print_summary(concepts_df, skill_mappings_df)
    
    print(f"\n✅ Master concepts generation complete!")
    print(f"\n📁 Output files:")
    print(f"   - {concepts_path}")
    print(f"   - {mappings_path}")
    print(f"\n💡 Next step: Run validation script to verify data integrity")


if __name__ == '__main__':
    main()

