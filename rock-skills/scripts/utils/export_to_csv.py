#!/usr/bin/env python3
"""
Script Name: export_to_csv.py
Purpose: Export taxonomy data from SQLite to CSV files
Tier: 3 (Utility)

Usage:
  # Export all tables
  python3 scripts/utils/export_to_csv.py
  
  # Export specific tables
  python3 scripts/utils/export_to_csv.py --tables base_skills,specifications
  
  # Custom output directory
  python3 scripts/utils/export_to_csv.py --output exports/

Outputs:
  - taxonomy/exports/base_skills_TIMESTAMP.csv
  - taxonomy/exports/specifications_TIMESTAMP.csv
  - taxonomy/exports/rock_skill_mappings_TIMESTAMP.csv
  
Estimated Time: < 1 minute
"""

import sqlite3
import csv
import sys
from pathlib import Path
from datetime import datetime
import argparse

def export_table_to_csv(cursor, table_name, output_dir):
    """Export a single table to CSV."""
    try:
        # Get all rows
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        
        if not rows:
            print(f"   ⚠️  {table_name}: No data to export")
            return None
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = output_dir / f'{table_name}_{timestamp}.csv'
        
        # Write CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"   ✓ {table_name}: {len(rows)} rows → {csv_file.name}")
        return csv_file
        
    except sqlite3.OperationalError as e:
        print(f"   ✗ {table_name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Export taxonomy to CSV')
    parser.add_argument('--db', default='taxonomy.db', help='Database path')
    parser.add_argument('--output', default='taxonomy/exports', help='Output directory')
    parser.add_argument('--tables', help='Comma-separated table names (default: all)')
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
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Determine which tables to export
    if args.tables:
        tables = [t.strip() for t in args.tables.split(',')]
    else:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Exporting {len(tables)} table(s) to {output_dir}/")
    print()
    
    exported = 0
    for table in tables:
        if export_table_to_csv(cursor, table, output_dir):
            exported += 1
    
    conn.close()
    
    print()
    print(f"✓ Exported {exported}/{len(tables)} tables")
    return 0

if __name__ == '__main__':
    sys.exit(main())

