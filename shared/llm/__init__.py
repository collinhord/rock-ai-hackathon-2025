"""Shared LLM infrastructure for AWS Bedrock integration.

This module provides a unified interface for interacting with AWS Bedrock
foundation models across all three project domains.
"""

from .bedrock_client import BedrockLanguageModels

__all__ = ['BedrockLanguageModels']

