#!/usr/bin/env python3
"""
Script Name: generate_reports.py
Purpose: Generate summary reports and analytics
Tier: 3 (Utility)

Usage:
  python3 scripts/utils/generate_reports.py
  python3 scripts/utils/generate_reports.py --output reports/

Outputs:
  - analysis/reports/summary_TIMESTAMP.txt
  - analysis/reports/metrics_TIMESTAMP.json
  
Estimated Time: 1-2 minutes
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

def generate_summary_report(db_path, output_dir):
    """Generate text summary report."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_dir / f'summary_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("═" * 70 + "\n")
        f.write("ROCK Skills Taxonomy - Summary Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("═" * 70 + "\n\n")
        
        # Base Skills
        cursor.execute('SELECT COUNT(*) FROM base_skills')
        base_count = cursor.fetchone()[0]
        f.write(f"Base Skills: {base_count}\n")
        
        # ROCK Skills
        cursor.execute('SELECT COUNT(*) FROM rock_skill_mappings')
        rock_count = cursor.fetchone()[0]
        f.write(f"ROCK Skills Mapped: {rock_count}\n")
        
        # Specifications
        cursor.execute('SELECT COUNT(*) FROM specifications')
        spec_count = cursor.fetchone()[0]
        f.write(f"Specifications: {spec_count}\n\n")
        
        # Coverage
        cursor.execute('''
            SELECT COUNT(DISTINCT rock_skill_id) 
            FROM rock_skill_mappings 
            WHERE base_skill_id IS NOT NULL
        ''')
        mapped = cursor.fetchone()[0]
        coverage = (mapped / rock_count * 100) if rock_count > 0 else 0
        f.write(f"Coverage: {coverage:.1f}%\n\n")
        
        # Top Base Skills by Frequency
        f.write("─" * 70 + "\n")
        f.write("Top 10 Most Frequent Base Skills\n")
        f.write("─" * 70 + "\n")
        
        cursor.execute('''
            SELECT 
                b.name,
                COUNT(r.rock_skill_id) as frequency
            FROM base_skills b
            LEFT JOIN rock_skill_mappings r ON b.id = r.base_skill_id
            GROUP BY b.id
            ORDER BY frequency DESC
            LIMIT 10
        ''')
        
        for i, (name, freq) in enumerate(cursor.fetchall(), 1):
            f.write(f"{i:2}. {name[:50]:<50} ({freq} mappings)\n")
        
        f.write("\n" + "═" * 70 + "\n")
    
    conn.close()
    print(f"✓ Summary report saved: {report_file}")
    return report_file

def generate_metrics_json(db_path, output_dir):
    """Generate JSON metrics file."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    metrics_file = output_dir / f'metrics_{timestamp}.json'
    
    metrics = {
        'generated_at': datetime.now().isoformat(),
        'database': str(db_path)
    }
    
    # Counts
    cursor.execute('SELECT COUNT(*) FROM base_skills')
    metrics['base_skills_count'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM rock_skill_mappings')
    metrics['rock_skills_count'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM specifications')
    metrics['specifications_count'] = cursor.fetchone()[0]
    
    # Coverage
    cursor.execute('''
        SELECT COUNT(DISTINCT rock_skill_id) 
        FROM rock_skill_mappings 
        WHERE base_skill_id IS NOT NULL
    ''')
    mapped = cursor.fetchone()[0]
    metrics['mapped_rock_skills'] = mapped
    metrics['coverage_percent'] = (mapped / metrics['rock_skills_count'] * 100) if metrics['rock_skills_count'] > 0 else 0
    
    # Specification coverage
    cursor.execute('''
        SELECT COUNT(DISTINCT base_skill_id)
        FROM specifications
    ''')
    base_with_specs = cursor.fetchone()[0]
    metrics['base_skills_with_specs'] = base_with_specs
    metrics['spec_coverage_percent'] = (base_with_specs / metrics['base_skills_count'] * 100) if metrics['base_skills_count'] > 0 else 0
    
    conn.close()
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Metrics saved: {metrics_file}")
    return metrics_file

def main():
    parser = argparse.ArgumentParser(description='Generate taxonomy reports')
    parser.add_argument('--output', default='analysis/reports', help='Output directory')
    parser.add_argument('--db', default='taxonomy.db', help='Database path')
    args = parser.parse_args()
    
    db_path = Path(args.db)
    output_dir = Path(args.output)
    
    # Check if database exists
    if not db_path.exists():
        print(f"✗ Database not found: {db_path}")
        print("  Run: ./scripts/refresh_taxonomy.sh")
        return 1
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating reports...")
    print()
    
    try:
        generate_summary_report(db_path, output_dir)
        generate_metrics_json(db_path, output_dir)
        print()
        print("✓ All reports generated successfully")
        return 0
    except Exception as e:
        print(f"✗ Error generating reports: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

