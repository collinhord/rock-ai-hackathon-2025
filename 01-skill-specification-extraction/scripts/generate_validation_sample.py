#!/usr/bin/env python3
"""
Generate Stratified Validation Sample - Phase 3.2

Creates a stratified random sample of skills for expert validation:
- 100 ELA skills (25 per grade band)
- 100 Math skills (20/30/30/20 per grade band)
- Mix of confidence levels
- Exports to CSV for manual review

Usage:
    python3 generate_validation_sample.py \
        --input ../outputs/production_extraction/combined/all_skills_metadata_combined.csv \
        --output ../outputs/production_extraction/validation/validation_sample.csv
"""

import pandas as pd
import argparse
from pathlib import Path
import numpy as np

def generate_stratified_sample(df: pd.DataFrame, content_area: str, sample_sizes: dict) -> pd.DataFrame:
    """Generate stratified random sample by grade band and confidence."""
    
    samples = []
    
    for band, size in sample_sizes.items():
        # Filter by content area and grade band
        band_df = df[
            (df['CONTENT_AREA'] == content_area) &
            (df['complexity_band'] == band)
        ]
        
        if len(band_df) == 0:
            print(f"Warning: No {content_area} skills found for band {band}")
            continue
        
        # Target confidence distribution: 80% high, 15% medium, 5% low
        high_target = int(size * 0.80)
        medium_target = int(size * 0.15)
        low_target = size - high_target - medium_target
        
        # Sample by confidence level
        high_skills = band_df[band_df['llm_confidence'] == 'high']
        medium_skills = band_df[band_df['llm_confidence'] == 'medium']
        low_skills = band_df[band_df['llm_confidence'] == 'low']
        
        # Adjust if not enough in category
        actual_high = min(high_target, len(high_skills))
        actual_medium = min(medium_target, len(medium_skills))
        actual_low = min(low_target, len(low_skills))
        
        # Fill remaining with high confidence if needed
        remaining = size - (actual_high + actual_medium + actual_low)
        if remaining > 0:
            actual_high += remaining
        
        # Sample
        if len(high_skills) >= actual_high:
            samples.append(high_skills.sample(n=actual_high, random_state=42))
        else:
            samples.append(high_skills)
            
        if len(medium_skills) >= actual_medium:
            samples.append(medium_skills.sample(n=actual_medium, random_state=42))
        else:
            samples.append(medium_skills)
            
        if len(low_skills) >= actual_low:
            samples.append(low_skills.sample(n=actual_low, random_state=42))
        else:
            samples.append(low_skills)
        
        print(f"  {content_area} {band}: {actual_high + actual_medium + actual_low} skills " +
              f"({actual_high} high, {actual_medium} medium, {actual_low} low)")
    
    return pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()

def add_validation_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add columns for manual validation."""
    
    df['validation_score'] = ''  # 1-5 scale
    df['validator_name'] = ''
    df['validation_date'] = ''
    df['validation_notes'] = ''
    
    # Add individual field validation columns
    fields_to_validate = [
        'root_verb', 'actions', 'targets', 'cognitive_demand',
        'task_complexity', 'skill_domain', 'text_type'
    ]
    
    for field in fields_to_validate:
        df[f'{field}_valid'] = ''  # Y/N
        df[f'{field}_correction'] = ''  # If N, what should it be?
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Generate validation sample')
    parser.add_argument('--input', required=True, help='Combined metadata file')
    parser.add_argument('--output', required=True, help='Output validation sample file')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    print("="*70)
    print("VALIDATION SAMPLE GENERATION")
    print("="*70)
    print()
    
    # Load data
    print("Loading metadata...")
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} skills")
    print(f"  ELA: {(df['CONTENT_AREA'] == 'English Language Arts').sum()}")
    print(f"  Math: {(df['CONTENT_AREA'] == 'Mathematics').sum()}")
    print()
    
    # Set seed
    np.random.seed(args.seed)
    
    # Define sample sizes
    ela_sizes = {
        'K-2': 25,
        '3-5': 25,
        '6-8': 25,
        '9-12': 25,
    }
    
    math_sizes = {
        'K-2': 20,
        '3-5': 30,
        '6-8': 30,
        '9-12': 20,
    }
    
    # Generate ELA sample
    print("Generating ELA sample...")
    ela_sample = generate_stratified_sample(df, 'English Language Arts', ela_sizes)
    print(f"  Total ELA sample: {len(ela_sample)} skills")
    print()
    
    # Generate Math sample
    print("Generating Math sample...")
    math_sample = generate_stratified_sample(df, 'Mathematics', math_sizes)
    print(f"  Total Math sample: {len(math_sample)} skills")
    print()
    
    # Combine
    validation_sample = pd.concat([ela_sample, math_sample], ignore_index=True)
    print(f"Combined sample: {len(validation_sample)} skills")
    print()
    
    # Add validation columns
    print("Adding validation columns...")
    validation_sample = add_validation_columns(validation_sample)
    
    # Reorder columns for readability
    core_cols = ['SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME', 'GRADE_LEVEL_SHORT_NAME', 
                 'CONTENT_AREA', 'complexity_band']
    metadata_cols = ['actions', 'targets', 'root_verb', 'cognitive_demand', 
                     'task_complexity', 'skill_domain', 'text_type', 'llm_confidence']
    validation_cols = [col for col in validation_sample.columns if 
                       col.startswith('validation_') or col.endswith('_valid') or col.endswith('_correction')]
    other_cols = [col for col in validation_sample.columns if 
                  col not in core_cols + metadata_cols + validation_cols]
    
    validation_sample = validation_sample[core_cols + metadata_cols + validation_cols + other_cols]
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validation_sample.to_csv(output_path, index=False)
    
    print(f"✓ Validation sample saved to: {output_path}")
    print()
    
    # Create summary
    print("="*70)
    print("SAMPLE SUMMARY")
    print("="*70)
    print()
    print("Distribution by Content Area and Grade Band:")
    print(validation_sample.groupby(['CONTENT_AREA', 'complexity_band']).size())
    print()
    print("Distribution by Confidence Level:")
    print(validation_sample.groupby(['CONTENT_AREA', 'llm_confidence']).size())
    print()
    
    # Create instructions file
    instructions_file = output_path.parent / 'VALIDATION_INSTRUCTIONS.md'
    with open(instructions_file, 'w') as f:
        f.write("""# Validation Instructions

## Overview

This file contains 200 randomly selected ROCK skills (100 ELA + 100 Math) for expert validation of extracted metadata.

## Validation Process

### 1. Review Each Skill

For each skill, review:
- SKILL_NAME: The original skill description
- Extracted metadata fields: actions, targets, cognitive_demand, etc.
- LLM confidence rating

### 2. Assign Overall Score

In the `validation_score` column, enter a score from 1-5:
- **5 - Excellent**: All metadata perfect, ready for production
- **4 - Good**: Minor issues, acceptable for production
- **3 - Acceptable**: Some issues, usable but could improve
- **2 - Poor**: Significant issues, requires correction
- **1 - Fail**: Major errors, not usable

### 3. Validate Individual Fields

For each field listed (root_verb, actions, targets, etc.):
- In the `*_valid` column, enter:
  - `Y` if the extracted value is correct
  - `N` if the extracted value is incorrect or missing
- If `N`, in the `*_correction` column, enter what the correct value should be

### 4. Add Notes

In the `validation_notes` column, add any additional comments:
- Explain issues found
- Suggest improvements
- Note edge cases or ambiguities

### 5. Complete Header Fields

- `validator_name`: Your name
- `validation_date`: Today's date (YYYY-MM-DD)

## Focus Areas

### High Priority Fields
1. **cognitive_demand**: Is the Bloom's taxonomy level correct?
2. **task_complexity**: Does basic/intermediate/advanced match the skill?
3. **skill_domain**: Is the primary domain correctly identified?
4. **actions**: Are the key verbs captured?

### Medium Priority Fields
5. **targets**: Are the main concepts/objects identified?
6. **text_type**: For ELA, is fictional/informational correct?
7. **root_verb**: Is the primary action verb correct?

## Common Issues to Watch For

### ELA Skills
- Text type ambiguity (could apply to both fictional and informational)
- Poetry skills may have text_mode incorrectly set
- Multi-domain skills (reading + writing) domain classification
- Support level not detected in skill description

### Math Skills
- Most text_type, text_mode, text_genre should be "not_applicable"
- skill_domain likely "not_applicable" (needs Math-specific values)
- scope values don't fit Math skills well
- Actions: look for solve, calculate, apply, construct, prove

## Example Validation

```
SKILL_NAME: "Identify the main idea of a text"

actions: "identify"          → actions_valid: Y
targets: "idea|text"          → targets_valid: Y
root_verb: "identify"         → root_verb_valid: Y
cognitive_demand: "recall"    → cognitive_demand_valid: N
cognitive_demand_correction: "comprehension" (identifying main idea requires understanding, not just recall)
task_complexity: "basic"      → task_complexity_valid: Y
skill_domain: "reading"       → skill_domain_valid: Y
text_type: "mixed"            → text_type_valid: Y (applies to any text)

validation_score: 4 (Good - one field needs correction)
validation_notes: "Cognitive demand should be comprehension. Main idea identification requires understanding the text, not memorizing facts."
```

## Submission

When complete, save the file and return to: [contact/submission method]

Target completion: [date]

Thank you for your expert review!
""")
    
    print(f"✓ Validation instructions saved to: {instructions_file}")
    print()
    print("="*70)
    print("✅ VALIDATION SAMPLE READY")
    print("="*70)
    print()
    print("Next steps:")
    print(f"1. Share {output_path.name} with domain experts")
    print(f"2. Provide {instructions_file.name} as validation guide")
    print("3. Collect completed validations")
    print("4. Calculate accuracy metrics")
    print("5. Identify systematic issues for schema v2.0")

if __name__ == '__main__':
    main()

