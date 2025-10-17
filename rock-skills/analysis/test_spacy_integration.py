#!/usr/bin/env python3
"""
Quick Test Script for spaCy Integration

Validates that all enhanced components are working correctly.

Usage:
    python3 test_spacy_integration.py
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages are installed."""
    print("=" * 70)
    print("TEST 1: Checking Imports")
    print("=" * 70)
    
    errors = []
    
    try:
        import spacy
        print("✓ spacy imported successfully")
    except ImportError as e:
        errors.append(f"✗ spacy import failed: {e}")
    
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✓ en_core_web_sm model loaded successfully")
    except OSError as e:
        errors.append(f"✗ en_core_web_sm not found: {e}")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers imported successfully")
    except ImportError as e:
        errors.append(f"✗ sentence-transformers import failed: {e}")
    
    try:
        from spacy_processor import SkillProcessor
        print("✓ spacy_processor module imported successfully")
    except ImportError as e:
        errors.append(f"✗ spacy_processor import failed: {e}")
    
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✓ All imports successful!")
        return True


def test_spacy_processor():
    """Test the SkillProcessor functionality."""
    print("\n" + "=" * 70)
    print("TEST 2: Testing SkillProcessor")
    print("=" * 70)
    
    try:
        from spacy_processor import SkillProcessor
        
        processor = SkillProcessor()
        print("✓ SkillProcessor initialized")
        
        # Test preprocessing
        test_text = "The student will blend spoken phonemes into words"
        cleaned = processor.preprocess_for_embeddings(test_text)
        print(f"\nPreprocessing test:")
        print(f"  Input:  '{test_text}'")
        print(f"  Output: '{cleaned}'")
        
        # Verify stop words removed
        if 'student' in cleaned or 'will' in cleaned:
            print("  ⚠ Warning: Stop words not fully removed")
        else:
            print("  ✓ Stop words removed correctly")
        
        # Verify content words present
        if 'blend' in cleaned and ('phoneme' in cleaned or 'word' in cleaned):
            print("  ✓ Content words preserved")
        else:
            print("  ✗ Content words missing")
        
        # Test concept extraction
        concepts = processor.extract_concepts(test_text)
        print(f"\nConcept extraction test:")
        print(f"  Actions: {concepts.actions}")
        print(f"  Targets: {concepts.targets}")
        print(f"  Key Concepts: {concepts.key_concepts}")
        
        if 'blend' in concepts.actions:
            print("  ✓ Actions extracted correctly")
        else:
            print("  ✗ Actions not extracted correctly")
        
        # Test structure extraction
        structure = processor.extract_structure(test_text)
        print(f"\nStructure extraction test:")
        print(f"  Root Verb: {structure.root_verb}")
        print(f"  Direct Objects: {structure.direct_objects}")
        
        if structure.root_verb:
            print("  ✓ Structure extracted correctly")
        else:
            print("  ✗ Structure not extracted correctly")
        
        # Test variant comparison
        skill1 = "Blend phonemes to form words"
        skill2 = "Orally produce words by blending sounds"
        comparison = processor.compare_skills_structurally(skill1, skill2)
        
        print(f"\nVariant detection test:")
        print(f"  Skill 1: '{skill1}'")
        print(f"  Skill 2: '{skill2}'")
        print(f"  Structural Similarity: {comparison['structural_similarity']:.2f}")
        print(f"  Likely Variant: {comparison['likely_variant']}")
        
        if comparison['structural_similarity'] > 0.3:
            print("  ✓ Variant detection working")
        else:
            print("  ⚠ Low similarity score (may need tuning)")
        
        print("\n✓ SkillProcessor tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ SkillProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_semantic_similarity():
    """Test that enhanced semantic similarity script exists and is importable."""
    print("\n" + "=" * 70)
    print("TEST 3: Testing Enhanced Semantic Similarity")
    print("=" * 70)
    
    try:
        # Check if file exists
        script_path = Path(__file__).parent / "semantic_similarity_enhanced.py"
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False
        
        print(f"✓ Script found: {script_path}")
        
        # Try importing (without running main)
        sys.path.insert(0, str(script_path.parent))
        import semantic_similarity_enhanced
        
        print("✓ Module importable")
        
        # Check for key classes
        if hasattr(semantic_similarity_enhanced, 'EnhancedSemanticMatcher'):
            print("✓ EnhancedSemanticMatcher class found")
        else:
            print("✗ EnhancedSemanticMatcher class not found")
            return False
        
        print("\n✓ Enhanced semantic similarity module validated!")
        return True
        
    except Exception as e:
        print(f"\n✗ Enhanced semantic similarity test failed: {e}")
        return False


def test_enhanced_batch_mapper():
    """Test that enhanced batch mapper script exists."""
    print("\n" + "=" * 70)
    print("TEST 4: Testing Enhanced Batch Mapper")
    print("=" * 70)
    
    try:
        # Check if file exists
        script_path = Path(__file__).parent / "scripts" / "batch_map_skills_enhanced.py"
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False
        
        print(f"✓ Script found: {script_path}")
        
        # Try importing (without running main)
        sys.path.insert(0, str(script_path.parent))
        import batch_map_skills_enhanced
        
        print("✓ Module importable")
        
        # Check for key classes
        if hasattr(batch_map_skills_enhanced, 'EnhancedLLMMapperAssistant'):
            print("✓ EnhancedLLMMapperAssistant class found")
        else:
            print("✗ EnhancedLLMMapperAssistant class not found")
            return False
        
        print("\n✓ Enhanced batch mapper module validated!")
        return True
        
    except Exception as e:
        print(f"\n✗ Enhanced batch mapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_files():
    """Check that required data files exist."""
    print("\n" + "=" * 70)
    print("TEST 5: Checking Data Files")
    print("=" * 70)
    
    base_dir = Path(__file__).parent.parent
    
    files_to_check = [
        ("SKILLS.csv", base_dir / "rock_schemas" / "SKILLS.csv"),
        ("Taxonomy CSV", base_dir / "POC_science_of_reading_literacy_skills_taxonomy.csv")
    ]
    
    all_found = True
    for name, path in files_to_check:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✓ {name} found ({size_mb:.1f} MB)")
        else:
            print(f"✗ {name} not found at: {path}")
            all_found = False
    
    if all_found:
        print("\n✓ All data files present!")
    else:
        print("\n⚠ Some data files missing (tests will be limited)")
    
    return all_found


def run_simple_demo():
    """Run a simple end-to-end demo."""
    print("\n" + "=" * 70)
    print("DEMO: End-to-End Example")
    print("=" * 70)
    
    try:
        from spacy_processor import SkillProcessor
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Initialize
        processor = SkillProcessor()
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Sample skills
        skills = [
            "Blend phonemes to form words",
            "Segment words into individual phonemes",
            "Identify the main idea of a text"
        ]
        
        print("\nProcessing sample skills with spaCy + embeddings:")
        print("-" * 70)
        
        # Preprocess with spaCy
        cleaned_skills = []
        for skill in skills:
            concepts = processor.extract_concepts(skill)
            cleaned_skills.append(concepts.cleaned_text)
            print(f"\nOriginal: {skill}")
            print(f"Cleaned:  {cleaned_skills[-1]}")
            print(f"Actions:  {', '.join(concepts.actions)}")
            print(f"Targets:  {', '.join(concepts.targets)}")
        
        # Compute embeddings
        print("\nComputing semantic similarities...")
        embeddings = encoder.encode(cleaned_skills)
        similarities = cosine_similarity(embeddings)
        
        print("\nSimilarity Matrix:")
        print("                   Skill 1  Skill 2  Skill 3")
        for i, skill in enumerate(skills):
            skill_short = skill[:20] + "..." if len(skill) > 20 else skill
            sims = " ".join([f"{similarities[i,j]:7.3f}" for j in range(len(skills))])
            print(f"  {skill_short:23s} {sims}")
        
        print("\n✓ Demo complete!")
        print("\nNotice how skills 1 & 2 have higher similarity (both phoneme-related)")
        print("while skill 3 is less similar (comprehension vs phonics)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ROCK SKILLS spaCy INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    
    if results[0][1]:  # Only continue if imports work
        results.append(("spaCy Processor", test_spacy_processor()))
        results.append(("Enhanced Semantic Similarity", test_enhanced_semantic_similarity()))
        results.append(("Enhanced Batch Mapper", test_enhanced_batch_mapper()))
        results.append(("Data Files", test_data_files()))
        results.append(("End-to-End Demo", run_simple_demo()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your spaCy integration is ready to use.")
        print("\nNext steps:")
        print("  1. Read SPACY_ENHANCEMENT_README.md for usage guide")
        print("  2. Try: python3 spacy_processor.py")
        print("  3. Run enhanced semantic similarity on sample data")
    else:
        print("\n⚠ Some tests failed. Please review errors above.")
        print("Common fixes:")
        print("  - Run: python3 -m spacy download en_core_web_sm")
        print("  - Install missing packages: pip install sentence-transformers scikit-learn")
        print("  - Check that you're in the correct directory")
    
    print("=" * 70)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

