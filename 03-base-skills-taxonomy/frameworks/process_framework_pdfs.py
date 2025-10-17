#!/usr/bin/env python3
"""
PDF Taxonomy Processor

Extracts taxonomic structures from scientific frameworks and educational PDFs.
Generates master concepts for integration with existing taxonomies or creation of new ones.

Usage:
    # Extract taxonomy structure from PDF
    python process_framework_pdfs.py --input input/math/cambridge.pdf --mode extract --subject math
    
    # Validate ELA framework against existing taxonomy
    python process_framework_pdfs.py --input input/ela/duke_2021.pdf --mode validate --subject ela
    
    # Generate master concepts for batch mapping
    python process_framework_pdfs.py --input input/ela/scarborough.pdf --mode generate_concepts --subject ela --prepare-batch-mapping
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'taxonomy_builder'))

from framework_analyzer import FrameworkAnalyzer, FrameworkParser
from llm_interface import LLMInterface

try:
    from compatibility import TaxonomyAccess
    TAXONOMY_ACCESS_AVAILABLE = True
except ImportError:
    TAXONOMY_ACCESS_AVAILABLE = False
    print("Warning: TaxonomyAccess not available. --validate mode will be limited.")


class PDFTaxonomyProcessor:
    """Main processor for PDF taxonomy extraction and analysis."""
    
    def __init__(self, llm_provider: str = 'bedrock', llm_model: str = None):
        """
        Initialize processor.
        
        Args:
            llm_provider: LLM provider ('bedrock' or 'openai')
            llm_model: Optional specific model ID
        """
        self.llm = LLMInterface(provider=llm_provider, model=llm_model)
        self.analyzer = FrameworkAnalyzer(llm=self.llm)
    
    def extract_mode(self, 
                    input_file: Path,
                    subject_area: str,
                    output_dir: Path) -> dict:
        """
        Extract taxonomy structure from PDF.
        
        Args:
            input_file: Path to PDF file
            subject_area: Subject area code (ela, math, science)
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with extraction results
        """
        print(f"\n{'='*70}")
        print(f"MODE: EXTRACT TAXONOMY STRUCTURE")
        print(f"{'='*70}\n")
        
        # Extract adaptive taxonomy
        extraction_result = self.analyzer.extract_adaptive_taxonomy(
            file_path=input_file,
            subject_area=subject_area
        )
        
        # Save extraction results
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full extraction as JSON
        extraction_file = output_dir / f"{input_file.stem}_extraction.json"
        with open(extraction_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved extraction to: {extraction_file}")
        
        # Save proposed hierarchy separately
        if 'extraction' in extraction_result and 'proposed_hierarchy' in extraction_result['extraction']:
            hierarchy_file = output_dir / f"{input_file.stem}_structure.json"
            with open(hierarchy_file, 'w', encoding='utf-8') as f:
                json.dump(extraction_result['extraction']['proposed_hierarchy'], f, indent=2, ensure_ascii=False)
            print(f"✅ Saved hierarchy structure to: {hierarchy_file}")
        
        # Save summary
        summary_file = output_dir / f"{input_file.stem}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Taxonomy Extraction Summary\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(f"Source: {input_file.name}\n")
            f.write(f"Subject: {subject_area}\n")
            f.write(f"Word Count: {extraction_result['document']['word_count']:,}\n\n")
            
            if 'extraction' in extraction_result and 'metadata_summary' in extraction_result['extraction']:
                summary = extraction_result['extraction']['metadata_summary']
                f.write(f"Concepts Extracted: {summary.get('total_concepts_extracted', 0)}\n\n")
                
                if 'concepts_by_level' in summary:
                    f.write("Concepts by Level:\n")
                    for level, count in summary['concepts_by_level'].items():
                        f.write(f"  - {level}: {count}\n")
        
        print(f"✅ Saved summary to: {summary_file}")
        
        return {
            'extraction_file': str(extraction_file),
            'hierarchy_file': str(hierarchy_file) if 'hierarchy_file' in locals() else None,
            'summary_file': str(summary_file)
        }
    
    def validate_mode(self,
                     input_file: Path,
                     subject_area: str,
                     output_dir: Path,
                     existing_taxonomy_path: Optional[Path] = None) -> dict:
        """
        Validate framework against existing taxonomy.
        
        Args:
            input_file: Path to PDF file
            subject_area: Subject area code
            output_dir: Directory to save outputs
            existing_taxonomy_path: Optional path to existing taxonomy CSV
            
        Returns:
            Dictionary with validation results
        """
        print(f"\n{'='*70}")
        print(f"MODE: VALIDATE AGAINST EXISTING TAXONOMY")
        print(f"{'='*70}\n")
        
        # Extract taxonomy
        extraction_result = self.analyzer.extract_adaptive_taxonomy(
            file_path=input_file,
            subject_area=subject_area
        )
        
        # Generate master concepts
        master_concepts = self.analyzer.generate_master_concepts(
            extracted_taxonomy=extraction_result,
            subject_area=subject_area
        )
        
        # Load existing taxonomy
        existing_taxonomy_df = None
        if existing_taxonomy_path:
            print(f"\nLoading existing taxonomy from: {existing_taxonomy_path}")
            existing_taxonomy_df = pd.read_csv(existing_taxonomy_path)
        elif TAXONOMY_ACCESS_AVAILABLE and subject_area == 'ela':
            print("\nLoading ELA taxonomy from default location...")
            try:
                with TaxonomyAccess() as tax:
                    existing_taxonomy_df = tax.get_taxonomy_df()
            except Exception as e:
                print(f"Warning: Could not load default taxonomy: {e}")
        
        # Analyze alignment
        alignment_result = self.analyzer.analyze_alignment(
            extracted_concepts=master_concepts,
            existing_taxonomy_df=existing_taxonomy_df
        )
        
        # Save results
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save alignment analysis
        gap_analysis_file = output_dir / f"{input_file.stem}_gap_analysis.json"
        with open(gap_analysis_file, 'w', encoding='utf-8') as f:
            json.dump(alignment_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved gap analysis to: {gap_analysis_file}")
        
        # Save gap report as readable markdown
        gap_report_file = output_dir / f"{input_file.stem}_gap_report.md"
        with open(gap_report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Gap Analysis Report\n\n")
            f.write(f"**Framework**: {input_file.name}\n")
            f.write(f"**Subject**: {subject_area}\n")
            f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
            
            f.write(f"## Alignment Summary\n\n")
            f.write(f"- **Alignment Score**: {alignment_result['alignment_score']:.1%}\n")
            f.write(f"- **Extracted Concepts**: {alignment_result['extracted_concept_count']}\n")
            f.write(f"- **Existing Concepts**: {alignment_result['existing_concept_count']}\n")
            f.write(f"- **Overlapping**: {len(alignment_result.get('overlapping_concepts', []))}\n\n")
            
            f.write(f"## New Concepts from Framework\n\n")
            f.write(f"These {len(alignment_result['missing_from_taxonomy'])} concepts appear in the framework but not in your taxonomy:\n\n")
            for concept in alignment_result['missing_from_taxonomy'][:30]:  # Limit to 30
                f.write(f"- {concept}\n")
            if len(alignment_result['missing_from_taxonomy']) > 30:
                f.write(f"\n... and {len(alignment_result['missing_from_taxonomy']) - 30} more\n")
            
            f.write(f"\n## Concepts Not in Framework\n\n")
            f.write(f"These {len(alignment_result['missing_from_framework'])} concepts are in your taxonomy but not in the framework:\n\n")
            for concept in alignment_result['missing_from_framework'][:20]:  # Limit to 20
                f.write(f"- {concept}\n")
            if len(alignment_result['missing_from_framework']) > 20:
                f.write(f"\n... and {len(alignment_result['missing_from_framework']) - 20} more\n")
        
        print(f"✅ Saved gap report to: {gap_report_file}")
        
        return {
            'gap_analysis_file': str(gap_analysis_file),
            'gap_report_file': str(gap_report_file),
            'alignment_score': alignment_result['alignment_score']
        }
    
    def generate_concepts_mode(self,
                              input_file: Path,
                              subject_area: str,
                              output_dir: Path,
                              prepare_batch_mapping: bool = False) -> dict:
        """
        Generate master concepts from PDF.
        
        Args:
            input_file: Path to PDF file
            subject_area: Subject area code
            output_dir: Directory to save outputs
            prepare_batch_mapping: Whether to prepare batch mapping input files
            
        Returns:
            Dictionary with results
        """
        print(f"\n{'='*70}")
        print(f"MODE: GENERATE MASTER CONCEPTS")
        print(f"{'='*70}\n")
        
        # Extract taxonomy
        extraction_result = self.analyzer.extract_adaptive_taxonomy(
            file_path=input_file,
            subject_area=subject_area
        )
        
        # Generate master concepts
        master_concepts = self.analyzer.generate_master_concepts(
            extracted_taxonomy=extraction_result,
            subject_area=subject_area
        )
        
        # Save results
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        concepts_csv_file = output_dir / f"{subject_area}_master_concepts.csv"
        if master_concepts:
            df = pd.DataFrame(master_concepts)
            df.to_csv(concepts_csv_file, index=False)
            print(f"\n✅ Saved master concepts CSV: {concepts_csv_file}")
            print(f"   ({len(master_concepts)} concepts)")
        
        results = {
            'concepts_csv_file': str(concepts_csv_file),
            'concept_count': len(master_concepts)
        }
        
        # Optionally prepare batch mapping inputs
        if prepare_batch_mapping:
            batch_output_dir = output_dir / 'batch_input'
            export_result = self.analyzer.export_for_batch_mapping(
                master_concepts=master_concepts,
                output_dir=batch_output_dir
            )
            results['batch_mapping_files'] = export_result
        
        return results
    
    def full_pipeline_mode(self,
                          input_file: Path,
                          subject_area: str,
                          output_dir: Path,
                          existing_taxonomy_path: Optional[Path] = None) -> dict:
        """
        Run full pipeline: extract → generate concepts → validate → prepare batch mapping.
        
        Args:
            input_file: Path to PDF file
            subject_area: Subject area code
            output_dir: Directory to save outputs
            existing_taxonomy_path: Optional path to existing taxonomy CSV
            
        Returns:
            Dictionary with all results
        """
        print(f"\n{'='*70}")
        print(f"MODE: FULL PIPELINE")
        print(f"{'='*70}\n")
        
        results = {}
        
        # Step 1: Extract
        print("\n[1/4] Extracting taxonomy...")
        extract_result = self.extract_mode(input_file, subject_area, output_dir / 'extraction')
        results['extraction'] = extract_result
        
        # Step 2: Generate concepts
        print("\n[2/4] Generating master concepts...")
        concepts_result = self.generate_concepts_mode(
            input_file, subject_area, output_dir / 'concepts',
            prepare_batch_mapping=True
        )
        results['concepts'] = concepts_result
        
        # Step 3: Validate (if existing taxonomy provided)
        if existing_taxonomy_path or (TAXONOMY_ACCESS_AVAILABLE and subject_area == 'ela'):
            print("\n[3/4] Validating against existing taxonomy...")
            validate_result = self.validate_mode(
                input_file, subject_area, output_dir / 'validation',
                existing_taxonomy_path
            )
            results['validation'] = validate_result
        else:
            print("\n[3/4] Skipping validation (no existing taxonomy)")
            results['validation'] = {'note': 'No existing taxonomy provided'}
        
        # Step 4: Summary
        print("\n[4/4] Generating summary...")
        summary_file = output_dir / 'SUMMARY.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# PDF Taxonomy Processing Summary\n\n")
            f.write(f"**Source**: {input_file.name}\n")
            f.write(f"**Subject**: {subject_area}\n")
            f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write(f"## Results\n\n")
            f.write(f"### 1. Extraction\n")
            f.write(f"- Output: `{Path(extract_result['extraction_file']).relative_to(output_dir)}`\n\n")
            
            f.write(f"### 2. Master Concepts\n")
            f.write(f"- Generated: {concepts_result['concept_count']} concepts\n")
            f.write(f"- Output: `{Path(concepts_result['concepts_csv_file']).relative_to(output_dir)}`\n")
            if 'batch_mapping_files' in concepts_result:
                f.write(f"- Batch mapping files: `{Path(concepts_result['batch_mapping_files']['output_dir']).relative_to(output_dir)}`\n")
            f.write(f"\n")
            
            if 'alignment_score' in results.get('validation', {}):
                f.write(f"### 3. Validation\n")
                f.write(f"- Alignment score: {results['validation']['alignment_score']:.1%}\n")
                f.write(f"- Gap report: `{Path(results['validation']['gap_report_file']).relative_to(output_dir)}`\n\n")
            
            f.write(f"## Next Steps\n\n")
            f.write(f"1. **Review** extracted concepts in `concepts/` directory\n")
            f.write(f"2. **Run batch mapping** using files in `concepts/batch_input/`\n")
            if 'validation' in results:
                f.write(f"3. **Review gaps** in validation reports\n")
            f.write(f"4. **Integrate** approved concepts into main taxonomy\n")
        
        print(f"\n✅ Full pipeline complete!")
        print(f"✅ Summary saved to: {summary_file}")
        
        results['summary_file'] = str(summary_file)
        
        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Process framework PDFs to extract taxonomies and generate master concepts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract structure from math PDF
  python process_framework_pdfs.py --input input/math/cambridge.pdf --mode extract --subject math
  
  # Validate ELA framework
  python process_framework_pdfs.py --input input/ela/duke.pdf --mode validate --subject ela
  
  # Generate concepts and prepare for batch mapping
  python process_framework_pdfs.py --input input/ela/scarborough.pdf --mode generate_concepts --subject ela --prepare-batch-mapping
  
  # Run full pipeline
  python process_framework_pdfs.py --input input/math/cambridge.pdf --mode full --subject math --output output/cambridge_full
        """
    )
    
    parser.add_argument('--input', '-i', type=Path, required=True,
                       help='Path to input PDF file')
    parser.add_argument('--mode', '-m', 
                       choices=['extract', 'validate', 'generate_concepts', 'full'],
                       required=True,
                       help='Processing mode')
    parser.add_argument('--subject', '-s',
                       choices=['ela', 'math', 'science', 'general'],
                       required=True,
                       help='Subject area')
    parser.add_argument('--output', '-o', type=Path,
                       help='Output directory (default: output/{filename})')
    parser.add_argument('--existing-taxonomy', type=Path,
                       help='Path to existing taxonomy CSV for validation')
    parser.add_argument('--prepare-batch-mapping', action='store_true',
                       help='Prepare input files for batch mapping pipeline')
    parser.add_argument('--llm-provider', default='bedrock',
                       choices=['bedrock', 'openai'],
                       help='LLM provider (default: bedrock)')
    parser.add_argument('--llm-model', 
                       help='Specific LLM model ID (optional)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Set default output directory
    if args.output is None:
        args.output = Path('output') / args.input.stem
    
    # Create processor
    try:
        processor = PDFTaxonomyProcessor(
            llm_provider=args.llm_provider,
            llm_model=args.llm_model
        )
    except Exception as e:
        print(f"Error initializing processor: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured (for bedrock)")
        print("  2. Required Python packages installed")
        sys.exit(1)
    
    # Run appropriate mode
    try:
        if args.mode == 'extract':
            results = processor.extract_mode(
                args.input, args.subject, args.output
            )
        elif args.mode == 'validate':
            results = processor.validate_mode(
                args.input, args.subject, args.output,
                args.existing_taxonomy
            )
        elif args.mode == 'generate_concepts':
            results = processor.generate_concepts_mode(
                args.input, args.subject, args.output,
                args.prepare_batch_mapping
            )
        elif args.mode == 'full':
            results = processor.full_pipeline_mode(
                args.input, args.subject, args.output,
                args.existing_taxonomy
            )
        
        # Print cost summary
        print(f"\n{'='*70}")
        print(f"COST SUMMARY")
        print(f"{'='*70}")
        usage = processor.llm.get_usage_stats()
        print(f"Total tokens: {usage['total_tokens']:,}")
        print(f"Estimated cost: ${usage['estimated_cost_usd']:.4f}")
        
        print(f"\n✅ Processing complete!")
        print(f"📁 Output directory: {args.output}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

