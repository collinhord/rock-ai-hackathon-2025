"""
Taxonomy Builder Package

A comprehensive toolkit for taxonomy validation, framework analysis,
and LLM-assisted taxonomy improvement.
"""

__version__ = '1.0.0'

from .compatibility import TaxonomyAccess, TaxonomyNode
from .validator import TaxonomyValidator, ValidationReport
from .llm_interface import LLMInterface, LLMResponse
from .framework_analyzer import FrameworkAnalyzer, FrameworkParser

__all__ = [
    'TaxonomyAccess',
    'TaxonomyNode',
    'TaxonomyValidator',
    'ValidationReport',
    'LLMInterface',
    'LLMResponse',
    'FrameworkAnalyzer',
    'FrameworkParser',
]

