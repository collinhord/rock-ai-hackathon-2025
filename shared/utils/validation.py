"""Common validation utilities for data quality checks.

This module provides reusable validation functions across all projects.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate that DataFrame contains all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all required columns present, False otherwise
    """
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
    
    return True


def validate_no_nulls(df: pd.DataFrame, columns: List[str]) -> bool:
    """Validate that specified columns contain no null values.
    
    Args:
        df: DataFrame to validate
        columns: List of column names to check
        
    Returns:
        True if no nulls found, False otherwise
    """
    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column {col} not found in DataFrame")
            continue
        
        null_count = df[col].isnull().sum()
        if null_count > 0:
            logger.error(f"Column {col} contains {null_count} null values")
            return False
    
    return True


def validate_unique_values(df: pd.DataFrame, column: str) -> bool:
    """Validate that a column contains only unique values.
    
    Args:
        df: DataFrame to validate
        column: Column name to check
        
    Returns:
        True if all values are unique, False otherwise
    """
    if column not in df.columns:
        logger.error(f"Column {column} not found in DataFrame")
        return False
    
    duplicate_count = df[column].duplicated().sum()
    
    if duplicate_count > 0:
        logger.error(f"Column {column} contains {duplicate_count} duplicate values")
        return False
    
    return True


def validate_data_types(
    df: pd.DataFrame,
    type_map: Dict[str, str]
) -> bool:
    """Validate that columns have expected data types.
    
    Args:
        df: DataFrame to validate
        type_map: Dictionary mapping column names to expected types
                  (e.g., {'SKILL_ID': 'int', 'SKILL_NAME': 'object'})
        
    Returns:
        True if all types match, False otherwise
    """
    for col, expected_type in type_map.items():
        if col not in df.columns:
            logger.warning(f"Column {col} not found in DataFrame")
            continue
        
        actual_type = str(df[col].dtype)
        
        # Flexible type matching
        if expected_type == 'int' and 'int' not in actual_type:
            logger.error(f"Column {col} has type {actual_type}, expected int")
            return False
        elif expected_type == 'float' and 'float' not in actual_type:
            logger.error(f"Column {col} has type {actual_type}, expected float")
            return False
        elif expected_type == 'object' and actual_type != 'object':
            logger.error(f"Column {col} has type {actual_type}, expected object")
            return False
    
    return True


def get_validation_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive validation summary for a DataFrame.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with validation metrics
    """
    return {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': list(df.columns),
        'null_counts': df.isnull().sum().to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
    }

