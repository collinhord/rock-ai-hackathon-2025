"""
CSV to SQLite Database Migration Script

Creates a normalized relational SQLite database from the taxonomy CSV and UUID mapping.
The database structure enables high-performance validation and hierarchical queries.

Usage:
    python csv_to_db.py [--csv taxonomy.csv] [--uuid-map uuid_map.json] [--db taxonomy.db]
"""

import sqlite3
import pandas as pd
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TaxonomyDatabase:
    """Manages taxonomy database creation and population."""
    
    def __init__(self, db_path: Path):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        
    def __enter__(self):
        """Context manager entry."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()
            
    def create_schema(self):
        """Create database schema."""
        print("Creating database schema...")
        
        # Taxonomy nodes table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxonomy_nodes (
                uuid TEXT PRIMARY KEY,
                level TEXT NOT NULL,
                name TEXT NOT NULL,
                parent_uuid TEXT,
                full_path TEXT NOT NULL UNIQUE,
                path_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_uuid) REFERENCES taxonomy_nodes(uuid)
            )
        ''')
        
        # Create indexes
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_nodes_level ON taxonomy_nodes(level)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_nodes_parent ON taxonomy_nodes(parent_uuid)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_nodes_name ON taxonomy_nodes(name)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_nodes_path_hash ON taxonomy_nodes(path_hash)
        ''')
        
        # Taxonomy hierarchy table (closure table for efficient querying)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxonomy_hierarchy (
                ancestor_uuid TEXT NOT NULL,
                descendant_uuid TEXT NOT NULL,
                depth INTEGER NOT NULL,
                PRIMARY KEY (ancestor_uuid, descendant_uuid),
                FOREIGN KEY (ancestor_uuid) REFERENCES taxonomy_nodes(uuid),
                FOREIGN KEY (descendant_uuid) REFERENCES taxonomy_nodes(uuid)
            )
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hierarchy_ancestor ON taxonomy_hierarchy(ancestor_uuid)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hierarchy_descendant ON taxonomy_hierarchy(descendant_uuid)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_hierarchy_depth ON taxonomy_hierarchy(depth)
        ''')
        
        # Taxonomy metadata table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxonomy_metadata (
                uuid TEXT PRIMARY KEY,
                annotation TEXT,
                examples TEXT,
                FOREIGN KEY (uuid) REFERENCES taxonomy_nodes(uuid)
            )
        ''')
        
        # Version tracking table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxonomy_versions (
                version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_csv TEXT,
                notes TEXT
            )
        ''')
        
        print("Schema created successfully")
        
    def insert_node(self, uuid: str, level: str, name: str, 
                   parent_uuid: Optional[str], full_path: str, path_hash: str):
        """Insert a taxonomy node."""
        self.cursor.execute('''
            INSERT OR REPLACE INTO taxonomy_nodes 
            (uuid, level, name, parent_uuid, full_path, path_hash, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (uuid, level, name, parent_uuid, full_path, path_hash))
        
    def insert_hierarchy_relation(self, ancestor_uuid: str, descendant_uuid: str, depth: int):
        """Insert a hierarchy relationship."""
        self.cursor.execute('''
            INSERT OR REPLACE INTO taxonomy_hierarchy 
            (ancestor_uuid, descendant_uuid, depth)
            VALUES (?, ?, ?)
        ''', (ancestor_uuid, descendant_uuid, depth))
        
    def insert_metadata(self, uuid: str, annotation: str, examples: str):
        """Insert taxonomy metadata."""
        self.cursor.execute('''
            INSERT OR REPLACE INTO taxonomy_metadata 
            (uuid, annotation, examples)
            VALUES (?, ?, ?)
        ''', (uuid, annotation, examples))
        
    def insert_version(self, source_csv: str, notes: str):
        """Insert version record."""
        self.cursor.execute('''
            INSERT INTO taxonomy_versions (source_csv, notes)
            VALUES (?, ?)
        ''', (source_csv, notes))
        
    def get_node_count(self) -> int:
        """Get total node count."""
        self.cursor.execute('SELECT COUNT(*) FROM taxonomy_nodes')
        return self.cursor.fetchone()[0]
        
    def get_hierarchy_count(self) -> int:
        """Get total hierarchy relations count."""
        self.cursor.execute('SELECT COUNT(*) FROM taxonomy_hierarchy')
        return self.cursor.fetchone()[0]


class TaxonomyMigrator:
    """Migrates taxonomy from CSV to SQLite database."""
    
    def __init__(self, csv_path: Path, uuid_map_path: Path, db_path: Path):
        """Initialize migrator."""
        self.csv_path = Path(csv_path)
        self.uuid_map_path = Path(uuid_map_path)
        self.db_path = Path(db_path)
        self.df = None
        self.uuid_map = None
        
    def load_data(self):
        """Load CSV and UUID mapping."""
        print(f"Loading taxonomy CSV: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        print(f"  Loaded {len(self.df)} rows")
        
        print(f"Loading UUID mapping: {self.uuid_map_path}")
        with open(self.uuid_map_path, 'r') as f:
            self.uuid_map = json.load(f)
        print(f"  Loaded {len(self.uuid_map['entries'])} UUID mappings")
        
    def build_taxonomy_path(self, row: pd.Series) -> str:
        """Build full taxonomy path from row."""
        levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        path_parts = []
        
        for level in levels:
            value = row.get(level, '')
            if pd.notna(value) and str(value).strip():
                path_parts.append(str(value).strip())
        
        return ' > '.join(path_parts)
    
    def get_level_map(self, row: pd.Series) -> Dict[str, Tuple[str, str]]:
        """
        Get mapping of level names to (value, uuid) for a row.
        
        Returns: {level_name: (value, uuid), ...}
        """
        levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        level_map = {}
        path_parts = []
        
        for level in levels:
            value = row.get(level, '')
            if pd.notna(value) and str(value).strip():
                path_parts.append(str(value).strip())
                partial_path = ' > '.join(path_parts)
                
                # Get UUID for this partial path
                uuid = self.uuid_map['forward_map'].get(partial_path, None)
                level_map[level] = (str(value).strip(), uuid)
        
        return level_map
    
    def migrate(self):
        """Perform migration from CSV to database."""
        print(f"\nMigrating to database: {self.db_path}")
        
        # Remove existing database if it exists
        if self.db_path.exists():
            print(f"  Removing existing database...")
            self.db_path.unlink()
        
        with TaxonomyDatabase(self.db_path) as db:
            # Create schema
            db.create_schema()
            
            # Track unique paths we've seen
            seen_paths = set()
            
            # Process each row - create nodes for ALL levels in the hierarchy
            print("\nInserting taxonomy nodes...")
            for idx, row in self.df.iterrows():
                # Get level map (values and UUIDs for each level)
                level_map = self.get_level_map(row)
                
                # Process each level in the hierarchy
                levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
                path_parts = []
                
                for i, level in enumerate(levels):
                    if level not in level_map:
                        continue
                    
                    value, uuid = level_map[level]
                    path_parts.append(value)
                    taxonomy_path = ' > '.join(path_parts)
                    
                    # Skip if we've already processed this path
                    if taxonomy_path in seen_paths:
                        continue
                    seen_paths.add(taxonomy_path)
                    
                    # Get UUID for this path
                    if not uuid:
                        uuid = self.uuid_map['forward_map'].get(taxonomy_path)
                    
                    if not uuid:
                        print(f"Warning: No UUID found for path: {taxonomy_path}")
                        continue
                    
                    # Find parent UUID (previous level's UUID)
                    parent_uuid = None
                    if i > 0:
                        parent_level = levels[i-1]
                        if parent_level in level_map:
                            parent_uuid = level_map[parent_level][1]
                    
                    # Get path hash
                    path_hash = None
                    for entry in self.uuid_map['entries']:
                        if entry['taxonomy_path'] == taxonomy_path:
                            path_hash = entry['path_hash']
                            break
                    
                    # Insert node for this level
                    db.insert_node(
                        uuid=uuid,
                        level=level,
                        name=value,
                        parent_uuid=parent_uuid,
                        full_path=taxonomy_path,
                        path_hash=path_hash or ''
                    )
                    
                    # Insert metadata (only for deepest level with annotation)
                    if level == 'Skill Subset' or (i == len([l for l in levels if l in level_map]) - 1):
                        annotation = row.get('Skill Subset Annotation', '')
                        db.insert_metadata(
                            uuid=uuid,
                            annotation=str(annotation) if pd.notna(annotation) else '',
                            examples=''
                        )
                
                if (idx + 1) % 100 == 0:
                    print(f"  Processed {idx + 1} rows...")
            
            print(f"  Inserted {db.get_node_count()} nodes")
            
            # Build hierarchy closure table
            print("\nBuilding hierarchy relationships...")
            self._build_hierarchy_closure(db)
            
            print(f"  Created {db.get_hierarchy_count()} hierarchy relationships")
            
            # Insert version record
            db.insert_version(
                source_csv=str(self.csv_path),
                notes=f"Initial migration from {self.csv_path.name}"
            )
            
        print("\nMigration complete!")
        
    def _build_hierarchy_closure(self, db: TaxonomyDatabase):
        """Build closure table for hierarchy relationships."""
        # Get all nodes
        db.cursor.execute('SELECT uuid, parent_uuid FROM taxonomy_nodes')
        nodes = db.cursor.fetchall()
        
        # Build parent-child map
        children = {}
        for uuid, parent_uuid in nodes:
            if parent_uuid:
                if parent_uuid not in children:
                    children[parent_uuid] = []
                children[parent_uuid].append(uuid)
        
        # Build closure table using recursive descent
        def add_descendants(ancestor_uuid: str, depth: int = 0):
            """Recursively add all descendants."""
            # Add self-reference
            db.insert_hierarchy_relation(ancestor_uuid, ancestor_uuid, depth)
            
            # Add children and their descendants
            if ancestor_uuid in children:
                for child_uuid in children[ancestor_uuid]:
                    db.insert_hierarchy_relation(ancestor_uuid, child_uuid, depth + 1)
                    add_descendants(child_uuid, depth + 1)
        
        # Find root nodes (nodes with no parent)
        root_nodes = [uuid for uuid, parent_uuid in nodes if parent_uuid is None]
        
        for root_uuid in root_nodes:
            add_descendants(root_uuid)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Migrate taxonomy to SQLite database')
    parser.add_argument(
        '--csv',
        type=str,
        default='../POC_science_of_reading_literacy_skills_taxonomy.csv',
        help='Path to taxonomy CSV'
    )
    parser.add_argument(
        '--uuid-map',
        type=str,
        default='../taxonomy_uuid_map.json',
        help='Path to UUID mapping JSON'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='../taxonomy.db',
        help='Path to output SQLite database'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize migrator
        migrator = TaxonomyMigrator(
            csv_path=Path(args.csv),
            uuid_map_path=Path(args.uuid_map),
            db_path=Path(args.db)
        )
        
        # Load data
        migrator.load_data()
        
        # Perform migration
        migrator.migrate()
        
        print(f"\nDatabase created: {args.db}")
        print(f"\nYou can query the database using:")
        print(f"  sqlite3 {args.db}")
        print(f"\nExample queries:")
        print(f"  -- Get all top-level strands")
        print(f"  SELECT * FROM taxonomy_nodes WHERE level='Strand';")
        print(f"  -- Get children of a node")
        print(f"  SELECT * FROM taxonomy_nodes WHERE parent_uuid='<uuid>';")
        print(f"  -- Get all descendants")
        print(f"  SELECT n.* FROM taxonomy_nodes n")
        print(f"  JOIN taxonomy_hierarchy h ON n.uuid = h.descendant_uuid")
        print(f"  WHERE h.ancestor_uuid = '<uuid>';")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

