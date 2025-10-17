#!/usr/bin/env python3
"""
Quick verification script to ensure all data loads correctly in the Streamlit app.
Run this before demo to verify data accessibility.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from data_loader import ROCKDataLoader

def verify_data_loading():
    """Verify all critical data files load successfully."""
    
    print("=" * 70)
    print("DATA LOADING VERIFICATION")
    print("=" * 70)
    
    # Initialize loader
    base_dir = Path(__file__).resolve().parent.parent
    schema_dir = base_dir / 'rock_data'
    analysis_dir = base_dir / 'analysis'
    
    print(f"\n📁 Schema directory: {schema_dir}")
    print(f"📁 Analysis directory: {analysis_dir}")
    
    loader = ROCKDataLoader(schema_dir, analysis_dir)
    
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    # Test 1: Base Skills
    print("\n" + "-" * 70)
    print("TEST 1: Base Skills")
    print("-" * 70)
    try:
        base_skills = loader.load_base_skills()
        if not base_skills.empty:
            count = len(base_skills)
            total_rock = base_skills['rock_skills_count'].sum()
            avg_redundancy = total_rock / count if count > 0 else 0
            print(f"✅ PASSED: Loaded {count} base skills")
            print(f"   - Total ROCK skills: {total_rock}")
            print(f"   - Average redundancy: {avg_redundancy:.2f}x")
            results["passed"].append("Base Skills")
        else:
            print("⚠️  WARNING: Base skills DataFrame is empty")
            results["warnings"].append("Base Skills (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"Base Skills: {e}")
    
    # Test 2: Specifications
    print("\n" + "-" * 70)
    print("TEST 2: Skill Specifications")
    print("-" * 70)
    try:
        specifications = loader.load_skill_specifications()
        if not specifications.empty:
            count = len(specifications)
            # Check key columns
            key_cols = ['text_type', 'cognitive_demand', 'task_complexity']
            present_cols = [col for col in key_cols if col in specifications.columns]
            print(f"✅ PASSED: Loaded {count} skills with specifications")
            print(f"   - Key columns present: {len(present_cols)}/{len(key_cols)}")
            print(f"   - Columns: {', '.join(present_cols)}")
            results["passed"].append("Specifications")
        else:
            print("⚠️  WARNING: Specifications DataFrame is empty")
            results["warnings"].append("Specifications (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"Specifications: {e}")
    
    # Test 3: Master Concepts
    print("\n" + "-" * 70)
    print("TEST 3: Master Concepts")
    print("-" * 70)
    try:
        concepts = loader.load_master_concepts()
        if not concepts.empty:
            count = len(concepts)
            print(f"✅ PASSED: Loaded {count} master concepts")
            if 'SKILL_COUNT' in concepts.columns:
                total_skills = concepts['SKILL_COUNT'].sum()
                print(f"   - Total skills mapped: {total_skills}")
            results["passed"].append("Master Concepts")
        else:
            print("⚠️  WARNING: Master concepts DataFrame is empty")
            results["warnings"].append("Master Concepts (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"Master Concepts: {e}")
    
    # Test 4: Skill-Concept Mappings
    print("\n" + "-" * 70)
    print("TEST 4: Skill-Concept Mappings")
    print("-" * 70)
    try:
        mappings = loader.load_skill_master_concept_mapping()
        if not mappings.empty:
            count = len(mappings)
            unique_skills = mappings['SKILL_ID'].nunique() if 'SKILL_ID' in mappings.columns else 0
            print(f"✅ PASSED: Loaded {count} mapping records")
            print(f"   - Unique skills: {unique_skills}")
            results["passed"].append("Skill-Concept Mappings")
        else:
            print("⚠️  WARNING: Mappings DataFrame is empty")
            results["warnings"].append("Skill-Concept Mappings (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"Skill-Concept Mappings: {e}")
    
    # Test 5: Taxonomy
    print("\n" + "-" * 70)
    print("TEST 5: Science of Reading Taxonomy")
    print("-" * 70)
    try:
        taxonomy = loader.load_sor_taxonomy()
        if not taxonomy.empty:
            count = len(taxonomy)
            strands = taxonomy['Strand'].nunique() if 'Strand' in taxonomy.columns else 0
            print(f"✅ PASSED: Loaded {count} taxonomy entries")
            print(f"   - Unique strands: {strands}")
            results["passed"].append("SoR Taxonomy")
        else:
            print("⚠️  WARNING: Taxonomy DataFrame is empty")
            results["warnings"].append("SoR Taxonomy (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"SoR Taxonomy: {e}")
    
    # Test 6: ROCK Skills
    print("\n" + "-" * 70)
    print("TEST 6: ROCK Skills Schema")
    print("-" * 70)
    try:
        skills = loader.load_skills()
        if not skills.empty:
            count = len(skills)
            print(f"✅ PASSED: Loaded {count} ROCK skills")
            results["passed"].append("ROCK Skills")
        else:
            print("⚠️  WARNING: ROCK skills DataFrame is empty")
            results["warnings"].append("ROCK Skills (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"ROCK Skills: {e}")
    
    # Test 7: Standard Sets
    print("\n" + "-" * 70)
    print("TEST 7: Standard Sets")
    print("-" * 70)
    try:
        standard_sets = loader.load_standard_sets()
        if not standard_sets.empty:
            count = len(standard_sets)
            authorities = standard_sets['EDUCATION_AUTHORITY'].nunique() if 'EDUCATION_AUTHORITY' in standard_sets.columns else 0
            print(f"✅ PASSED: Loaded {count} standard sets")
            print(f"   - Unique authorities: {authorities}")
            results["passed"].append("Standard Sets")
        else:
            print("⚠️  WARNING: Standard sets DataFrame is empty")
            results["warnings"].append("Standard Sets (empty)")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results["failed"].append(f"Standard Sets: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"\n✅ PASSED: {len(results['passed'])} tests")
    for item in results['passed']:
        print(f"   - {item}")
    
    if results['warnings']:
        print(f"\n⚠️  WARNINGS: {len(results['warnings'])} items")
        for item in results['warnings']:
            print(f"   - {item}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])} tests")
        for item in results['failed']:
            print(f"   - {item}")
    
    print("\n" + "=" * 70)
    
    if results['failed']:
        print("❌ VERIFICATION FAILED - Fix errors before demo")
        return False
    elif results['warnings'] and not results['passed']:
        print("⚠️  VERIFICATION INCOMPLETE - Some data files may be missing")
        return False
    else:
        print("✅ VERIFICATION PASSED - App is ready for demo!")
        return True

if __name__ == "__main__":
    success = verify_data_loading()
    sys.exit(0 if success else 1)

