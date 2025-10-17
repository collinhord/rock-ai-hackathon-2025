"""
Database Manager for Taxonomy

Provides CRUD operations for base skills, specifications, and mappings.
Supports both JSON storage and SQLite querying.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class TaxonomyDB:
    """Database manager for base skills, specifications, and mappings."""
    
    def __init__(self, db_path: str = None, json_dir: str = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database (default: taxonomy.db)
            json_dir: Path to JSON taxonomy directory (default: ../taxonomy)
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "taxonomy.db"
        if json_dir is None:
            json_dir = Path(__file__).parent.parent / "taxonomy"
        
        self.db_path = Path(db_path)
        self.json_dir = Path(json_dir)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Base Skills Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS base_skills (
                base_skill_id TEXT PRIMARY KEY,
                base_skill_name TEXT UNIQUE NOT NULL,
                base_skill_description TEXT,
                skill_family TEXT,
                cognitive_category TEXT,
                rock_skills_count INTEGER DEFAULT 0,
                created_by TEXT,
                validation_status TEXT DEFAULT 'pending',
                created_timestamp TEXT,
                updated_timestamp TEXT
            )
        """)
        
        # ROCK Skill Mappings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rock_skill_mappings (
                rock_skill_id TEXT PRIMARY KEY,
                rock_skill_name TEXT NOT NULL,
                base_skill_id TEXT NOT NULL,
                extraction_confidence TEXT,
                extraction_timestamp TEXT,
                human_validated BOOLEAN DEFAULT 0,
                FOREIGN KEY (base_skill_id) REFERENCES base_skills(base_skill_id)
            )
        """)
        
        # Specifications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_specifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rock_skill_id TEXT NOT NULL,
                spec_type TEXT NOT NULL,
                spec_value TEXT NOT NULL,
                spec_confidence TEXT,
                FOREIGN KEY (rock_skill_id) REFERENCES rock_skill_mappings(rock_skill_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_base_skill_name ON base_skills(base_skill_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mapping_base ON rock_skill_mappings(base_skill_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_spec_type ON skill_specifications(spec_type, spec_value)")
        
        conn.commit()
        conn.close()
    
    def add_base_skill(self, base_skill: Dict) -> str:
        """
        Add a base skill to the database.
        
        Args:
            base_skill: Dictionary with base skill data
            
        Returns:
            base_skill_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO base_skills 
            (base_skill_id, base_skill_name, base_skill_description, skill_family,
             cognitive_category, rock_skills_count, created_by, validation_status,
             created_timestamp, updated_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            base_skill['base_skill_id'],
            base_skill['base_skill_name'],
            base_skill.get('base_skill_description', ''),
            base_skill.get('skill_family', 'Unknown'),
            base_skill.get('cognitive_category', 'comprehension'),
            base_skill.get('rock_skills_count', 0),
            base_skill.get('created_by', 'unknown'),
            base_skill.get('validation_status', 'pending'),
            base_skill.get('created_timestamp', datetime.utcnow().isoformat()),
            base_skill.get('updated_timestamp', datetime.utcnow().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        # Also save JSON
        json_file = self.json_dir / "base_skills" / f"{base_skill['base_skill_id']}.json"
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w') as f:
            json.dump(base_skill, f, indent=2)
        
        return base_skill['base_skill_id']
    
    def get_base_skill(self, base_skill_id: str) -> Optional[Dict]:
        """Get a base skill by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM base_skills WHERE base_skill_id = ?", (base_skill_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def search_base_skills(self, query: str) -> List[Dict]:
        """Search base skills by name (case-insensitive)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM base_skills 
            WHERE base_skill_name LIKE ? OR base_skill_description LIKE ?
        """, (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_rock_skills_by_base(self, base_skill_id: str) -> List[Dict]:
        """Get all ROCK skills mapped to a base skill."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM rock_skill_mappings
            WHERE base_skill_id = ?
        """, (base_skill_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_rock_skills_by_specs(self, spec_filters: Dict[str, str]) -> List[Dict]:
        """
        Get ROCK skills matching specification filters.
        
        Args:
            spec_filters: Dictionary of {spec_type: spec_value}
            
        Returns:
            List of ROCK skill dictionaries
        """
        if not spec_filters:
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query for multiple spec filters
        query = """
            SELECT DISTINCT m.* FROM rock_skill_mappings m
            WHERE m.rock_skill_id IN (
                SELECT rock_skill_id FROM skill_specifications
                WHERE """
        
        conditions = []
        params = []
        for spec_type, spec_value in spec_filters.items():
            conditions.append("(spec_type = ? AND spec_value = ?)")
            params.extend([spec_type, spec_value])
        
        query += " OR ".join(conditions)
        query += f" GROUP BY rock_skill_id HAVING COUNT(DISTINCT spec_type) = {len(spec_filters)})"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_rock_skill_mapping(self, mapping: Dict) -> bool:
        """Add a ROCK skill → base skill mapping."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO rock_skill_mappings
                (rock_skill_id, rock_skill_name, base_skill_id, extraction_confidence,
                 extraction_timestamp, human_validated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mapping['rock_skill_id'],
                mapping['rock_skill_name'],
                mapping['base_skill_id'],
                mapping.get('extraction_confidence', 'medium'),
                mapping.get('extraction_timestamp', datetime.utcnow().isoformat()),
                mapping.get('human_validated', False)
            ))
            
            # Add specifications
            if 'specifications' in mapping:
                for spec in mapping['specifications']:
                    cursor.execute("""
                        INSERT INTO skill_specifications
                        (rock_skill_id, spec_type, spec_value, spec_confidence)
                        VALUES (?, ?, ?, ?)
                    """, (
                        mapping['rock_skill_id'],
                        spec['spec_type'],
                        spec['spec_value'],
                        spec.get('spec_confidence', 'medium')
                    ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding mapping: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_all_base_skills(self) -> List[Dict]:
        """Get all base skills."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM base_skills ORDER BY base_skill_name")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get taxonomy statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count base skills
        cursor.execute("SELECT COUNT(*) FROM base_skills")
        stats['total_base_skills'] = cursor.fetchone()[0]
        
        # Count ROCK skills
        cursor.execute("SELECT COUNT(*) FROM rock_skill_mappings")
        stats['total_rock_skills'] = cursor.fetchone()[0]
        
        # Count mapped skills
        cursor.execute("SELECT COUNT(*) FROM rock_skill_mappings WHERE base_skill_id IS NOT NULL")
        stats['mapped_rock_skills'] = cursor.fetchone()[0]
        
        # Average skills per base
        if stats['total_base_skills'] > 0:
            stats['avg_skills_per_base'] = stats['total_rock_skills'] / stats['total_base_skills']
        else:
            stats['avg_skills_per_base'] = 0
        
        conn.close()
        
        return stats


class QueryBuilder:
    """Flexible query builder for base skills + specifications."""
    
    def __init__(self, db_path: str = None):
        """Initialize query builder."""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "taxonomy.db"
        
        self.db_path = Path(db_path)
        self.filters = {
            'base_skills': [],
            'specifications': [],
            'exclusions': []
        }
    
    def base_skill(self, name: str):
        """Filter by base skill name."""
        self.filters['base_skills'].append(name)
        return self
    
    def specification(self, spec_type: str, spec_value: str):
        """Filter by specification."""
        self.filters['specifications'].append((spec_type, spec_value))
        return self
    
    def exclude_specification(self, spec_type: str, spec_value: str):
        """Exclude skills with this specification."""
        self.filters['exclusions'].append((spec_type, spec_value))
        return self
    
    def execute(self) -> List[Dict]:
        """Execute the query and return results."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build SQL query
        query = "SELECT DISTINCT m.* FROM rock_skill_mappings m"
        conditions = []
        params = []
        
        # Base skill filter
        if self.filters['base_skills']:
            query += " JOIN base_skills b ON m.base_skill_id = b.base_skill_id"
            placeholders = ', '.join(['?' for _ in self.filters['base_skills']])
            conditions.append(f"b.base_skill_name IN ({placeholders})")
            params.extend(self.filters['base_skills'])
        
        # Specification filters
        if self.filters['specifications']:
            query += " JOIN skill_specifications s ON m.rock_skill_id = s.rock_skill_id"
            spec_conditions = []
            for spec_type, spec_value in self.filters['specifications']:
                spec_conditions.append("(s.spec_type = ? AND s.spec_value = ?)")
                params.extend([spec_type, spec_value])
            conditions.append(f"({' OR '.join(spec_conditions)})")
        
        # Exclusion filters
        if self.filters['exclusions']:
            exclusion_ids = []
            for spec_type, spec_value in self.filters['exclusions']:
                cursor.execute("""
                    SELECT rock_skill_id FROM skill_specifications
                    WHERE spec_type = ? AND spec_value = ?
                """, (spec_type, spec_value))
                exclusion_ids.extend([row[0] for row in cursor.fetchall()])
            
            if exclusion_ids:
                placeholders = ', '.join(['?' for _ in exclusion_ids])
                conditions.append(f"m.rock_skill_id NOT IN ({placeholders})")
                params.extend(exclusion_ids)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def reset(self):
        """Reset all filters."""
        self.filters = {
            'base_skills': [],
            'specifications': [],
            'exclusions': []
        }
        return self

