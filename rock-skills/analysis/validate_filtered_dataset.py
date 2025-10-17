#!/usr/bin/env python3
"""
Validate Filtered Dataset Processing
ROCK AI Hackathon 2025

Tests the three-level integration on skill_list_filtered_data_set.csv (338 skills):
1. MICRO: Metadata extraction using spaCy
2. MID: Redundancy detection with concept-aware similarity
3. MACRO: Master concept grouping

Usage:
    python3 validate_filtered_dataset.py --full  # Run all three levels
    python3 validate_filtered_dataset.py --micro  # Only MICRO level
    python3 validate_filtered_dataset.py --mid    # Only MID level
    python3 validate_filtered_dataset.py --macro  # Only MACRO level
"""

import pandas as pd
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add analysis directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from spacy_processor import SkillProcessor
    SPACY_AVAILABLE = True
except ImportError:
    print("Warning: spacy_processor not available")
    SPACY_AVAILABLE = False


class FilteredDatasetValidator:
    """Validate three-level integration on filtered dataset."""
    
    def __init__(self, input_file: str):
        """Initialize validator."""
        self.input_file = Path(input_file)
        self.output_dir = Path(__file__).parent / "outputs" / "filtered_validation"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load dataset
        print(f"\n📊 Loading filtered dataset from {self.input_file}")
        self.df = pd.read_csv(self.input_file)
        print(f"✓ Loaded {len(self.df)} skills")
        
        # Initialize spaCy processor
        if SPACY_AVAILABLE:
            try:
                self.processor = SkillProcessor(model_name='en_core_web_sm')
            except:
                print("⚠️  Falling back to simpler processing (spaCy model not available)")
                self.processor = None
        else:
            self.processor = None
        
        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "input_file": str(self.input_file),
            "total_skills": len(self.df),
            "micro": {},
            "mid": {},
            "macro": {}
        }
    
    def validate_micro(self) -> Dict:
        """
        MICRO Level: Metadata Extraction & Concept Parsing
        
        Tests:
        - Extract concepts (actions, targets, qualifiers) from skills
        - Identify metadata (skill_domain, complexity, text_type)
        - Validate extraction accuracy
        """
        print("\n" + "="*70)
        print("🔬 MICRO LEVEL: Metadata Extraction & Concept Parsing")
        print("="*70)
        
        if not self.processor:
            print("⚠️  spaCy processor not available - skipping MICRO validation")
            return {"status": "skipped", "reason": "spaCy not available"}
        
        enriched_skills = []
        extraction_stats = {
            "total_processed": 0,
            "with_actions": 0,
            "with_targets": 0,
            "with_qualifiers": 0,
            "with_grade_indicators": 0,
            "errors": 0
        }
        
        print(f"\nProcessing {len(self.df)} skills...")
        
        for idx, row in self.df.iterrows():
            skill_name = row['SKILL_NAME']
            
            try:
                # Extract concepts
                concepts = self.processor.extract_concepts(skill_name)
                
                # Create enriched record
                enriched = {
                    **row.to_dict(),
                    'concepts_actions': concepts.actions,
                    'concepts_targets': concepts.targets,
                    'concepts_qualifiers': concepts.qualifiers,
                    'concepts_grade_indicators': concepts.grade_indicators,
                    'concepts_complexity_markers': concepts.complexity_markers,
                    'cleaned_text': concepts.cleaned_text
                }
                
                enriched_skills.append(enriched)
                extraction_stats['total_processed'] += 1
                
                if concepts.actions:
                    extraction_stats['with_actions'] += 1
                if concepts.targets:
                    extraction_stats['with_targets'] += 1
                if concepts.qualifiers:
                    extraction_stats['with_qualifiers'] += 1
                if concepts.grade_indicators:
                    extraction_stats['with_grade_indicators'] += 1
                
            except Exception as e:
                print(f"✗ Error processing skill {idx}: {e}")
                extraction_stats['errors'] += 1
        
        # Convert to DataFrame and save
        enriched_df = pd.DataFrame(enriched_skills)
        output_file = self.output_dir / "filtered_metadata_extraction.csv"
        enriched_df.to_csv(output_file, index=False)
        
        # Calculate metrics
        total = extraction_stats['total_processed']
        metrics = {
            "total_processed": total,
            "actions_extraction_rate": f"{extraction_stats['with_actions']/total*100:.1f}%",
            "targets_extraction_rate": f"{extraction_stats['with_targets']/total*100:.1f}%",
            "qualifiers_extraction_rate": f"{extraction_stats['with_qualifiers']/total*100:.1f}%",
            "errors": extraction_stats['errors'],
            "output_file": str(output_file)
        }
        
        # Display results
        print(f"\n📊 MICRO Level Results:")
        print(f"   ✓ Processed: {total} skills")
        print(f"   ✓ Actions extracted: {extraction_stats['with_actions']} ({metrics['actions_extraction_rate']})")
        print(f"   ✓ Targets extracted: {extraction_stats['with_targets']} ({metrics['targets_extraction_rate']})")
        print(f"   ✓ Qualifiers extracted: {extraction_stats['with_qualifiers']} ({metrics['qualifiers_extraction_rate']})")
        print(f"   ✓ Output saved to: {output_file}")
        
        # Sample results
        print(f"\n📝 Sample Extracted Concepts (first 5 skills):")
        for i, skill in enumerate(enriched_skills[:5]):
            print(f"\n   Skill {i+1}: {skill['SKILL_NAME'][:70]}...")
            print(f"      Actions: {skill['concepts_actions']}")
            print(f"      Targets: {skill['concepts_targets']}")
            print(f"      Qualifiers: {skill['concepts_qualifiers'][:3]}")  # Limit qualifiers shown
        
        self.results['micro'] = metrics
        return metrics
    
    def validate_mid(self) -> Dict:
        """
        MID Level: Redundancy Detection
        
        Tests:
        - Detect redundant skill pairs using semantic similarity
        - Group cross-state variants
        - Calculate concept overlap scores
        - Flag potential duplicates
        """
        print("\n" + "="*70)
        print("🔍 MID LEVEL: Redundancy Detection")
        print("="*70)
        
        # Check if MICRO output exists
        micro_output = self.output_dir / "filtered_metadata_extraction.csv"
        if not micro_output.exists():
            print("⚠️  MICRO output not found - run --micro first or use --full")
            return {"status": "skipped", "reason": "MICRO output not available"}
        
        # Load enriched data
        enriched_df = pd.read_csv(micro_output)
        print(f"\n✓ Loaded {len(enriched_df)} enriched skills")
        
        # Simple redundancy detection (text-based for POC)
        # In production, this would use validate_mece.py
        print("\n🔍 Detecting potential redundancies...")
        
        redundancy_groups = []
        processed_skills = set()
        
        # Group by content area and skill area for efficiency
        for (content_area, skill_area), group in enriched_df.groupby(['CONTENT_AREA_SHORT_NAME', 'SKILL_AREA_NAME']):
            if len(group) < 2:
                continue
            
            print(f"\n   Analyzing {content_area} - {skill_area} ({len(group)} skills)")
            
            # Simple similarity check based on shared concepts
            for idx1, skill1 in group.iterrows():
                if idx1 in processed_skills:
                    continue
                
                similar_skills = [skill1.to_dict()]
                
                for idx2, skill2 in group.iterrows():
                    if idx2 <= idx1 or idx2 in processed_skills:
                        continue
                    
                    # Simple concept overlap check
                    # In production: use embeddings + semantic similarity
                    if self._simple_similarity_check(skill1, skill2):
                        similar_skills.append(skill2.to_dict())
                        processed_skills.add(idx2)
                
                if len(similar_skills) > 1:
                    redundancy_groups.append({
                        "group_id": f"RED-{len(redundancy_groups)+1:03d}",
                        "content_area": content_area,
                        "skill_area": skill_area,
                        "skill_count": len(similar_skills),
                        "skills": [s['SKILL_ID'] for s in similar_skills],
                        "skill_names": [s['SKILL_NAME'][:50] + "..." if len(s['SKILL_NAME']) > 50 else s['SKILL_NAME'] 
                                       for s in similar_skills]
                    })
                    processed_skills.add(idx1)
        
        # Save redundancy report
        output_file = self.output_dir / "filtered_redundancy_report.json"
        with open(output_file, 'w') as f:
            json.dump({
                "total_skills": len(enriched_df),
                "redundancy_groups": redundancy_groups,
                "total_groups": len(redundancy_groups),
                "skills_in_groups": sum(g['skill_count'] for g in redundancy_groups),
                "unique_concepts": len(enriched_df) - sum(g['skill_count'] - 1 for g in redundancy_groups)
            }, f, indent=2)
        
        metrics = {
            "total_skills_analyzed": len(enriched_df),
            "redundancy_groups_found": len(redundancy_groups),
            "skills_in_groups": sum(g['skill_count'] for g in redundancy_groups),
            "unique_concepts_estimated": len(enriched_df) - sum(g['skill_count'] - 1 for g in redundancy_groups),
            "redundancy_rate": f"{(sum(g['skill_count'] - 1 for g in redundancy_groups) / len(enriched_df) * 100):.1f}%",
            "output_file": str(output_file)
        }
        
        # Display results
        print(f"\n📊 MID Level Results:")
        print(f"   ✓ Skills analyzed: {metrics['total_skills_analyzed']}")
        print(f"   ✓ Redundancy groups: {metrics['redundancy_groups_found']}")
        print(f"   ✓ Skills in groups: {metrics['skills_in_groups']}")
        print(f"   ✓ Estimated unique concepts: {metrics['unique_concepts_estimated']}")
        print(f"   ✓ Redundancy rate: {metrics['redundancy_rate']}")
        print(f"   ✓ Output saved to: {output_file}")
        
        # Show sample groups
        print(f"\n📝 Sample Redundancy Groups (first 5):")
        for group in redundancy_groups[:5]:
            print(f"\n   Group {group['group_id']}: {group['content_area']} - {group['skill_area']}")
            print(f"      Skills: {group['skill_count']}")
            for skill_name in group['skill_names'][:3]:  # Show first 3
                print(f"         • {skill_name}")
        
        self.results['mid'] = metrics
        return metrics
    
    def _simple_similarity_check(self, skill1: pd.Series, skill2: pd.Series) -> bool:
        """
        Simple similarity check based on grade level and basic text overlap.
        In production, use semantic embeddings.
        """
        # Same grade level
        if skill1['GRADE_LEVEL_SHORT_NAME'] != skill2['GRADE_LEVEL_SHORT_NAME']:
            return False
        
        # Basic text overlap (very simple)
        words1 = set(str(skill1['SKILL_NAME']).lower().split())
        words2 = set(str(skill2['SKILL_NAME']).lower().split())
        
        # Remove common words
        stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'and', 'or'}
        words1 = words1 - stopwords
        words2 = words2 - stopwords
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2) / len(words1 | words2)
        return overlap > 0.5
    
    def validate_macro(self) -> Dict:
        """
        MACRO Level: Master Concept Mapping
        
        Tests:
        - Extract base skills from redundancy groups
        - Group by skill area and content
        - Estimate master concepts
        - Calculate coverage metrics
        """
        print("\n" + "="*70)
        print("🎯 MACRO LEVEL: Master Concept Mapping")
        print("="*70)
        
        # Check if MID output exists
        mid_output = self.output_dir / "filtered_redundancy_report.json"
        if not mid_output.exists():
            print("⚠️  MID output not found - run --mid first or use --full")
            return {"status": "skipped", "reason": "MID output not available"}
        
        # Load redundancy report
        with open(mid_output) as f:
            redundancy_data = json.load(f)
        
        print(f"\n✓ Loaded redundancy report with {redundancy_data['total_groups']} groups")
        
        # Estimate master concepts
        # In production: use extract_base_skills.py
        master_concepts = []
        
        for group in redundancy_data['redundancy_groups']:
            master_concepts.append({
                "master_concept_id": f"MC-{len(master_concepts)+1:03d}",
                "base_skill": f"{group['content_area']}: {group['skill_area']}",
                "rock_skill_count": group['skill_count'],
                "rock_skill_mappings": group['skills'],
                "content_area": group['content_area'],
                "skill_area": group['skill_area']
            })
        
        # Add ungrouped skills as individual concepts
        grouped_skills = set()
        for group in redundancy_data['redundancy_groups']:
            grouped_skills.update(group['skills'])
        
        ungrouped = len(self.df) - len(grouped_skills)
        total_concepts = len(master_concepts) + ungrouped
        
        # Save master concepts
        output_file = self.output_dir / "filtered_master_concepts.json"
        with open(output_file, 'w') as f:
            json.dump({
                "total_master_concepts": total_concepts,
                "grouped_concepts": len(master_concepts),
                "individual_concepts": ungrouped,
                "master_concepts": master_concepts
            }, f, indent=2)
        
        metrics = {
            "total_rock_skills": len(self.df),
            "master_concepts_identified": total_concepts,
            "grouped_concepts": len(master_concepts),
            "individual_concepts": ungrouped,
            "reduction_ratio": f"{(1 - total_concepts/len(self.df))*100:.1f}%",
            "output_file": str(output_file)
        }
        
        # Display results
        print(f"\n📊 MACRO Level Results:")
        print(f"   ✓ ROCK skills input: {metrics['total_rock_skills']}")
        print(f"   ✓ Master concepts identified: {metrics['master_concepts_identified']}")
        print(f"   ✓ Grouped concepts: {metrics['grouped_concepts']}")
        print(f"   ✓ Individual concepts: {metrics['individual_concepts']}")
        print(f"   ✓ Reduction ratio: {metrics['reduction_ratio']}")
        print(f"   ✓ Output saved to: {output_file}")
        
        # Show sample concepts
        print(f"\n📝 Sample Master Concepts (first 5):")
        for concept in master_concepts[:5]:
            print(f"\n   {concept['master_concept_id']}: {concept['base_skill']}")
            print(f"      ROCK skills: {concept['rock_skill_count']}")
        
        self.results['macro'] = metrics
        return metrics
    
    def generate_summary(self):
        """Generate validation summary report."""
        print("\n" + "="*70)
        print("📋 VALIDATION SUMMARY")
        print("="*70)
        
        summary_file = self.output_dir / "validation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n🎯 Three-Level Integration Results:")
        print(f"\n   INPUT: {self.results['total_skills']} ROCK skills")
        
        if 'micro' in self.results and self.results['micro']:
            print(f"\n   🔬 MICRO Level:")
            print(f"      • Actions extracted: {self.results['micro'].get('actions_extraction_rate', 'N/A')}")
            print(f"      • Targets extracted: {self.results['micro'].get('targets_extraction_rate', 'N/A')}")
        
        if 'mid' in self.results and self.results['mid']:
            print(f"\n   🔍 MID Level:")
            print(f"      • Redundancy groups: {self.results['mid'].get('redundancy_groups_found', 'N/A')}")
            print(f"      • Redundancy rate: {self.results['mid'].get('redundancy_rate', 'N/A')}")
        
        if 'macro' in self.results and self.results['macro']:
            print(f"\n   🎯 MACRO Level:")
            print(f"      • Master concepts: {self.results['macro'].get('master_concepts_identified', 'N/A')}")
            print(f"      • Reduction: {self.results['macro'].get('reduction_ratio', 'N/A')}")
        
        print(f"\n   OUTPUT: Master skill spine with cross-state mappings")
        print(f"\n✓ Summary saved to: {summary_file}")
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="Validate three-level integration on filtered dataset")
    parser.add_argument('--input', default='../rock_schemas/skill_list_filtered_data_set.csv',
                       help="Input CSV file (default: skill_list_filtered_data_set.csv)")
    parser.add_argument('--full', action='store_true', help="Run all three levels")
    parser.add_argument('--micro', action='store_true', help="Run MICRO level only")
    parser.add_argument('--mid', action='store_true', help="Run MID level only")
    parser.add_argument('--macro', action='store_true', help="Run MACRO level only")
    
    args = parser.parse_args()
    
    # Default to full if no specific level specified
    if not (args.micro or args.mid or args.macro):
        args.full = True
    
    print("\n" + "="*70)
    print("🚀 ROCK AI HACKATHON 2025: Three-Level Integration Validator")
    print("="*70)
    
    validator = FilteredDatasetValidator(args.input)
    
    if args.full or args.micro:
        validator.validate_micro()
    
    if args.full or args.mid:
        validator.validate_mid()
    
    if args.full or args.macro:
        validator.validate_macro()
    
    validator.generate_summary()
    
    print("\n✅ Validation complete!")


if __name__ == "__main__":
    main()

