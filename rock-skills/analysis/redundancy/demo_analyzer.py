"""
Demo Analyzer Script

Quick demo script to test the redundancy system on the filtered dataset.
Processes a sample of skills to demonstrate the complete pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis.redundancy.redundancy_analyzer import RedundancyAnalyzer, load_enhanced_metadata

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run demo analysis on filtered dataset."""
    
    print("=" * 70)
    print("SKILL REDUNDANCY SYSTEM - DEMO")
    print("=" * 70)
    print()
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    metadata_path = project_root / "analysis" / "outputs" / "filtered_enhanced_metadata"
    
    # Find the most recent metadata file
    metadata_files = sorted(metadata_path.glob("skill_metadata_enhanced_*.csv"), reverse=True)
    
    if not metadata_files:
        print("❌ Error: No enhanced metadata found!")
        print(f"   Expected location: {metadata_path}")
        print()
        print("Please run the enhanced metadata extractor first:")
        print("  cd analysis/scripts")
        print("  python3 enhanced_metadata_extractor.py --input ../../rock_data/skill_list_filtered_data_set.csv --output-dir ../outputs/filtered_enhanced_metadata")
        return
    
    metadata_file = metadata_files[0]
    print(f"📂 Loading metadata from: {metadata_file.name}")
    
    # Load metadata
    try:
        metadata_df = load_enhanced_metadata(metadata_file)
        print(f"✓ Loaded {len(metadata_df)} skills with enhanced metadata")
        print()
    except Exception as e:
        print(f"❌ Error loading metadata: {e}")
        return
    
    # Validate metadata
    print("🔍 Validating metadata...")
    required_fields = ['SKILL_ID', 'SKILL_NAME', 'actions', 'targets', 'key_concepts']
    missing_fields = [f for f in required_fields if f not in metadata_df.columns]
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return
    
    # Check data quality
    actions_filled = metadata_df['actions'].notna().sum()
    targets_filled = metadata_df['targets'].notna().sum()
    print(f"   Actions filled: {actions_filled}/{len(metadata_df)} ({actions_filled/len(metadata_df):.1%})")
    print(f"   Targets filled: {targets_filled}/{len(metadata_df)} ({targets_filled/len(metadata_df):.1%})")
    print()
    
    # Ask user for sample size
    print("How many skill pairs would you like to analyze?")
    print("  - Enter a number (e.g., 50, 100, 200)")
    print("  - Enter 'all' to process all pairs (may take a while)")
    print("  - Enter 'demo' for quick demo (20 pairs)")
    print()
    
    user_input = input("Your choice [demo]: ").strip().lower() or "demo"
    
    if user_input == "all":
        max_pairs = None
        print("Processing ALL pairs...")
    elif user_input == "demo":
        max_pairs = 20
        print("Running quick demo with 20 pairs...")
    else:
        try:
            max_pairs = int(user_input)
            print(f"Processing {max_pairs} pairs...")
        except ValueError:
            print("Invalid input, using demo mode (20 pairs)")
            max_pairs = 20
    
    print()
    
    # Output directory
    output_dir = project_root / "analysis" / "redundancy" / "outputs" / "relationships"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    print("🚀 Starting redundancy analysis...")
    print()
    
    try:
        analyzer = RedundancyAnalyzer()
        relationships, recommendations = analyzer.analyze_skills(
            metadata_df,
            semantic_embeddings=None,  # Will skip semantic similarity for speed
            output_dir=output_dir,
            max_pairs=max_pairs
        )
        
        print()
        print("=" * 70)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        print()
        
        # Summary statistics
        print("📊 RESULTS SUMMARY")
        print("-" * 70)
        print(f"Total relationships analyzed: {len(relationships)}")
        print(f"Total recommendations generated: {len(recommendations)}")
        print()
        
        # Relationship types
        from collections import Counter
        rel_types = Counter(r.relationship_type.value for r in relationships)
        print("Relationship Types:")
        for rtype in ['TRUE_DUPLICATE', 'SPECIFICATION_VARIANT', 'PREREQUISITE', 
                     'PROGRESSION', 'COMPLEMENTARY', 'AMBIGUOUS', 'DISTINCT']:
            count = rel_types.get(rtype, 0)
            if count > 0:
                pct = count / len(relationships) * 100
                print(f"  {rtype:25s}: {count:3d} ({pct:5.1f}%)")
        print()
        
        # Priority distribution
        priorities = Counter(r.priority for r in recommendations)
        print("Priority Distribution:")
        for priority in ['P0', 'P1', 'P2', 'P3']:
            count = priorities.get(priority, 0)
            if count > 0:
                pct = count / len(recommendations) * 100
                emoji = {'P0': '🔴', 'P1': '🟠', 'P2': '🟡', 'P3': '🟢'}[priority]
                print(f"  {emoji} {priority}: {count:3d} ({pct:5.1f}%)")
        print()
        
        # Top recommendations
        print("🎯 TOP 5 HIGH-PRIORITY RECOMMENDATIONS:")
        print("-" * 70)
        
        top_recs = sorted(recommendations, key=lambda r: r.priority_score, reverse=True)[:5]
        
        for i, rec in enumerate(top_recs, 1):
            rel = [r for r in relationships if r.relationship_id == rec.relationship_id][0]
            print(f"\n{i}. [{rec.priority}] {rel.relationship_type.value}")
            print(f"   Skill A: {rel.skill_a_name}")
            print(f"   Skill B: {rel.skill_b_name}")
            print(f"   Action: {rec.action.value}")
            print(f"   Rationale: {rec.rationale}")
            print(f"   Composite Score: {rel.similarity_scores['composite']:.3f}")
        
        print()
        print("=" * 70)
        print("📁 Results saved to:")
        print(f"   {output_dir}")
        print()
        print("🌐 To review in UI, run:")
        print("   cd poc")
        print("   streamlit run skill_bridge_app.py")
        print("   Then navigate to 'Redundancy Review' page")
        print("=" * 70)
        
    except Exception as e:
        print()
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

