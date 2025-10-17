"""Shared data access layer for Snowflake and local CSV data.

This module provides unified data loading across all three project domains.
"""

from .snowflake_connector import SkillDataLoader

__all__ = ['SkillDataLoader']

