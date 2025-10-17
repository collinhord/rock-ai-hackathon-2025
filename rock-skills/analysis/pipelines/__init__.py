"""
Classification pipelines for base skill extraction, specification tagging,
and MECE validation.
"""

from pathlib import Path

PIPELINES_DIR = Path(__file__).parent
SCHEMAS_DIR = PIPELINES_DIR.parent.parent / "schemas"
TAXONOMY_DIR = PIPELINES_DIR.parent.parent / "taxonomy"

