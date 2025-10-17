"""Common export utilities for CSV and JSON output.

This module provides consistent data export functions across all projects.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def export_to_csv(
    df: pd.DataFrame,
    output_path: str,
    index: bool = False,
    create_dirs: bool = True,
    add_timestamp: bool = False
) -> str:
    """Export DataFrame to CSV file.
    
    Args:
        df: DataFrame to export
        output_path: Path to output CSV file
        index: Whether to include DataFrame index
        create_dirs: Whether to create parent directories
        add_timestamp: Whether to add timestamp to filename
        
    Returns:
        Actual path where file was saved
    """
    output_path_obj = Path(output_path)
    
    # Add timestamp if requested
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = output_path_obj.stem
        suffix = output_path_obj.suffix
        output_path_obj = output_path_obj.parent / f"{stem}_{timestamp}{suffix}"
    
    # Create parent directories
    if create_dirs:
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Export
    df.to_csv(output_path_obj, index=index)
    logger.info(f"Exported {len(df)} rows to {output_path_obj}")
    
    return str(output_path_obj)


def export_to_json(
    data: Any,
    output_path: str,
    indent: int = 2,
    create_dirs: bool = True,
    add_timestamp: bool = False
) -> str:
    """Export data to JSON file.
    
    Args:
        data: Data to export (dict, list, etc.)
        output_path: Path to output JSON file
        indent: JSON indentation level
        create_dirs: Whether to create parent directories
        add_timestamp: Whether to add timestamp to filename
        
    Returns:
        Actual path where file was saved
    """
    output_path_obj = Path(output_path)
    
    # Add timestamp if requested
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = output_path_obj.stem
        suffix = output_path_obj.suffix
        output_path_obj = output_path_obj.parent / f"{stem}_{timestamp}{suffix}"
    
    # Create parent directories
    if create_dirs:
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Export
    with open(output_path_obj, 'w') as f:
        json.dump(data, f, indent=indent)
    
    logger.info(f"Exported data to {output_path_obj}")
    
    return str(output_path_obj)


def create_report(
    title: str,
    sections: Dict[str, Any],
    output_path: str,
    format: str = 'markdown'
) -> str:
    """Create a formatted report file.
    
    Args:
        title: Report title
        sections: Dictionary of section_name: content
        output_path: Path to output file
        format: Output format ('markdown' or 'text')
        
    Returns:
        Path to created report file
    """
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, 'w') as f:
        # Title
        if format == 'markdown':
            f.write(f"# {title}\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        else:
            f.write(f"{title}\n")
            f.write("=" * len(title) + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Sections
        for section_name, content in sections.items():
            if format == 'markdown':
                f.write(f"## {section_name}\n\n")
            else:
                f.write(f"\n{section_name}\n")
                f.write("-" * len(section_name) + "\n")
            
            if isinstance(content, str):
                f.write(content + "\n\n")
            elif isinstance(content, (list, dict)):
                f.write(json.dumps(content, indent=2) + "\n\n")
            else:
                f.write(str(content) + "\n\n")
    
    logger.info(f"Created report: {output_path_obj}")
    return str(output_path_obj)

