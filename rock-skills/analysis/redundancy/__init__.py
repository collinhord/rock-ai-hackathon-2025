"""
Skill Redundancy and Relationship Validation System

A comprehensive system for detecting, classifying, and managing skill redundancies
in educational taxonomies using multi-dimensional similarity analysis.

Components:
- similarity_engine: Multi-dimensional similarity calculation
- relationship_classifier: Rule-based and LLM-powered relationship classification
- recommendation_engine: Actionable recommendations and prioritization
- llm_reviewer: LLM integration for ambiguous cases

Usage:
    from analysis.redundancy import RedundancyAnalyzer
    
    analyzer = RedundancyAnalyzer(config_path='config.yaml')
    relationships = analyzer.analyze_skills(metadata_df)
    recommendations = analyzer.generate_recommendations(relationships)
"""

__version__ = "1.0.0"
__author__ = "ROCK AI Hackathon Team"

from pathlib import Path

# Module-level constants
MODULE_DIR = Path(__file__).parent
CONFIG_PATH = MODULE_DIR / "config.yaml"
OUTPUTS_DIR = MODULE_DIR / "outputs"

# Relationship types
RELATIONSHIP_TYPES = [
    "TRUE_DUPLICATE",
    "SPECIFICATION_VARIANT",
    "PREREQUISITE",
    "PROGRESSION",
    "COMPLEMENTARY",
    "AMBIGUOUS",
    "DISTINCT"
]

# Priority levels
PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]

__all__ = [
    "RELATIONSHIP_TYPES",
    "PRIORITY_LEVELS",
    "MODULE_DIR",
    "CONFIG_PATH",
    "OUTPUTS_DIR"
]

