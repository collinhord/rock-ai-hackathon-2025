"""
LLM Interface Module

Handles LLM interactions for:
- Structural validation review
- Framework extraction
- Naming consistency suggestions
- Conceptual hierarchy validation
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import time

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("Warning: boto3 not available. AWS Bedrock features will be disabled.")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai not available. OpenAI features will be disabled.")


@dataclass
class LLMResponse:
    """Represents an LLM response."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_estimate: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMInterface:
    """Interface for LLM interactions."""
    
    def __init__(self, provider: str = 'bedrock', model: str = None, region: str = 'us-west-2'):
        """
        Initialize LLM interface.
        
        Args:
            provider: 'bedrock' or 'openai'
            model: Model ID (defaults based on provider)
            region: AWS region (for Bedrock)
        """
        self.provider = provider
        self.region = region
        
        if provider == 'bedrock':
            if not BOTO3_AVAILABLE:
                raise ImportError("boto3 is required for Bedrock. Install with: pip install boto3")
            # Configure with longer timeout for large document processing
            from botocore.config import Config
            config = Config(
                read_timeout=300,  # 5 minutes for large PDF processing
                connect_timeout=10,
                retries={'max_attempts': 2}
            )
            self.client = boto3.client('bedrock-runtime', region_name=region, config=config)
            self.model = model or 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        elif provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai is required for OpenAI. Install with: pip install openai")
            self.client = openai.OpenAI()
            self.model = model or 'gpt-4-turbo-preview'
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def call(self, 
             prompt: str, 
             system_prompt: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: int = 4096) -> LLMResponse:
        """
        Call LLM with prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            
        Returns:
            LLMResponse with content and metadata
        """
        if self.provider == 'bedrock':
            return self._call_bedrock(prompt, system_prompt, temperature, max_tokens)
        elif self.provider == 'openai':
            return self._call_openai(prompt, system_prompt, temperature, max_tokens)
    
    def _call_bedrock(self,
                     prompt: str,
                     system_prompt: Optional[str],
                     temperature: float,
                     max_tokens: int) -> LLMResponse:
        """Call AWS Bedrock (Claude)."""
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        content = response_body['content'][0]['text']
        input_tokens = response_body['usage']['input_tokens']
        output_tokens = response_body['usage']['output_tokens']
        
        # Estimate cost (Claude Sonnet 4.5 pricing as of Oct 2024)
        cost = (input_tokens / 1000 * 0.003) + (output_tokens / 1000 * 0.015)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        
        return LLMResponse(
            content=content,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_estimate=cost
        )
    
    def _call_openai(self,
                    prompt: str,
                    system_prompt: Optional[str],
                    temperature: float,
                    max_tokens: int) -> LLMResponse:
        """Call OpenAI API."""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Estimate cost (GPT-4 Turbo pricing)
        cost = (input_tokens / 1000 * 0.01) + (output_tokens / 1000 * 0.03)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        
        return LLMResponse(
            content=content,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_estimate=cost
        )
    
    def validate_structure(self, taxonomy_summary: str) -> Dict:
        """
        Ask LLM to validate taxonomy structure.
        
        Args:
            taxonomy_summary: Summary of taxonomy structure
            
        Returns:
            Dictionary with validation feedback
        """
        prompt_template = Path(__file__).parent / 'prompts' / 'structural_validation.txt'
        
        if prompt_template.exists():
            with open(prompt_template, 'r') as f:
                prompt = f.read().format(taxonomy_summary=taxonomy_summary)
        else:
            # Fallback prompt
            prompt = f"""
Please analyze the following taxonomy structure and provide feedback on:
1. Logical hierarchy and organization
2. Naming consistency and conventions
3. Completeness and coverage
4. Any structural issues or suggestions for improvement

Taxonomy Summary:
{taxonomy_summary}

Provide your analysis in JSON format with keys: 'issues', 'suggestions', 'strengths'.
"""
        
        response = self.call(
            prompt=prompt,
            system_prompt="You are an expert in educational taxonomy design and structure.",
            temperature=0.3
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # If response isn't valid JSON, wrap it
            return {
                'raw_response': response.content,
                'parse_error': True
            }
    
    def extract_framework(self, framework_text: str) -> Dict:
        """
        Extract structured taxonomy from framework text.
        
        Args:
            framework_text: Text content of framework document
            
        Returns:
            Dictionary with extracted taxonomy structure
        """
        prompt_template = Path(__file__).parent / 'prompts' / 'framework_extraction.txt'
        
        if prompt_template.exists():
            with open(prompt_template, 'r') as f:
                prompt = f.read().format(framework_text=framework_text[:8000])  # Limit size
        else:
            # Fallback prompt
            prompt = f"""
Extract the taxonomy or skill hierarchy from the following educational framework.

Identify:
1. Main categories or strands
2. Subcategories or domains
3. Specific skills or competencies
4. Any hierarchical relationships

Framework Text:
{framework_text[:8000]}

Provide the extracted taxonomy in JSON format.
"""
        
        response = self.call(
            prompt=prompt,
            system_prompt="You are an expert in analyzing educational frameworks and extracting structured taxonomies.",
            temperature=0.2
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                'raw_response': response.content,
                'parse_error': True
            }
    
    def compare_taxonomies(self, 
                          our_taxonomy: str, 
                          framework_taxonomy: str) -> Dict:
        """
        Compare our taxonomy with an external framework.
        
        Args:
            our_taxonomy: Summary of our taxonomy
            framework_taxonomy: Summary of framework taxonomy
            
        Returns:
            Dictionary with comparison results
        """
        prompt_template = Path(__file__).parent / 'prompts' / 'comparison_analysis.txt'
        
        if prompt_template.exists():
            with open(prompt_template, 'r') as f:
                prompt = f.read().format(
                    our_taxonomy=our_taxonomy,
                    framework_taxonomy=framework_taxonomy
                )
        else:
            # Fallback prompt
            prompt = f"""
Compare the following two taxonomies and identify:
1. Concepts present in the framework but missing from our taxonomy
2. Concepts in our taxonomy not addressed by the framework
3. Structural differences
4. Recommendations for alignment or enhancement

Our Taxonomy:
{our_taxonomy}

Framework Taxonomy:
{framework_taxonomy}

Provide your analysis in JSON format.
"""
        
        response = self.call(
            prompt=prompt,
            system_prompt="You are an expert in taxonomy alignment and educational framework analysis.",
            temperature=0.3
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                'raw_response': response.content,
                'parse_error': True
            }
    
    def suggest_naming_improvements(self, names_by_level: Dict[str, List[str]]) -> Dict:
        """
        Suggest naming consistency improvements.
        
        Args:
            names_by_level: Dictionary of level -> list of names
            
        Returns:
            Dictionary with suggestions
        """
        prompt_template = Path(__file__).parent / 'prompts' / 'naming_consistency.txt'
        
        names_summary = json.dumps(names_by_level, indent=2)
        
        if prompt_template.exists():
            with open(prompt_template, 'r') as f:
                prompt = f.read().format(names_summary=names_summary)
        else:
            # Fallback prompt
            prompt = f"""
Review the following taxonomy names for consistency and suggest improvements:

{names_summary}

Provide suggestions for:
1. Inconsistent capitalization patterns
2. Mixed naming conventions
3. Unclear or ambiguous names
4. Opportunities for better parallelism

Provide your suggestions in JSON format.
"""
        
        response = self.call(
            prompt=prompt,
            system_prompt="You are an expert in taxonomy naming conventions and consistency.",
            temperature=0.3
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                'raw_response': response.content,
                'parse_error': True
            }
    
    def extract_taxonomy_adaptive(self, framework_text: str, max_text_length: int = 30000) -> Dict:
        """
        Extract structured taxonomy with adaptive hierarchy detection.
        
        Uses the comprehensive taxonomy_extraction.txt prompt to:
        - Detect natural hierarchy levels
        - Extract concepts with full metadata
        - Identify relationships and progressions
        - Generate subject-specific metadata
        
        Args:
            framework_text: Full text content of framework document
            max_text_length: Maximum characters to send (to control token usage)
            
        Returns:
            Dictionary with complete taxonomy extraction following the format:
            {
                'document_analysis': {...},
                'proposed_hierarchy': {...},
                'extracted_concepts': [...],
                'relationship_graph': {...},
                'grade_progressions': [...],
                'metadata_summary': {...}
            }
        """
        prompt_template = Path(__file__).parent / 'prompts' / 'taxonomy_extraction.txt'
        
        # Truncate text if too long
        truncated_text = framework_text[:max_text_length]
        if len(framework_text) > max_text_length:
            truncated_text += f"\n\n[... document truncated at {max_text_length} characters ...]"
        
        if prompt_template.exists():
            with open(prompt_template, 'r') as f:
                system_prompt = f.read()
        else:
            raise FileNotFoundError("taxonomy_extraction.txt prompt not found")
        
        # User prompt is just the document content
        prompt = f"""Please analyze the following educational framework document:

--- BEGIN DOCUMENT ---
{truncated_text}
--- END DOCUMENT ---

Provide your analysis following the structured JSON format specified in the instructions."""
        
        response = self.call(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,  # Lower temperature for structured extraction
            max_tokens=16000  # Large output for comprehensive analysis
        )
        
        try:
            # Try to parse JSON from response
            content = response.content.strip()
            
            # Sometimes LLMs wrap JSON in markdown code blocks
            if content.startswith('```'):
                # Extract JSON from code block
                lines = content.split('\n')
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith('```'):
                        if in_block:
                            break
                        in_block = True
                        continue
                    if in_block:
                        json_lines.append(line)
                content = '\n'.join(json_lines)
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {
                'raw_response': response.content,
                'parse_error': True,
                'error_message': str(e),
                'note': 'Failed to parse as JSON, returning raw response'
            }
    
    def get_usage_stats(self) -> Dict:
        """Get token usage and cost statistics."""
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'estimated_cost_usd': round(self.total_cost, 4)
        }


# Example usage
if __name__ == '__main__':
    print("=== LLM Interface Demo ===\n")
    
    # Test with a simple example
    try:
        llm = LLMInterface(provider='bedrock')
        
        response = llm.call(
            prompt="What are the key principles of good taxonomy design?",
            system_prompt="You are an expert in educational taxonomy design.",
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"Model: {response.model}")
        print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")
        print(f"Cost: ${response.cost_estimate:.4f}")
        print(f"\nResponse:\n{response.content}")
        
        print(f"\n{llm.get_usage_stats()}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure AWS credentials are configured or use provider='openai'")

