#!/usr/bin/env python3
"""
Taxonomy Builder CLI

Command-line interface for taxonomy validation, framework comparison,
and LLM-assisted improvements.

Usage:
    python cli.py validate [--output report.md]
    python cli.py compare <framework_file> [--output report.md]
    python cli.py suggest [--aspect naming|structure]
    python cli.py report [--output report.md]
"""

import sys
import argparse
from pathlib import Path
import json

# Add parent directory to path if running as script
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

from taxonomy_builder.compatibility import TaxonomyAccess
from taxonomy_builder.validator import TaxonomyValidator
from taxonomy_builder.llm_interface import LLMInterface
from taxonomy_builder.framework_analyzer import FrameworkAnalyzer


def cmd_validate(args):
    """Run validation on taxonomy."""
    print("="*60)
    print("TAXONOMY VALIDATION")
    print("="*60)
    print()
    
    with TaxonomyAccess() as tax:
        validator = TaxonomyValidator(tax)
        report = validator.validate()
        
        # Print summary to console
        print(f"\nValidation Results:")
        print(f"  Total nodes: {report.total_nodes}")
        print(f"  Total issues: {report.total_issues}")
        print(f"\nBy Severity:")
        for severity, count in sorted(report.issues_by_severity.items()):
            print(f"  {severity}: {count}")
        print(f"\nBy Category:")
        for category, count in sorted(report.issues_by_category.items()):
            print(f"  {category}: {count}")
        
        # Save reports
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path('validation_report.md')
        
        json_path = output_path.with_suffix('.json')
        
        # Save JSON
        with open(json_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nJSON report saved to: {json_path}")
        
        # Save Markdown
        with open(output_path, 'w') as f:
            f.write(report.to_markdown())
        print(f"Markdown report saved to: {output_path}")
        
        print("\nValidation complete!")
        
        return 0 if report.total_issues == 0 else 1


def cmd_compare(args):
    """Compare framework with taxonomy."""
    print("="*60)
    print("FRAMEWORK COMPARISON")
    print("="*60)
    print()
    
    framework_path = Path(args.framework_file)
    
    if not framework_path.exists():
        print(f"Error: Framework file not found: {framework_path}")
        return 1
    
    with TaxonomyAccess() as tax:
        # Initialize LLM
        provider = args.provider or 'bedrock'
        llm = LLMInterface(provider=provider)
        
        # Analyze framework
        analyzer = FrameworkAnalyzer(tax, llm)
        result = analyzer.analyze_framework(
            framework_path,
            compare_with_taxonomy=True
        )
        
        # Generate report
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(f'framework_comparison_{framework_path.stem}.md')
        
        report = analyzer.generate_report(result, output_path)
        
        # Print summary
        print(f"\n{'='*60}")
        print("Summary:")
        if result.get('comparison') and not result['comparison'].get('parse_error'):
            comparison = result['comparison']
            print(f"  Alignment score: {comparison.get('alignment_score', 'N/A')}")
            print(f"  Missing from our taxonomy: {len(comparison.get('missing_from_ours', []))}")
            print(f"  Missing from framework: {len(comparison.get('missing_from_framework', []))}")
            print(f"  Recommendations: {len(comparison.get('recommendations', []))}")
        
        # LLM usage
        usage = result.get('llm_usage', {})
        print(f"\nLLM Usage:")
        print(f"  Total tokens: {usage.get('total_tokens', 0)}")
        print(f"  Estimated cost: ${usage.get('estimated_cost_usd', 0):.4f}")
        
        print(f"\nComparison complete!")
        
        return 0


def cmd_suggest(args):
    """Get LLM suggestions for taxonomy improvements."""
    print("="*60)
    print("TAXONOMY IMPROVEMENT SUGGESTIONS")
    print("="*60)
    print()
    
    aspect = args.aspect or 'naming'
    
    with TaxonomyAccess() as tax:
        # Initialize LLM
        provider = args.provider or 'bedrock'
        llm = LLMInterface(provider=provider)
        
        if aspect == 'naming':
            print("Analyzing naming consistency...")
            
            # Get names by level
            conn = tax.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT level, GROUP_CONCAT(name, '|||') as names
                FROM taxonomy_nodes
                GROUP BY level
            ''')
            
            names_by_level = {}
            for row in cursor.fetchall():
                level = row['level']
                names = row['names'].split('|||')
                names_by_level[level] = sorted(set(names))
            
            suggestions = llm.suggest_naming_improvements(names_by_level)
            
        elif aspect == 'structure':
            print("Analyzing structural design...")
            
            # Get taxonomy summary
            validator = TaxonomyValidator(tax)
            stats = validator._generate_statistics()
            
            # Get sample of taxonomy structure
            summary_parts = []
            strands = tax.get_nodes_by_level('Strand')
            
            for strand in strands[:3]:  # Sample first 3 strands
                summary_parts.append(f"Strand: {strand.name}")
                pillars = tax.get_children(strand.uuid)
                for pillar in pillars[:2]:
                    summary_parts.append(f"  Pillar: {pillar.name}")
                    domains = tax.get_children(pillar.uuid)
                    for domain in domains[:2]:
                        summary_parts.append(f"    Domain: {domain.name}")
            
            summary_parts.append(f"\nStatistics: {json.dumps(stats, indent=2)}")
            taxonomy_summary = '\n'.join(summary_parts)
            
            suggestions = llm.validate_structure(taxonomy_summary)
        else:
            print(f"Error: Unknown aspect '{aspect}'. Use 'naming' or 'structure'.")
            return 1
        
        # Save suggestions
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(f'suggestions_{aspect}.json')
        
        with open(output_path, 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        print(f"\nSuggestions saved to: {output_path}")
        
        # Print summary if not parse error
        if not suggestions.get('parse_error'):
            if aspect == 'naming' and 'recommendations' in suggestions:
                print(f"\nFound {len(suggestions['recommendations'])} recommendations")
            elif aspect == 'structure' and 'suggestions' in suggestions:
                print(f"\nFound {len(suggestions['suggestions'])} suggestions")
        
        # LLM usage
        usage = llm.get_usage_stats()
        print(f"\nLLM Usage:")
        print(f"  Total tokens: {usage['total_tokens']}")
        print(f"  Estimated cost: ${usage['estimated_cost_usd']:.4f}")
        
        print("\nSuggestions complete!")
        
        return 0


def cmd_report(args):
    """Generate comprehensive report."""
    print("="*60)
    print("COMPREHENSIVE TAXONOMY REPORT")
    print("="*60)
    print()
    
    print("Running validation...")
    with TaxonomyAccess() as tax:
        validator = TaxonomyValidator(tax)
        validation_report = validator.validate()
        
        # Prepare output
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path('comprehensive_report.md')
        
        # Build comprehensive report
        lines = []
        lines.append("# Comprehensive Taxonomy Report")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Nodes:** {validation_report.total_nodes}")
        lines.append(f"- **Total Issues Found:** {validation_report.total_issues}")
        lines.append("")
        
        # Include validation report
        lines.append("## Validation Report")
        lines.append("")
        lines.append(validation_report.to_markdown())
        
        # Save report
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"\nComprehensive report saved to: {output_path}")
        print("\nReport generation complete!")
        
        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Taxonomy Builder - Validation and Framework Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate taxonomy
  python cli.py validate --output validation_report.md

  # Compare with framework
  python cli.py compare framework.pdf --output comparison.md

  # Get naming suggestions
  python cli.py suggest --aspect naming --output suggestions.json

  # Generate comprehensive report
  python cli.py report --output full_report.md
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate taxonomy structure')
    validate_parser.add_argument('--output', '-o', help='Output file path')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare with external framework')
    compare_parser.add_argument('framework_file', help='Path to framework file (PDF, DOCX, TXT)')
    compare_parser.add_argument('--output', '-o', help='Output file path')
    compare_parser.add_argument('--provider', choices=['bedrock', 'openai'], help='LLM provider')
    
    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Get LLM suggestions')
    suggest_parser.add_argument('--aspect', choices=['naming', 'structure'], help='Aspect to analyze')
    suggest_parser.add_argument('--output', '-o', help='Output file path')
    suggest_parser.add_argument('--provider', choices=['bedrock', 'openai'], help='LLM provider')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive report')
    report_parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'compare':
        return cmd_compare(args)
    elif args.command == 'suggest':
        return cmd_suggest(args)
    elif args.command == 'report':
        return cmd_report(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

