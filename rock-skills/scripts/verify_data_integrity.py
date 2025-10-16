#!/usr/bin/env python3
"""
Data Integrity Validation Script

Verifies that all critical data files load correctly and are properly formatted.
Run this before demos or presentations to ensure data integrity.

Usage:
    python verify_data_integrity.py
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def validate_file(filepath, description, required_columns=None, min_rows=1):
    """Validate a CSV file loads correctly."""
    try:
        df = pd.read_csv(filepath)
        
        # Check row count
        if len(df) < min_rows:
            print(f"❌ {description}: Too few rows ({len(df)} < {min_rows})")
            return False
        
        # Check required columns
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                print(f"❌ {description}: Missing columns: {missing}")
                return False
        
        print(f"✅ {description}: {len(df)} rows, {len(df.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ {description}: Failed to load - {str(e)}")
        return False

def main():
    """Run all data integrity checks."""
    print("=" * 70)
    print("ROCK Skills Data Integrity Validation")
    print("=" * 70)
    print()
    
    base_path = Path(__file__).parent.parent
    all_valid = True
    
    # Critical data files
    checks = [
        # ROCK Schemas
        (base_path / "rock_schemas" / "SKILLS.csv", 
         "ROCK Skills", 
         ["SKILL_ID", "SKILL_NAME"], 
         8000),
        
        (base_path / "rock_schemas" / "STANDARD_SKILLS.csv",
         "Standard-Skill Relationships",
         ["STANDARD_ID", "SKILL_ID"],
         100000),
        
        # Taxonomy
        (base_path / "POC_science_of_reading_literacy_skills_taxonomy.csv",
         "Science of Reading Taxonomy",
         ["Strand", "Pillar", "Domain"],
         1000),
        
        # LLM Mappings
        (base_path / "analysis" / "llm_skill_mappings.csv",
         "LLM Skill Mappings",
         ["SKILL_ID", "SKILL_NAME"],
         50),
        
        # Master Concepts
        (base_path / "analysis" / "master-concepts.csv",
         "Master Concepts",
         ["MASTER_CONCEPT_ID", "MASTER_CONCEPT_NAME"],
         10),
        
        # POC Mock Data
        (base_path / "poc" / "mock_data" / "content_library.csv",
         "Content Library (Mock Data)",
         ["CONTENT_ID", "CONTENT_TITLE"],
         10),
        
        (base_path / "poc" / "mock_data" / "tagging_scenarios.csv",
         "Tagging Scenarios (Mock Data)",
         ["SCENARIO_ID"],
         10),
    ]
    
    for filepath, description, required_cols, min_rows in checks:
        if not filepath.exists():
            print(f"⚠️  {description}: File not found at {filepath}")
            all_valid = False
        else:
            if not validate_file(filepath, description, required_cols, min_rows):
                all_valid = False
    
    print()
    print("=" * 70)
    if all_valid:
        print("✅ All data integrity checks PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ Some data integrity checks FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

