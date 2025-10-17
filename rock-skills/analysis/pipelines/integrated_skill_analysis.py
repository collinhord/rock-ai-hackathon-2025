#!/usr/bin/env python3
"""
Integrated Skill Analysis Pipeline
ROCK AI Hackathon 2025

Single-command pipeline integrating three levels:
1. MICRO: Metadata extraction (Jess)
2. MID: Redundancy detection (Savannah)
3. MACRO: Master concept mapping (Collin)

Usage:
    # Run full pipeline
    python3 integrated_skill_analysis.py --input ../../rock_schemas/skill_list_filtered_data_set.csv
    
    # Run with custom output directory
    python3 integrated_skill_analysis.py --input skills.csv --output ./results
    
    # Skip levels that are already complete
    python3 integrated_skill_analysis.py --input skills.csv --skip-micro --skip-mid
"""

import pandas as pd
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from spacy_processor import SkillProcessor
    SPACY_AVAILABLE = True
except ImportError:
    print("Warning: spacy_processor not available")
    SPACY_AVAILABLE = False


class IntegratedSkillPipeline:
    """
    Integrated three-level skill analysis pipeline.
    
    Connects MICRO → MID → MACRO processing in a single workflow.
    """
    
    def __init__(self, input_file: str, output_dir: Optional[str] = None):
        """Initialize the pipeline."""
        self.input_file = Path(input_file)
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent / "outputs" / "integrated_pipeline"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline results
        self.results = {
            "pipeline_version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "input_file": str(self.input_file),
            "output_dir": str(self.output_dir),
            "levels_completed": []
        }
        
        # Data storage
        self.raw_df = None
        self.enriched_df = None
        self.redundancy_groups = None
        self.master_concepts = None
        
        print("\n" + "="*70)
        print("🚀 INTEGRATED SKILL ANALYSIS PIPELINE")
        print("   ROCK AI Hackathon 2025")
        print("="*70)
    
    def load_data(self) -> pd.DataFrame:
        """Load input skills dataset."""
        print(f"\n📊 Loading dataset from {self.input_file}")
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.raw_df = pd.read_csv(self.input_file)
        print(f"✓ Loaded {len(self.raw_df)} skills")
        
        # Display dataset summary
        print(f"\n📋 Dataset Summary:")
        if 'CONTENT_AREA_SHORT_NAME' in self.raw_df.columns:
            print(f"   Content Areas: {self.raw_df['CONTENT_AREA_SHORT_NAME'].nunique()}")
            for area in self.raw_df['CONTENT_AREA_SHORT_NAME'].unique():
                count = len(self.raw_df[self.raw_df['CONTENT_AREA_SHORT_NAME'] == area])
                print(f"      • {area}: {count} skills")
        
        if 'GRADE_LEVEL_SHORT_NAME' in self.raw_df.columns:
            print(f"   Grade Levels: {sorted(self.raw_df['GRADE_LEVEL_SHORT_NAME'].unique())}")
        
        self.results['input_skills'] = len(self.raw_df)
        return self.raw_df
    
    def run_micro_level(self) -> pd.DataFrame:
        """
        MICRO Level: Metadata Extraction
        
        Extract structured concepts and metadata from skill text.
        """
        print("\n" + "="*70)
        print("🔬 LEVEL 1: MICRO - Metadata Extraction")
        print("="*70)
        
        if not SPACY_AVAILABLE:
            print("⚠️  spaCy processor not available - skipping MICRO level")
            return self.raw_df
        
        start_time = time.time()
        
        # Initialize processor
        try:
            processor = SkillProcessor(model_name='en_core_web_sm')
        except:
            print("⚠️  Could not load spaCy model - skipping MICRO level")
            return self.raw_df
        
        print(f"\n📝 Processing {len(self.raw_df)} skills...")
        
        enriched_skills = []
        stats = {'actions': 0, 'targets': 0, 'qualifiers': 0, 'errors': 0}
        
        for idx, row in self.raw_df.iterrows():
            try:
                concepts = processor.extract_concepts(row['SKILL_NAME'])
                
                enriched = {
                    **row.to_dict(),
                    'concepts_actions': '|'.join(concepts.actions) if concepts.actions else '',
                    'concepts_targets': '|'.join(concepts.targets) if concepts.targets else '',
                    'concepts_qualifiers': '|'.join(concepts.qualifiers) if concepts.qualifiers else '',
                    'cleaned_text': concepts.cleaned_text
                }
                
                enriched_skills.append(enriched)
                
                if concepts.actions:
                    stats['actions'] += 1
                if concepts.targets:
                    stats['targets'] += 1
                if concepts.qualifiers:
                    stats['qualifiers'] += 1
                
                # Progress indicator
                if (idx + 1) % 50 == 0:
                    print(f"   Processed {idx + 1}/{len(self.raw_df)} skills...")
                
            except Exception as e:
                print(f"   ✗ Error processing skill {idx}: {e}")
                stats['errors'] += 1
                enriched_skills.append(row.to_dict())
        
        self.enriched_df = pd.DataFrame(enriched_skills)
        
        # Save enriched dataset
        output_file = self.output_dir / "01_micro_enriched_skills.csv"
        self.enriched_df.to_csv(output_file, index=False)
        
        elapsed = time.time() - start_time
        
        # Results
        total = len(self.enriched_df)
        micro_results = {
            "level": "MICRO",
            "total_processed": total,
            "actions_extracted": stats['actions'],
            "targets_extracted": stats['targets'],
            "qualifiers_extracted": stats['qualifiers'],
            "extraction_rates": {
                "actions": f"{stats['actions']/total*100:.1f}%",
                "targets": f"{stats['targets']/total*100:.1f}%",
                "qualifiers": f"{stats['qualifiers']/total*100:.1f}%"
            },
            "errors": stats['errors'],
            "processing_time_seconds": round(elapsed, 2),
            "output_file": str(output_file)
        }
        
        print(f"\n✓ MICRO Level Complete")
        print(f"   • Actions: {micro_results['extraction_rates']['actions']}")
        print(f"   • Targets: {micro_results['extraction_rates']['targets']}")
        print(f"   • Time: {elapsed:.1f} seconds")
        print(f"   • Output: {output_file}")
        
        self.results['micro'] = micro_results
        self.results['levels_completed'].append('MICRO')
        
        return self.enriched_df
    
    def run_mid_level(self) -> List[Dict]:
        """
        MID Level: Redundancy Detection
        
        Identify redundant skills and group variants.
        """
        print("\n" + "="*70)
        print("🔍 LEVEL 2: MID - Redundancy Detection")
        print("="*70)
        
        if self.enriched_df is None:
            print("⚠️  No enriched data available - loading from file or using raw data")
            micro_output = self.output_dir / "01_micro_enriched_skills.csv"
            if micro_output.exists():
                self.enriched_df = pd.read_csv(micro_output)
            else:
                self.enriched_df = self.raw_df
        
        start_time = time.time()
        
        print(f"\n🔍 Analyzing {len(self.enriched_df)} skills for redundancies...")
        
        redundancy_groups = []
        processed_skills = set()
        
        # Group by content area and skill area for efficiency
        grouping_cols = []
        if 'CONTENT_AREA_SHORT_NAME' in self.enriched_df.columns:
            grouping_cols.append('CONTENT_AREA_SHORT_NAME')
        if 'SKILL_AREA_NAME' in self.enriched_df.columns:
            grouping_cols.append('SKILL_AREA_NAME')
        
        if not grouping_cols:
            groups = [('All', self.enriched_df)]
        else:
            groups = self.enriched_df.groupby(grouping_cols)
        
        for group_key, group in groups:
            if len(group) < 2:
                continue
            
            group_name = group_key if isinstance(group_key, str) else ' - '.join(str(k) for k in group_key)
            print(f"\n   Analyzing: {group_name} ({len(group)} skills)")
            
            # Simple similarity detection
            for idx1, skill1 in group.iterrows():
                if idx1 in processed_skills:
                    continue
                
                similar_skills = [skill1.to_dict()]
                
                for idx2, skill2 in group.iterrows():
                    if idx2 <= idx1 or idx2 in processed_skills:
                        continue
                    
                    if self._check_similarity(skill1, skill2):
                        similar_skills.append(skill2.to_dict())
                        processed_skills.add(idx2)
                
                if len(similar_skills) > 1:
                    redundancy_groups.append({
                        "group_id": f"RED-{len(redundancy_groups)+1:03d}",
                        "group_key": group_name,
                        "skill_count": len(similar_skills),
                        "skill_ids": [s['SKILL_ID'] for s in similar_skills],
                        "skill_names": [s['SKILL_NAME'] for s in similar_skills]
                    })
                    processed_skills.add(idx1)
        
        self.redundancy_groups = redundancy_groups
        
        # Save redundancy report
        output_file = self.output_dir / "02_mid_redundancy_groups.json"
        with open(output_file, 'w') as f:
            json.dump({
                "total_skills": len(self.enriched_df),
                "redundancy_groups": redundancy_groups,
                "total_groups": len(redundancy_groups),
                "skills_in_groups": sum(g['skill_count'] for g in redundancy_groups),
                "unique_concepts_estimated": len(self.enriched_df) - sum(g['skill_count'] - 1 for g in redundancy_groups)
            }, f, indent=2)
        
        elapsed = time.time() - start_time
        
        # Results
        mid_results = {
            "level": "MID",
            "total_skills_analyzed": len(self.enriched_df),
            "redundancy_groups_found": len(redundancy_groups),
            "skills_in_groups": sum(g['skill_count'] for g in redundancy_groups),
            "unique_concepts_estimated": len(self.enriched_df) - sum(g['skill_count'] - 1 for g in redundancy_groups),
            "redundancy_rate": f"{(sum(g['skill_count'] - 1 for g in redundancy_groups) / len(self.enriched_df) * 100):.1f}%",
            "processing_time_seconds": round(elapsed, 2),
            "output_file": str(output_file)
        }
        
        print(f"\n✓ MID Level Complete")
        print(f"   • Groups found: {mid_results['redundancy_groups_found']}")
        print(f"   • Redundancy rate: {mid_results['redundancy_rate']}")
        print(f"   • Time: {elapsed:.1f} seconds")
        print(f"   • Output: {output_file}")
        
        self.results['mid'] = mid_results
        self.results['levels_completed'].append('MID')
        
        return redundancy_groups
    
    def _check_similarity(self, skill1: pd.Series, skill2: pd.Series) -> bool:
        """Check if two skills are similar enough to be grouped."""
        # Same grade level check
        if 'GRADE_LEVEL_SHORT_NAME' in skill1.index:
            if skill1['GRADE_LEVEL_SHORT_NAME'] != skill2['GRADE_LEVEL_SHORT_NAME']:
                return False
        
        # Text-based similarity (simple word overlap)
        words1 = set(str(skill1['SKILL_NAME']).lower().split())
        words2 = set(str(skill2['SKILL_NAME']).lower().split())
        
        stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'and', 'or', 'from', 'using'}
        words1 = words1 - stopwords
        words2 = words2 - stopwords
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2) / len(words1 | words2)
        
        # Concept-based enhancement (if concepts available)
        if 'concepts_actions' in skill1.index and skill1['concepts_actions']:
            actions1 = set(str(skill1['concepts_actions']).split('|'))
            actions2 = set(str(skill2['concepts_actions']).split('|'))
            
            if actions1 and actions2:
                action_overlap = len(actions1 & actions2) / len(actions1 | actions2)
                overlap = 0.7 * overlap + 0.3 * action_overlap
        
        return overlap > 0.5
    
    def run_macro_level(self) -> List[Dict]:
        """
        MACRO Level: Master Concept Mapping
        
        Create master concepts from redundancy groups.
        """
        print("\n" + "="*70)
        print("🎯 LEVEL 3: MACRO - Master Concept Mapping")
        print("="*70)
        
        if self.redundancy_groups is None:
            print("⚠️  No redundancy groups available - loading from file")
            mid_output = self.output_dir / "02_mid_redundancy_groups.json"
            if mid_output.exists():
                with open(mid_output) as f:
                    data = json.load(f)
                    self.redundancy_groups = data['redundancy_groups']
            else:
                print("⚠️  MID output not found - skipping MACRO level")
                return []
        
        start_time = time.time()
        
        print(f"\n🎯 Creating master concepts from {len(self.redundancy_groups)} groups...")
        
        master_concepts = []
        
        # Create master concept for each redundancy group
        for group in self.redundancy_groups:
            master_concepts.append({
                "master_concept_id": f"MC-{len(master_concepts)+1:03d}",
                "base_skill_name": group['group_key'],
                "rock_skill_count": group['skill_count'],
                "rock_skill_mappings": group['skill_ids'],
                "variant_group_id": group['group_id'],
                "concept_type": "grouped"
            })
        
        # Add individual concepts for ungrouped skills
        if self.enriched_df is not None:
            grouped_skill_ids = set()
            for group in self.redundancy_groups:
                grouped_skill_ids.update(group['skill_ids'])
            
            ungrouped = self.enriched_df[~self.enriched_df['SKILL_ID'].isin(grouped_skill_ids)]
            
            for _, skill in ungrouped.iterrows():
                skill_area = skill.get('SKILL_AREA_NAME', 'Unknown')
                content_area = skill.get('CONTENT_AREA_SHORT_NAME', 'Unknown')
                
                master_concepts.append({
                    "master_concept_id": f"MC-{len(master_concepts)+1:03d}",
                    "base_skill_name": f"{content_area}: {skill_area}",
                    "rock_skill_count": 1,
                    "rock_skill_mappings": [skill['SKILL_ID']],
                    "variant_group_id": None,
                    "concept_type": "individual"
                })
        
        self.master_concepts = master_concepts
        
        # Save master concepts
        output_file = self.output_dir / "03_macro_master_concepts.json"
        with open(output_file, 'w') as f:
            json.dump({
                "total_master_concepts": len(master_concepts),
                "grouped_concepts": sum(1 for c in master_concepts if c['concept_type'] == 'grouped'),
                "individual_concepts": sum(1 for c in master_concepts if c['concept_type'] == 'individual'),
                "total_rock_skills": sum(c['rock_skill_count'] for c in master_concepts),
                "master_concepts": master_concepts
            }, f, indent=2)
        
        elapsed = time.time() - start_time
        
        # Results
        macro_results = {
            "level": "MACRO",
            "master_concepts_created": len(master_concepts),
            "grouped_concepts": sum(1 for c in master_concepts if c['concept_type'] == 'grouped'),
            "individual_concepts": sum(1 for c in master_concepts if c['concept_type'] == 'individual'),
            "total_rock_skills_mapped": sum(c['rock_skill_count'] for c in master_concepts),
            "reduction_ratio": f"{(1 - len(master_concepts) / self.results.get('input_skills', len(master_concepts))) * 100:.1f}%",
            "processing_time_seconds": round(elapsed, 2),
            "output_file": str(output_file)
        }
        
        print(f"\n✓ MACRO Level Complete")
        print(f"   • Master concepts: {macro_results['master_concepts_created']}")
        print(f"   • Reduction: {macro_results['reduction_ratio']}")
        print(f"   • Time: {elapsed:.1f} seconds")
        print(f"   • Output: {output_file}")
        
        self.results['macro'] = macro_results
        self.results['levels_completed'].append('MACRO')
        
        return master_concepts
    
    def generate_final_report(self):
        """Generate comprehensive pipeline report."""
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        
        # Save complete results
        summary_file = self.output_dir / "pipeline_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n🎯 Three-Level Pipeline Results:")
        print(f"\n   INPUT:")
        print(f"      • Skills: {self.results.get('input_skills', 'N/A')}")
        print(f"      • Source: {Path(self.results['input_file']).name}")
        
        if 'micro' in self.results:
            print(f"\n   🔬 MICRO Level:")
            print(f"      • Actions: {self.results['micro']['extraction_rates']['actions']}")
            print(f"      • Targets: {self.results['micro']['extraction_rates']['targets']}")
            print(f"      • Time: {self.results['micro']['processing_time_seconds']}s")
        
        if 'mid' in self.results:
            print(f"\n   🔍 MID Level:")
            print(f"      • Groups: {self.results['mid']['redundancy_groups_found']}")
            print(f"      • Redundancy: {self.results['mid']['redundancy_rate']}")
            print(f"      • Time: {self.results['mid']['processing_time_seconds']}s")
        
        if 'macro' in self.results:
            print(f"\n   🎯 MACRO Level:")
            print(f"      • Concepts: {self.results['macro']['master_concepts_created']}")
            print(f"      • Reduction: {self.results['macro']['reduction_ratio']}")
            print(f"      • Time: {self.results['macro']['processing_time_seconds']}s")
        
        total_time = sum(
            self.results.get(level, {}).get('processing_time_seconds', 0)
            for level in ['micro', 'mid', 'macro']
        )
        
        print(f"\n   PIPELINE:")
        print(f"      • Total time: {total_time:.1f}s")
        print(f"      • Levels completed: {', '.join(self.results['levels_completed'])}")
        print(f"      • Summary: {summary_file}")
        
        print("\n" + "="*70)
        print("✅ INTEGRATED PIPELINE COMPLETE")
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Integrated three-level skill analysis pipeline")
    parser.add_argument('--input', required=True, help="Input CSV file with ROCK skills")
    parser.add_argument('--output', help="Output directory (default: outputs/integrated_pipeline)")
    parser.add_argument('--skip-micro', action='store_true', help="Skip MICRO level")
    parser.add_argument('--skip-mid', action='store_true', help="Skip MID level")
    parser.add_argument('--skip-macro', action='store_true', help="Skip MACRO level")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = IntegratedSkillPipeline(args.input, args.output)
    
    # Load data
    pipeline.load_data()
    
    # Run levels
    if not args.skip_micro:
        pipeline.run_micro_level()
    
    if not args.skip_mid:
        pipeline.run_mid_level()
    
    if not args.skip_macro:
        pipeline.run_macro_level()
    
    # Generate final report
    pipeline.generate_final_report()


if __name__ == "__main__":
    main()

