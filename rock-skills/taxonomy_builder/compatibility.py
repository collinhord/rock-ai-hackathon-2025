"""
Compatibility Layer for Taxonomy Access

Provides adapter functions to access taxonomy data in multiple formats:
- CSV (original format, maintains backward compatibility)
- JSON UUID mapping
- SQLite database

This ensures existing scripts continue working while new tools can leverage
the database for high-performance queries.
"""

import pandas as pd
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class TaxonomyNode:
    """Represents a single taxonomy node."""
    uuid: str
    level: str
    name: str
    parent_uuid: Optional[str]
    full_path: str
    path_hash: str
    annotation: Optional[str] = None
    

class TaxonomyAccess:
    """Unified interface for accessing taxonomy data."""
    
    def __init__(self, base_path: Union[str, Path] = None):
        """
        Initialize taxonomy access.
        
        Args:
            base_path: Base directory containing taxonomy files.
                      Defaults to parent of this file.
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.csv_path = self.base_path / 'POC_science_of_reading_literacy_skills_taxonomy.csv'
        self.uuid_map_path = self.base_path / 'taxonomy_uuid_map.json'
        self.db_path = self.base_path / 'taxonomy.db'
        
        # Lazy-loaded caches
        self._csv_df = None
        self._uuid_map = None
        self._db_conn = None
        
    def load_csv(self) -> pd.DataFrame:
        """
        Load taxonomy CSV.
        
        Returns:
            DataFrame with taxonomy data
        """
        if self._csv_df is None:
            self._csv_df = pd.read_csv(self.csv_path)
        return self._csv_df
    
    def load_uuid_map(self) -> Dict:
        """
        Load UUID mapping.
        
        Returns:
            Dictionary with UUID mappings
        """
        if self._uuid_map is None:
            with open(self.uuid_map_path, 'r') as f:
                self._uuid_map = json.load(f)
        return self._uuid_map
    
    def get_db_connection(self) -> sqlite3.Connection:
        """
        Get database connection.
        
        Returns:
            SQLite connection
        """
        if self._db_conn is None:
            self._db_conn = sqlite3.connect(self.db_path)
            # Enable row factory for dict-like access
            self._db_conn.row_factory = sqlite3.Row
        return self._db_conn
    
    def close(self):
        """Close database connection."""
        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # CSV-compatible methods (for backward compatibility)
    
    def get_taxonomy_df(self) -> pd.DataFrame:
        """
        Get taxonomy as DataFrame (CSV format).
        
        BACKWARD COMPATIBLE: Drop-in replacement for direct CSV loading.
        """
        return self.load_csv()
    
    def build_taxonomy_path(self, row: Union[pd.Series, Dict]) -> str:
        """
        Build taxonomy path from row data.
        
        Args:
            row: Pandas Series or dict with taxonomy levels
            
        Returns:
            Full taxonomy path string
        """
        levels = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        path_parts = []
        
        for level in levels:
            if isinstance(row, dict):
                value = row.get(level, '')
            else:
                value = row.get(level, '')
            
            if pd.notna(value) and str(value).strip():
                path_parts.append(str(value).strip())
        
        return ' > '.join(path_parts)
    
    # UUID mapping methods
    
    def path_to_uuid(self, taxonomy_path: str) -> Optional[str]:
        """
        Convert taxonomy path to UUID.
        
        Args:
            taxonomy_path: Full taxonomy path string
            
        Returns:
            UUID or None if not found
        """
        uuid_map = self.load_uuid_map()
        return uuid_map['forward_map'].get(taxonomy_path)
    
    def uuid_to_path(self, uuid: str) -> Optional[str]:
        """
        Convert UUID to taxonomy path.
        
        Args:
            uuid: Taxonomy UUID
            
        Returns:
            Full taxonomy path or None if not found
        """
        uuid_map = self.load_uuid_map()
        return uuid_map['reverse_map'].get(uuid)
    
    def get_node_by_uuid(self, uuid: str) -> Optional[TaxonomyNode]:
        """
        Get taxonomy node by UUID.
        
        Args:
            uuid: Taxonomy UUID
            
        Returns:
            TaxonomyNode or None if not found
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
            FROM taxonomy_nodes n
            LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
            WHERE n.uuid = ?
        ''', (uuid,))
        
        row = cursor.fetchone()
        if row:
            return TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
        return None
    
    def get_node_by_path(self, taxonomy_path: str) -> Optional[TaxonomyNode]:
        """
        Get taxonomy node by full path.
        
        Args:
            taxonomy_path: Full taxonomy path string
            
        Returns:
            TaxonomyNode or None if not found
        """
        uuid = self.path_to_uuid(taxonomy_path)
        if uuid:
            return self.get_node_by_uuid(uuid)
        return None
    
    # Database query methods (high performance)
    
    def get_children(self, uuid: str) -> List[TaxonomyNode]:
        """
        Get immediate children of a node.
        
        Args:
            uuid: Parent UUID
            
        Returns:
            List of child TaxonomyNodes
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
            FROM taxonomy_nodes n
            LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
            WHERE n.parent_uuid = ?
            ORDER BY n.name
        ''', (uuid,))
        
        return [
            TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
            for row in cursor.fetchall()
        ]
    
    def get_descendants(self, uuid: str, max_depth: Optional[int] = None) -> List[TaxonomyNode]:
        """
        Get all descendants of a node.
        
        Args:
            uuid: Ancestor UUID
            max_depth: Maximum depth to traverse (None = unlimited)
            
        Returns:
            List of descendant TaxonomyNodes
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        if max_depth is not None:
            cursor.execute('''
                SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
                FROM taxonomy_nodes n
                JOIN taxonomy_hierarchy h ON n.uuid = h.descendant_uuid
                LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
                WHERE h.ancestor_uuid = ? AND h.depth <= ? AND h.depth > 0
                ORDER BY h.depth, n.name
            ''', (uuid, max_depth))
        else:
            cursor.execute('''
                SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
                FROM taxonomy_nodes n
                JOIN taxonomy_hierarchy h ON n.uuid = h.descendant_uuid
                LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
                WHERE h.ancestor_uuid = ? AND h.depth > 0
                ORDER BY h.depth, n.name
            ''', (uuid,))
        
        return [
            TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
            for row in cursor.fetchall()
        ]
    
    def get_ancestors(self, uuid: str) -> List[TaxonomyNode]:
        """
        Get all ancestors of a node.
        
        Args:
            uuid: Descendant UUID
            
        Returns:
            List of ancestor TaxonomyNodes (ordered from root to parent)
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
            FROM taxonomy_nodes n
            JOIN taxonomy_hierarchy h ON n.uuid = h.ancestor_uuid
            LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
            WHERE h.descendant_uuid = ? AND h.depth > 0
            ORDER BY h.depth DESC
        ''', (uuid,))
        
        return [
            TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
            for row in cursor.fetchall()
        ]
    
    def get_nodes_by_level(self, level: str) -> List[TaxonomyNode]:
        """
        Get all nodes at a specific level.
        
        Args:
            level: Level name (e.g., 'Strand', 'Pillar', 'Domain', etc.)
            
        Returns:
            List of TaxonomyNodes at that level
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
            FROM taxonomy_nodes n
            LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
            WHERE n.level = ?
            ORDER BY n.name
        ''', (level,))
        
        return [
            TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
            for row in cursor.fetchall()
        ]
    
    def search_nodes(self, query: str, level: Optional[str] = None) -> List[TaxonomyNode]:
        """
        Search for nodes by name.
        
        Args:
            query: Search query (partial match)
            level: Optional level filter
            
        Returns:
            List of matching TaxonomyNodes
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        if level:
            cursor.execute('''
                SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
                FROM taxonomy_nodes n
                LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
                WHERE n.name LIKE ? AND n.level = ?
                ORDER BY n.name
            ''', (f'%{query}%', level))
        else:
            cursor.execute('''
                SELECT n.uuid, n.level, n.name, n.parent_uuid, n.full_path, n.path_hash, m.annotation
                FROM taxonomy_nodes n
                LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
                WHERE n.name LIKE ?
                ORDER BY n.level, n.name
            ''', (f'%{query}%',))
        
        return [
            TaxonomyNode(
                uuid=row['uuid'],
                level=row['level'],
                name=row['name'],
                parent_uuid=row['parent_uuid'],
                full_path=row['full_path'],
                path_hash=row['path_hash'],
                annotation=row['annotation']
            )
            for row in cursor.fetchall()
        ]
    
    # Migration helpers
    
    def regenerate_csv_from_db(self, output_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Regenerate CSV from database.
        
        Args:
            output_path: Optional path to save CSV
            
        Returns:
            DataFrame with taxonomy data
        """
        conn = self.get_db_connection()
        
        # Query all nodes with metadata
        query = '''
            SELECT 
                n.full_path,
                n.uuid,
                m.annotation
            FROM taxonomy_nodes n
            LEFT JOIN taxonomy_metadata m ON n.uuid = m.uuid
            ORDER BY n.full_path
        '''
        
        df = pd.read_sql_query(query, conn)
        
        # Split full_path into columns
        path_columns = ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']
        paths = df['full_path'].str.split(' > ', expand=True)
        
        # Assign to columns (pad with None if needed)
        for i, col in enumerate(path_columns):
            if i < len(paths.columns):
                df[col] = paths[i]
            else:
                df[col] = None
        
        # Rename annotation column
        df = df.rename(columns={'annotation': 'Skill Subset Annotation'})
        
        # Reorder columns to match original CSV
        final_columns = path_columns + ['Skill Subset Annotation']
        df = df[final_columns]
        
        if output_path:
            df.to_csv(output_path, index=False)
        
        return df


# Convenience function for backward compatibility
def load_taxonomy_csv(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load taxonomy CSV (backward compatible).
    
    Args:
        base_path: Base directory containing taxonomy files
        
    Returns:
        DataFrame with taxonomy data
    """
    accessor = TaxonomyAccess(base_path)
    return accessor.get_taxonomy_df()


# Example usage
if __name__ == '__main__':
    # Demonstrate usage
    with TaxonomyAccess() as tax:
        print("=== Taxonomy Access Demo ===\n")
        
        # Get taxonomy as DataFrame (backward compatible)
        df = tax.get_taxonomy_df()
        print(f"Loaded {len(df)} rows from CSV\n")
        
        # Get UUID for a path
        path = df.iloc[0]
        taxonomy_path = tax.build_taxonomy_path(path)
        uuid = tax.path_to_uuid(taxonomy_path)
        print(f"Path: {taxonomy_path}")
        print(f"UUID: {uuid}\n")
        
        # Get node details
        node = tax.get_node_by_uuid(uuid)
        if node:
            print(f"Node: {node.name}")
            print(f"Level: {node.level}")
            print(f"Path: {node.full_path}\n")
        
        # Get strands
        strands = tax.get_nodes_by_level('Strand')
        print(f"Found {len(strands)} strands:")
        for strand in strands:
            print(f"  - {strand.name}")
        
        print("\nDone!")

