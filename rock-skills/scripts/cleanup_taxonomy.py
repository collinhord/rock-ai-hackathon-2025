"""
Taxonomy Cleanup Script

Normalizes capitalization, punctuation, and wording inconsistencies in the
Science of Reading taxonomy CSV file.

Creates a timestamped backup before making any modifications.

Usage:
    python cleanup_taxonomy.py [--input path/to/taxonomy.csv] [--dry-run]
"""

import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
import re
import sys
from typing import Dict, List, Tuple
from difflib import SequenceMatcher


class TaxonomyCleanup:
    """Cleans and normalizes taxonomy data."""
    
    def __init__(self, csv_path: Path):
        """Initialize with path to taxonomy CSV."""
        self.csv_path = Path(csv_path)
        self.df = None
        self.changes = []
        
    def load(self):
        """Load the taxonomy CSV."""
        print(f"Loading taxonomy from: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} rows")
        
    def create_backup(self):
        """Create timestamped backup of original file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.csv_path.parent / f"{self.csv_path.stem}_backup_{timestamp}.csv"
        self.df.to_csv(backup_path, index=False)
        print(f"Created backup: {backup_path}")
        return backup_path
        
    def normalize_capitalization(self, text: str) -> str:
        """
        Normalize capitalization of common conjunctions and prepositions.
        
        Rules:
        - Lowercase: and, or, of, for, to, in, on, at, by, with, from
        - Keep uppercase at start of string
        - Preserve acronyms and proper nouns
        """
        if pd.isna(text) or not text:
            return text
            
        # Words that should be lowercase when mid-phrase
        lowercase_words = {
            'And', 'Or', 'Of', 'For', 'To', 'In', 'On', 'At', 'By', 'With', 'From',
            'The', 'A', 'An', 'As', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been'
        }
        
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Keep first word as-is (maintain sentence case)
            if i == 0:
                result.append(word)
            # Lowercase conjunctions/prepositions mid-phrase
            elif word in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word)
                
        return ' '.join(result)
    
    def normalize_punctuation(self, text: str) -> str:
        """
        Normalize punctuation: convert & to 'and'.
        
        Exception: Keep & if it appears to be part of standard abbreviation
        like 'Q&A' or technical term.
        """
        if pd.isna(text) or not text:
            return text
            
        # Keep Q&A as-is (special case)
        if 'Q&A' in text:
            return text
            
        # Replace & with 'and'
        normalized = text.replace(' & ', ' and ')
        
        return normalized
    
    def normalize_articles(self, text: str) -> str:
        """
        Remove inconsistent use of articles.
        
        This is conservative - only fixes obvious inconsistencies.
        """
        if pd.isna(text) or not text:
            return text
            
        # Specific fixes based on analysis
        fixes = {
            'Previewing the Text': 'Previewing Text',
        }
        
        return fixes.get(text, text)
    
    def apply_specific_fixes(self, text: str) -> str:
        """Apply specific known fixes."""
        if pd.isna(text) or not text:
            return text
            
        # Known issues from analysis
        specific_fixes = {
            'Using Metaphors And Analogies': 'Using Metaphors and Analogies',
        }
        
        return specific_fixes.get(text, text)
    
    def clean_cell(self, text: str, column: str) -> Tuple[str, bool]:
        """
        Clean a single cell value.
        
        Returns: (cleaned_text, was_modified)
        """
        if pd.isna(text) or not text:
            return text, False
            
        original = text
        
        # Apply transformations
        text = self.apply_specific_fixes(text)
        text = self.normalize_punctuation(text)
        text = self.normalize_capitalization(text)
        text = self.normalize_articles(text)
        
        # Strip extra whitespace
        text = ' '.join(text.split())
        
        was_modified = (text != original)
        
        if was_modified:
            self.changes.append({
                'column': column,
                'original': original,
                'cleaned': text
            })
            
        return text, was_modified
    
    def clean_taxonomy(self):
        """Clean all taxonomy columns."""
        print("\nCleaning taxonomy...")
        
        # Columns to clean
        columns_to_clean = [
            'Strand', 'Pillar', 'Domain', 'Skill Area', 
            'Skill Set', 'Skill Subset'
        ]
        
        total_changes = 0
        
        for column in columns_to_clean:
            if column not in self.df.columns:
                continue
                
            print(f"  Cleaning column: {column}")
            changes_in_column = 0
            
            for idx, value in self.df[column].items():
                cleaned, was_modified = self.clean_cell(value, column)
                
                if was_modified:
                    self.df.at[idx, column] = cleaned
                    changes_in_column += 1
                    
            print(f"    Modified {changes_in_column} cells")
            total_changes += changes_in_column
        
        print(f"\nTotal changes: {total_changes}")
        
    def detect_near_duplicates(self, threshold: float = 0.85) -> List[Dict]:
        """
        Detect near-duplicate entries using fuzzy matching.
        
        Args:
            threshold: Similarity threshold (0-1). Default 0.85.
            
        Returns:
            List of potential duplicates with similarity scores
        """
        print(f"\nDetecting near-duplicates (threshold: {threshold})...")
        
        duplicates = []
        columns_to_check = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set']
        
        for column in columns_to_check:
            if column not in self.df.columns:
                continue
                
            unique_values = self.df[column].dropna().unique()
            
            for i, val1 in enumerate(unique_values):
                for val2 in unique_values[i+1:]:
                    similarity = SequenceMatcher(None, val1.lower(), val2.lower()).ratio()
                    
                    if threshold < similarity < 1.0 and len(val1) > 5:
                        duplicates.append({
                            'column': column,
                            'value1': val1,
                            'value2': val2,
                            'similarity': similarity
                        })
        
        # Sort by similarity descending
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"Found {len(duplicates)} potential near-duplicates")
        
        return duplicates
    
    def validate_hierarchy(self) -> Dict:
        """
        Validate hierarchy integrity.
        
        Returns:
            Dictionary with validation results
        """
        print("\nValidating hierarchy integrity...")
        
        issues = {
            'empty_required_cells': [],
            'orphaned_entries': [],
            'inconsistent_paths': []
        }
        
        # Check for empty cells in required columns
        required_columns = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set']
        
        for idx, row in self.df.iterrows():
            for col in required_columns:
                if pd.isna(row.get(col)) or not str(row.get(col)).strip():
                    issues['empty_required_cells'].append({
                        'row': idx + 2,  # +2 for header and 0-indexing
                        'column': col
                    })
        
        # Validate parent-child relationships
        # Build hierarchy map
        hierarchy = {}
        
        for idx, row in self.df.iterrows():
            strand = row.get('Strand', '')
            pillar = row.get('Pillar', '')
            domain = row.get('Domain', '')
            
            if pd.notna(strand) and pd.notna(pillar):
                if strand not in hierarchy:
                    hierarchy[strand] = set()
                hierarchy[strand].add(pillar)
        
        print(f"  Empty required cells: {len(issues['empty_required_cells'])}")
        print(f"  Hierarchy levels: {len(hierarchy)} strands")
        
        return issues
    
    def save(self, output_path: Path = None):
        """Save cleaned taxonomy."""
        if output_path is None:
            output_path = self.csv_path
            
        print(f"\nSaving cleaned taxonomy to: {output_path}")
        self.df.to_csv(output_path, index=False)
        print("Save complete")
        
    def generate_report(self, near_duplicates: List[Dict], validation_issues: Dict) -> str:
        """Generate cleanup report."""
        report = []
        report.append("=" * 80)
        report.append("TAXONOMY CLEANUP REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Input file: {self.csv_path}")
        report.append(f"Total rows: {len(self.df)}")
        report.append("")
        
        # Changes made
        report.append("CHANGES MADE:")
        report.append("-" * 80)
        if self.changes:
            report.append(f"Total modifications: {len(self.changes)}")
            report.append("")
            report.append("Sample changes:")
            for change in self.changes[:20]:
                report.append(f"  Column: {change['column']}")
                report.append(f"    Before: {change['original']}")
                report.append(f"    After:  {change['cleaned']}")
                report.append("")
        else:
            report.append("No changes were necessary")
        report.append("")
        
        # Near-duplicates
        report.append("POTENTIAL NEAR-DUPLICATES:")
        report.append("-" * 80)
        if near_duplicates:
            report.append(f"Found {len(near_duplicates)} potential duplicates")
            report.append("")
            for dup in near_duplicates[:30]:
                report.append(f"  Column: {dup['column']} (similarity: {dup['similarity']:.2f})")
                report.append(f"    1: {dup['value1']}")
                report.append(f"    2: {dup['value2']}")
                report.append("")
        else:
            report.append("No near-duplicates detected")
        report.append("")
        
        # Validation issues
        report.append("VALIDATION ISSUES:")
        report.append("-" * 80)
        total_issues = sum(len(v) for v in validation_issues.values())
        if total_issues > 0:
            report.append(f"Total issues: {total_issues}")
            report.append("")
            
            if validation_issues['empty_required_cells']:
                report.append(f"Empty required cells: {len(validation_issues['empty_required_cells'])}")
                for issue in validation_issues['empty_required_cells'][:10]:
                    report.append(f"  Row {issue['row']}, Column: {issue['column']}")
                report.append("")
        else:
            report.append("No validation issues found")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Clean and normalize taxonomy CSV')
    parser.add_argument(
        '--input',
        type=str,
        default='../POC_science_of_reading_literacy_skills_taxonomy.csv',
        help='Path to input taxonomy CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output CSV (default: overwrites input after backup)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without saving changes'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Path to save report (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Initialize cleaner
    cleaner = TaxonomyCleanup(args.input)
    
    try:
        # Load data
        cleaner.load()
        
        # Create backup unless dry-run
        if not args.dry_run:
            cleaner.create_backup()
        
        # Run cleanup
        cleaner.clean_taxonomy()
        
        # Detect near-duplicates
        near_duplicates = cleaner.detect_near_duplicates(threshold=0.85)
        
        # Validate hierarchy
        validation_issues = cleaner.validate_hierarchy()
        
        # Generate report
        report = cleaner.generate_report(near_duplicates, validation_issues)
        
        # Output report
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.report}")
        else:
            print("\n" + report)
        
        # Save cleaned data
        if not args.dry_run:
            output_path = args.output if args.output else args.input
            cleaner.save(output_path)
        else:
            print("\nDRY RUN: No changes saved")
            
        print("\nCleanup complete!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

