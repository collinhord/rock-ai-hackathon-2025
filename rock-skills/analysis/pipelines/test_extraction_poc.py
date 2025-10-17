#!/usr/bin/env python3
"""
Test script for base skill extraction on a small subset of data.

This validates the extraction pipeline works before running on full dataset.
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_base_skills import BaseSkillExtractor


def test_poc():
    """Run proof-of-concept test on 20 sample skills."""
    
    print("="*60)
    print("BASE SKILL EXTRACTION - POC TEST")
    print("="*60)
    
    # Sample skills representing different types
    sample_skills = [
        "Determine main idea with support (Grade K)",
        "Identify the main idea independently (Grade 3)",
        "Analyze development of central idea (Grade 8)",
        "Determine main idea of an informational text (Grade 5)",
        "Identify central concept with teacher prompting (Grade 2)",
        
        "Analyze narrative perspective (Grade 7)",
        "Analyze narrator perspective and point of view (Grade 9)",
        "Identify point of view (1st/3rd person) (Grade 4)",
        "Analyze how narrator's background influences story (Grade 10)",
        "Determine perspective in fiction (Grade 6)",
        
        "Decode CVC words (Grade 1)",
        "Decode multisyllabic words (Grade 3)",
        "Decode words with consonant blends (Grade 2)",
        
        "Make inferences from text (Grade 4)",
        "Make inferences using textual evidence (Grade 7)",
        "Draw inferences with support (Grade 2)",
        
        "Identify character traits (Grade 3)",
        "Analyze character development (Grade 8)",
        "Describe characters using details (Grade 2)",
        "Compare and contrast characters (Grade 5)"
    ]
    
    # Create DataFrame
    skills_df = pd.DataFrame({
        'SKILL_ID': [f'test-skill-{i:03d}' for i in range(len(sample_skills))],
        'SKILL_NAME': sample_skills,
        'GRADE_LEVEL_NAME': [
            'K', '3', '8', '5', '2',
            '7', '9', '4', '10', '6',
            '1', '3', '2',
            '4', '7', '2',
            '3', '8', '2', '5'
        ]
    })
    
    print(f"\n✓ Created test dataset with {len(skills_df)} sample skills")
    
    # Initialize extractor (LLM disabled for speed)
    print("\nInitializing extractor...")
    extractor = BaseSkillExtractor(use_llm=False, use_clustering=True)
    
    # Run extraction
    print("\nRunning extraction pipeline...")
    skills_with_mappings, base_skills = extractor.extract_base_skills(skills_df)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\nGenerated {len(base_skills)} base skills:")
    for bs in base_skills:
        print(f"\n{bs['base_skill_id']}: {bs['base_skill_name']}")
        print(f"  Description: {bs['base_skill_description']}")
        print(f"  Family: {bs['skill_family']}")
        print(f"  ROCK skills: {bs['rock_skills_count']}")
        
        # Show mapped ROCK skills
        mapped = skills_with_mappings[
            skills_with_mappings['base_skill_id'] == bs['base_skill_id']
        ]['SKILL_NAME'].tolist()
        for skill in mapped[:3]:  # Show first 3
            print(f"    - {skill}")
        if len(mapped) > 3:
            print(f"    ... and {len(mapped) - 3} more")
    
    print("\n" + "="*60)
    print("POC TEST COMPLETE")
    print("="*60)
    
    return True


if __name__ == '__main__':
    try:
        success = test_poc()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

