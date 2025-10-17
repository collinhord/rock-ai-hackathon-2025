"""Unified Snowflake data access for all three projects.

This module provides a consistent interface for accessing ROCK skills data
from Snowflake, with built-in caching and connection pooling.
"""

from typing import Optional, List
import pandas as pd
import os
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class SkillDataLoader:
    """Unified data access for all three projects.
    
    Provides caching, connection pooling, and consistent
    query interface for ROCK data from Snowflake.
    
    Note: Currently uses CSV fallback for local development.
    Snowflake integration can be enabled when credentials are available.
    """
    
    def __init__(self, config_path: str = 'config/snowflake.yaml', use_local_csv: bool = True):
        """Initialize the data loader.
        
        Args:
            config_path: Path to Snowflake configuration file
            use_local_csv: If True, use local CSV files instead of Snowflake
        """
        self.use_local_csv = use_local_csv
        self._conn = None
        
        # Default paths for local CSV data
        self.csv_paths = {
            'skills': 'rock-skills/rock_data/SKILLS.csv',
            'skill_areas': 'rock-skills/rock_data/SKILL_AREAS.csv',
            'standards': 'rock-skills/rock_data/STANDARDS.csv',
            'standard_skills': 'rock-skills/rock_data/STANDARD_SKILLS.csv',
        }
        
        # Try to load config if it exists
        if Path(config_path).exists():
            self.config = self._load_config(config_path)
            self.cache_enabled = self.config.get('cache', {}).get('enabled', True)
            cache_dir = self.config.get('cache', {}).get('directory', 'data/cache/')
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            logger.warning(f"Config file {config_path} not found. Using defaults.")
            self.config = None
            self.cache_enabled = True
            self.cache_dir = Path('data/cache/')
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _connect(self):
        """Lazy connection to Snowflake.
        
        Note: Requires snowflake-connector-python package and credentials.
        """
        if self._conn is None and not self.use_local_csv:
            try:
                import snowflake.connector
                self._conn = snowflake.connector.connect(
                    account=self.config['snowflake']['account'],
                    warehouse=self.config['snowflake']['warehouse'],
                    database=self.config['snowflake']['database'],
                    schema=self.config['snowflake']['schema'],
                    user=os.getenv('SNOWFLAKE_USER'),
                    password=os.getenv('SNOWFLAKE_PASSWORD'),
                )
                logger.info("Connected to Snowflake")
            except ImportError:
                logger.warning("snowflake-connector-python not installed. Falling back to local CSV.")
                self.use_local_csv = True
            except Exception as e:
                logger.error(f"Failed to connect to Snowflake: {e}")
                logger.warning("Falling back to local CSV files.")
                self.use_local_csv = True
        
        return self._conn
    
    def get_all_skills(
        self, 
        content_area: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """Load skills with optional filtering and caching.
        
        Args:
            content_area: Filter by content area (e.g., 'English Language Arts')
            use_cache: Use cached data if available
            
        Returns:
            DataFrame with SKILL_ID, SKILL_NAME, SKILL_AREA_NAME, etc.
        """
        cache_key = f"skills_{content_area or 'all'}"
        cache_file = self.cache_dir / f"{cache_key}.csv"
        
        # Check cache
        if use_cache and self.cache_enabled and cache_file.exists():
            logger.debug(f"Loading skills from cache: {cache_file}")
            return pd.read_csv(cache_file)
        
        # Load from source
        if self.use_local_csv:
            df = self._load_from_csv('skills')
        else:
            df = self._load_from_snowflake('skills')
        
        # Filter if requested
        if content_area and 'CONTENT_AREA_NAME' in df.columns:
            df = df[df['CONTENT_AREA_NAME'] == content_area].copy()
        
        # Save to cache
        if self.cache_enabled:
            df.to_csv(cache_file, index=False)
            logger.debug(f"Saved {len(df)} skills to cache: {cache_file}")
        
        return df
    
    def _load_from_csv(self, table_name: str) -> pd.DataFrame:
        """Load data from local CSV file."""
        csv_path = self.csv_paths.get(table_name)
        if not csv_path or not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found for table: {table_name}")
        
        logger.debug(f"Loading {table_name} from CSV: {csv_path}")
        return pd.read_csv(csv_path)
    
    def _load_from_snowflake(self, table_name: str) -> pd.DataFrame:
        """Load data from Snowflake."""
        conn = self._connect()
        if conn is None:
            return self._load_from_csv(table_name)
        
        query = f"SELECT * FROM {table_name.upper()}"
        logger.debug(f"Executing Snowflake query: {query}")
        return pd.read_sql(query, conn)
    
    def get_skills_with_standards(self, skill_ids: List[int]) -> pd.DataFrame:
        """Get skills with their related standards.
        
        Joins SKILLS, STANDARD_SKILLS, STANDARDS tables.
        
        Args:
            skill_ids: List of SKILL_IDs to fetch
            
        Returns:
            DataFrame with skill and standard information
        """
        skills = self.get_all_skills()
        skills_filtered = skills[skills['SKILL_ID'].isin(skill_ids)]
        
        # Load related data
        if self.use_local_csv:
            standard_skills = self._load_from_csv('standard_skills')
            standards = self._load_from_csv('standards')
        else:
            standard_skills = self._load_from_snowflake('standard_skills')
            standards = self._load_from_snowflake('standards')
        
        # Join data
        result = skills_filtered.merge(
            standard_skills, on='SKILL_ID', how='left'
        ).merge(
            standards, on='STANDARD_ID', how='left'
        )
        
        return result
    
    def close(self):
        """Close Snowflake connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("Closed Snowflake connection")

