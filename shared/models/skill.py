"""Shared ROCK skill data models.

This module defines the core Skill data structure used across all three projects.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class Skill:
    """ROCK skill data model used across all projects.
    
    Attributes:
        skill_id: Unique ROCK skill identifier
        skill_name: Human-readable skill description
        skill_area_name: Skill area classification
        content_area_name: Content area (e.g., 'English Language Arts', 'Mathematics')
        grade_level_name: Grade level (e.g., 'Grade 3', 'K')
        metadata: Optional metadata from Project 1 (specification extraction)
        master_concept_id: Optional master concept ID from Project 2 (redundancy detection)
        base_skill_id: Optional base skill ID from Project 3 (base taxonomy)
    """
    
    skill_id: int
    skill_name: str
    skill_area_name: str
    content_area_name: str
    grade_level_name: str
    metadata: Optional[Dict[str, Any]] = None
    master_concept_id: Optional[str] = None
    base_skill_id: Optional[str] = None
    
    @classmethod
    def from_series(cls, row: pd.Series) -> 'Skill':
        """Create Skill instance from pandas Series.
        
        Args:
            row: pandas Series with SKILL_ID, SKILL_NAME, etc.
            
        Returns:
            Skill instance
        """
        return cls(
            skill_id=int(row['SKILL_ID']),
            skill_name=str(row['SKILL_NAME']),
            skill_area_name=str(row.get('SKILL_AREA_NAME', '')),
            content_area_name=str(row.get('CONTENT_AREA_NAME', '')),
            grade_level_name=str(row.get('GRADE_LEVEL_NAME', ''))
        )
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> list['Skill']:
        """Create list of Skill instances from DataFrame.
        
        Args:
            df: DataFrame with skill data
            
        Returns:
            List of Skill instances
        """
        return [cls.from_series(row) for _, row in df.iterrows()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Skill to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'skill_id': self.skill_id,
            'skill_name': self.skill_name,
            'skill_area_name': self.skill_area_name,
            'content_area_name': self.content_area_name,
            'grade_level_name': self.grade_level_name,
            'metadata': self.metadata,
            'master_concept_id': self.master_concept_id,
            'base_skill_id': self.base_skill_id,
        }

