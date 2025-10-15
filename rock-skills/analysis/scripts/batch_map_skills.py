#!/usr/bin/env python3
"""
Batch Skill Mapping Pipeline

Process multiple ROCK skills through LLM-assisted mapping with:
- Resume from checkpoint (for 8,355 skills)
- Progress tracking and logging
- Cost monitoring
- Error handling and recovery
- Human review queue for low-confidence mappings

Usage:
    python batch_map_skills.py --start-index 50 --batch-size 100
"""

import pandas as pd
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.llm_mapping_assistant import LLMMapperAssistant


class BatchMapper:
    """
    Batch processor for mapping ROCK skills to taxonomy.
    """
    
    def __init__(
        self,
        skills_df: pd.DataFrame,
        taxonomy_df: pd.DataFrame,
        output_dir: Path,
        resume_from: Optional[Path] = None
    ):
        """
        Initialize batch mapper.
        
        Args:
            skills_df: ROCK skills DataFrame
            taxonomy_df: Science of Reading taxonomy DataFrame
            output_dir: Directory for output files
            resume_from: Optional checkpoint file to resume from
        """
        self.skills_df = skills_df
        self.taxonomy_df = taxonomy_df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize LLM assistant
        print("Initializing LLM mapping assistant...")
        self.assistant = LLMMapperAssistant(taxonomy_df)
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        self.review_queue = []
        self.processed_count = 0
        self.error_count = 0
        
        # Resume from checkpoint if provided
        if resume_from and resume_from.exists():
            self._load_checkpoint(resume_from)
    
    def _load_checkpoint(self, checkpoint_path: Path):
        """
        Load progress from checkpoint file.
        """
        print(f"Loading checkpoint from: {checkpoint_path}")
        try:
            checkpoint_df = pd.read_csv(checkpoint_path)
            self.results = checkpoint_df.to_dict('records')
            self.processed_count = len(self.results)
            print(f"✓ Resumed from checkpoint: {self.processed_count} skills already mapped")
        except Exception as e:
            print(f"Warning: Could not load checkpoint: {e}")
    
    def _save_checkpoint(self):
        """
        Save current progress to checkpoint file.
        """
        if not self.results:
            return
        
        checkpoint_path = self.output_dir / f"checkpoint_{self.session_id}.csv"
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(checkpoint_path, index=False)
        print(f"✓ Checkpoint saved: {checkpoint_path}")
    
    def _save_review_queue(self):
        """
        Save low-confidence mappings to review queue.
        """
        if not self.review_queue:
            return
        
        review_path = self.output_dir / f"review_queue_{self.session_id}.csv"
        review_df = pd.DataFrame(self.review_queue)
        review_df.to_csv(review_path, index=False)
        print(f"✓ Review queue saved: {len(self.review_queue)} items -> {review_path}")
    
    def map_skill(self, skill_row: pd.Series) -> dict:
        """
        Map a single skill and return result.
        
        Returns:
            Dict with mapping result
        """
        try:
            # Get LLM suggestions
            suggestions = self.assistant.suggest_mappings(
                skill_id=skill_row['SKILL_ID'],
                skill_name=skill_row['SKILL_NAME'],
                skill_area=skill_row.get('SKILL_AREA_NAME'),
                content_area=skill_row.get('CONTENT_AREA_NAME'),
                grade_level=skill_row.get('GRADE_LEVEL_NAME'),
                top_k=3  # Get top 3 suggestions
            )
            
            if not suggestions:
                return {
                    'skill_id': skill_row['SKILL_ID'],
                    'skill_name': skill_row['SKILL_NAME'],
                    'status': 'no_suggestions',
                    'error': 'No suggestions returned'
                }
            
            # Take best suggestion
            best_suggestion = suggestions[0]
            
            # Check if needs human review
            needs_review = (
                best_suggestion['confidence'] == 'Low' or
                best_suggestion.get('semantic_similarity', 0) < 0.5
            )
            
            result = {
                'skill_id': skill_row['SKILL_ID'],
                'skill_name': skill_row['SKILL_NAME'],
                'skill_area': skill_row.get('SKILL_AREA_NAME', ''),
                'content_area': skill_row.get('CONTENT_AREA_NAME', ''),
                'grade_level': skill_row.get('GRADE_LEVEL_NAME', ''),
                'taxonomy_path': best_suggestion['taxonomy_path'],
                'confidence': best_suggestion['confidence'],
                'rationale': best_suggestion['rationale'],
                'semantic_similarity': best_suggestion.get('semantic_similarity', 0),
                'needs_review': needs_review,
                'alternative_1': suggestions[1]['taxonomy_path'] if len(suggestions) > 1 else '',
                'alternative_2': suggestions[2]['taxonomy_path'] if len(suggestions) > 2 else '',
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to review queue if needed
            if needs_review:
                self.review_queue.append(result)
            
            return result
            
        except Exception as e:
            self.error_count += 1
            return {
                'skill_id': skill_row['SKILL_ID'],
                'skill_name': skill_row['SKILL_NAME'],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_batch(
        self,
        start_index: int = 0,
        batch_size: Optional[int] = None,
        checkpoint_interval: int = 10,
        filter_content_area: Optional[str] = None
    ):
        """
        Process a batch of skills.
        
        Args:
            start_index: Index to start from
            batch_size: Number of skills to process (None = all remaining)
            checkpoint_interval: Save checkpoint every N skills
            filter_content_area: Optional content area filter (e.g., 'ELA')
        """
        # Filter skills if requested
        skills_to_process = self.skills_df.copy()
        if filter_content_area:
            skills_to_process = skills_to_process[
                skills_to_process['CONTENT_AREA_NAME'] == filter_content_area
            ]
            print(f"Filtered to {len(skills_to_process)} {filter_content_area} skills")
        
        # Determine batch range
        end_index = start_index + batch_size if batch_size else len(skills_to_process)
        end_index = min(end_index, len(skills_to_process))
        
        total_to_process = end_index - start_index
        
        print(f"\n{'=' * 60}")
        print(f"BATCH PROCESSING: Skills {start_index} to {end_index}")
        print(f"Total: {total_to_process} skills")
        print(f"{'=' * 60}\n")
        
        start_time = time.time()
        
        # Process each skill
        for i in range(start_index, end_index):
            skill_row = skills_to_process.iloc[i]
            
            print(f"\n[{i+1}/{end_index}] Processing: {skill_row['SKILL_NAME'][:80]}...")
            
            result = self.map_skill(skill_row)
            self.results.append(result)
            self.processed_count += 1
            
            # Print result summary
            if result['status'] == 'success':
                print(f"  ✓ Mapped with confidence: {result['confidence']}")
                if result['needs_review']:
                    print(f"  ⚠ Added to review queue")
            else:
                print(f"  ✗ Error: {result.get('error', 'Unknown')}")
            
            # Save checkpoint periodically
            if self.processed_count % checkpoint_interval == 0:
                print(f"\n--- Checkpoint at {self.processed_count} skills ---")
                self._save_checkpoint()
                self._save_review_queue()
                self.assistant.print_usage_stats()
        
        # Final save
        elapsed_time = time.time() - start_time
        
        print(f"\n{'=' * 60}")
        print(f"BATCH COMPLETE")
        print(f"{'=' * 60}")
        print(f"Processed: {total_to_process} skills")
        print(f"Successful: {self.processed_count - self.error_count}")
        print(f"Errors: {self.error_count}")
        print(f"Review Queue: {len(self.review_queue)} skills")
        print(f"Time Elapsed: {elapsed_time:.1f}s")
        print(f"Avg Time per Skill: {elapsed_time / total_to_process:.1f}s")
        
        # Save final results
        self._save_final_results()
        self._save_checkpoint()
        self._save_review_queue()
        self.assistant.print_usage_stats()
    
    def _save_final_results(self):
        """
        Save final mapping results.
        """
        output_path = self.output_dir / f"llm_assisted_mappings_{self.session_id}.csv"
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(output_path, index=False)
        print(f"\n✓ Final results saved: {output_path}")
        
        # Generate summary report
        summary_path = self.output_dir / f"mapping_summary_{self.session_id}.txt"
        with open(summary_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("LLM-ASSISTED MAPPING SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Total Skills Processed: {self.processed_count}\n")
            f.write(f"Successful Mappings: {self.processed_count - self.error_count}\n")
            f.write(f"Errors: {self.error_count}\n\n")
            
            # Confidence breakdown
            if results_df['status'].eq('success').any():
                success_df = results_df[results_df['status'] == 'success']
                f.write("Confidence Distribution:\n")
                confidence_counts = success_df['confidence'].value_counts()
                for conf, count in confidence_counts.items():
                    pct = (count / len(success_df)) * 100
                    f.write(f"  {conf}: {count} ({pct:.1f}%)\n")
                f.write(f"\nNeeds Review: {success_df['needs_review'].sum()} ({(success_df['needs_review'].sum() / len(success_df)) * 100:.1f}%)\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("LLM USAGE\n")
            f.write("=" * 60 + "\n")
            stats = self.assistant.get_usage_stats()
            f.write(f"API Calls: {stats['api_calls']:,}\n")
            f.write(f"Total Tokens: {stats['total_tokens']:,}\n")
            f.write(f"Estimated Cost: ${stats['estimated_cost_usd']:.2f}\n")
        
        print(f"✓ Summary report saved: {summary_path}")


def main():
    """
    Main entry point for batch mapping.
    """
    parser = argparse.ArgumentParser(
        description='Batch map ROCK skills to taxonomy using LLM assistance'
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=0,
        help='Index to start from (default: 0)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Number of skills to process (default: all remaining)'
    )
    parser.add_argument(
        '--checkpoint-interval',
        type=int,
        default=10,
        help='Save checkpoint every N skills (default: 10)'
    )
    parser.add_argument(
        '--content-area',
        type=str,
        default=None,
        help='Filter to specific content area (e.g., ELA)'
    )
    parser.add_argument(
        '--resume-from',
        type=str,
        default=None,
        help='Resume from checkpoint file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ROCK SKILLS BATCH MAPPING PIPELINE")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    skills_path = Path('../../rock_schemas/SKILLS.csv')
    taxonomy_path = Path('../../POC_science_of_reading_literacy_skills_taxonomy.csv')
    
    # OPTIMIZATION: Load only essential columns to reduce memory and improve performance
    essential_columns = [
        'SKILL_ID',
        'SKILL_NAME',
        'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME',
        'GRADE_LEVEL_NAME',  # Full name is more readable for LLM (e.g., "Grade 1" vs "1")
        'GRADE_LEVEL_SHORT_NAME'  # Keep for potential filtering/display
    ]
    
    skills_df = pd.read_csv(skills_path, usecols=essential_columns)
    taxonomy_df = pd.read_csv(taxonomy_path)
    
    print(f"✓ Loaded {len(skills_df):,} ROCK skills (optimized: {len(essential_columns)} columns)")
    print(f"✓ Loaded {len(taxonomy_df):,} taxonomy entries")
    
    # Initialize batch mapper
    resume_path = Path(args.resume_from) if args.resume_from else None
    
    mapper = BatchMapper(
        skills_df=skills_df,
        taxonomy_df=taxonomy_df,
        output_dir=Path(args.output_dir),
        resume_from=resume_path
    )
    
    # Process batch
    mapper.process_batch(
        start_index=args.start_index,
        batch_size=args.batch_size,
        checkpoint_interval=args.checkpoint_interval,
        filter_content_area=args.content_area
    )
    
    print("\n" + "=" * 60)
    print("BATCH MAPPING COMPLETE!")
    print("=" * 60)


if __name__ == '__main__':
    main()

