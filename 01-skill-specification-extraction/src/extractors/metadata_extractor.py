#!/usr/bin/env python3
"""
ROCK Skills Metadata Enrichment Pipeline

Extracts pedagogical metadata from ROCK skills using AWS Bedrock (Claude Sonnet 4.5).
Analyzes skill characteristics to identify:
- text_type: fictional | informational | mixed | not_applicable
- text_mode: prose | poetry | mixed | not_applicable
- text_genre: narrative | expository | argumentative | procedural | literary | not_applicable
- skill_domain: reading | writing | speaking | listening | language | not_applicable
- task_complexity: basic | intermediate | advanced
- cognitive_demand: recall | comprehension | application | analysis | synthesis | evaluation

Usage:
    python metadata_extractor.py \\
        --content-area "English Language Arts" \\
        --checkpoint-interval 50 \\
        --output-dir ./outputs/metadata_enrichment \\
        --skip-existing ./outputs/skill_metadata_enriched.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import boto3
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("Install with: pip install boto3")
    DEPENDENCIES_AVAILABLE = False


class MetadataExtractor:
    """LLM-based metadata extraction for ROCK skills."""
    
    def __init__(self):
        """Initialize the metadata extractor."""
        # Initialize Bedrock client
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        # Use Claude Sonnet 4.5 (cross-region inference profile)
        self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
    
    def build_extraction_prompt(self, skill_id: str, skill_name: str, 
                               skill_area: Optional[str], grade_level: Optional[str]) -> str:
        """Build the LLM prompt for metadata extraction."""
        
        prompt = f"""You are an expert in literacy education and pedagogical taxonomy.

Analyze the following ROCK skill and extract pedagogical metadata.

SKILL ID: {skill_id}
SKILL NAME: {skill_name}
SKILL AREA: {skill_area or 'N/A'}
GRADE LEVEL: {grade_level or 'N/A'}

Extract the following metadata (respond ONLY with valid JSON):

{{
  "text_type": "fictional|informational|mixed|not_applicable",
  "text_mode": "prose|poetry|mixed|not_applicable", 
  "text_genre": "narrative|expository|argumentative|procedural|literary|not_applicable",
  "skill_domain": "reading|writing|speaking|listening|language|not_applicable",
  "task_complexity": "basic|intermediate|advanced",
  "cognitive_demand": "recall|comprehension|application|analysis|synthesis|evaluation",
  "confidence": "high|medium|low",
  "notes": "brief explanation if needed"
}}

RULES:
- Use "not_applicable" if the skill doesn't involve that dimension
- Consider skill-specific characteristics, not just grade level
- For text_type: "informational" includes expository, technical, scientific texts; "fictional" includes narratives, stories, literature
- For text_mode: prose is default for non-poetry; use "poetry" only if skill explicitly mentions poetry, poems, or verse
- For text_genre: choose the most specific applicable genre based on skill description
- For skill_domain: identify the primary literacy domain (reading comprehension, writing production, oral language, or language mechanics)
- For task_complexity: basic = foundational/identification, intermediate = application/analysis, advanced = synthesis/evaluation/creation
- For cognitive_demand: use Bloom's taxonomy to classify the primary cognitive skill required

START YOUR RESPONSE IMMEDIATELY WITH THE JSON OBJECT - NO PREAMBLE!"""
        
        return prompt
    
    def call_bedrock(self, prompt: str) -> Dict:
        """Call AWS Bedrock API."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        })
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        
        # Track tokens
        if 'usage' in response_body:
            self.total_input_tokens += response_body['usage'].get('input_tokens', 0)
            self.total_output_tokens += response_body['usage'].get('output_tokens', 0)
        
        return response_body
    
    def parse_llm_response(self, response_text: str) -> Optional[Dict]:
        """Parse LLM response into structured metadata."""
        try:
            # Try to find JSON in the response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Parse JSON
            metadata = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['text_type', 'text_mode', 'text_genre', 'skill_domain', 
                             'task_complexity', 'cognitive_demand', 'confidence']
            
            for field in required_fields:
                if field not in metadata:
                    print(f"  ⚠ Missing required field: {field}")
                    return None
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parsing error: {e}")
            print(f"  Response text: {response_text[:200]}")
            return None
    
    def extract_metadata(self, skill_id: str, skill_name: str,
                        skill_area: Optional[str], grade_level: Optional[str]) -> Optional[Dict]:
        """Extract metadata for a single skill using LLM."""
        
        prompt = self.build_extraction_prompt(skill_id, skill_name, skill_area, grade_level)
        
        try:
            response = self.call_bedrock(prompt)
            self.api_calls += 1
            
            # Parse LLM response
            metadata = self.parse_llm_response(response['content'][0]['text'])
            
            if metadata:
                return {
                    'SKILL_ID': skill_id,
                    'SKILL_NAME': skill_name,
                    'text_type': metadata.get('text_type', 'not_applicable'),
                    'text_mode': metadata.get('text_mode', 'not_applicable'),
                    'text_genre': metadata.get('text_genre', 'not_applicable'),
                    'skill_domain': metadata.get('skill_domain', 'not_applicable'),
                    'task_complexity': metadata.get('task_complexity', 'basic'),
                    'cognitive_demand': metadata.get('cognitive_demand', 'comprehension'),
                    'extraction_confidence': metadata.get('confidence', 'medium'),
                    'extraction_notes': metadata.get('notes', ''),
                    'extracted_timestamp': datetime.now().isoformat()
                }
            else:
                return None
            
        except Exception as e:
            print(f"  ✗ Error extracting metadata: {e}")
            return None
    
    def get_usage_stats(self) -> Dict:
        """Get token usage statistics."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        # Sonnet 4.5 pricing: $3/M input, $15/M output
        cost = (self.total_input_tokens / 1_000_000 * 3.0) + (self.total_output_tokens / 1_000_000 * 15.0)
        
        return {
            'api_calls': self.api_calls,
            'total_tokens': total_tokens,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'estimated_cost': cost
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract pedagogical metadata from ROCK skills using LLM assistance"
    )
    
    # Input/output
    parser.add_argument('--skills-path', default='rock_schemas/SKILLS.csv',
                        help='Path to SKILLS.csv')
    parser.add_argument('--output-dir', default='./outputs/metadata_enrichment',
                        help='Output directory for results')
    
    # Filtering
    parser.add_argument('--content-area', default='English Language Arts',
                        help='Filter skills by content area')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Start index for batch processing')
    parser.add_argument('--batch-size', type=int,
                        help='Number of skills to process (default: all remaining)')
    
    # Skip existing
    parser.add_argument('--skip-existing',
                        help='Path to existing metadata CSV to skip (e.g., outputs/skill_metadata_enriched.csv)')
    
    # Checkpointing
    parser.add_argument('--checkpoint-interval', type=int, default=50,
                        help='Save checkpoint every N skills')
    
    args = parser.parse_args()
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not installed")
        return 1
    
    print("=" * 60)
    print("ROCK SKILLS METADATA ENRICHMENT PIPELINE")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("Loading data...")
    # Resolve paths relative to the analysis directory (parent of scripts/)
    scripts_dir = Path(__file__).parent  # scripts/
    base_dir = scripts_dir.parent  # analysis/
    project_root = base_dir.parent  # rock-skills/
    
    # Handle relative paths
    if not Path(args.skills_path).is_absolute():
        skills_path = project_root / args.skills_path
    else:
        skills_path = Path(args.skills_path)
    
    essential_columns = [
        'SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME'
    ]
    skills_df = pd.read_csv(skills_path, usecols=essential_columns)
    
    print(f"Loaded {len(skills_df):,} skills")
    
    # Filter by content area
    if args.content_area:
        skills_df = skills_df[skills_df['CONTENT_AREA_NAME'] == args.content_area]
        print(f"Filtered to {len(skills_df)} {args.content_area} skills")
    
    # Skip existing metadata
    if args.skip_existing:
        skip_path = Path(args.skip_existing)
        if not skip_path.is_absolute():
            skip_path = base_dir / skip_path
        
        if skip_path.exists():
            existing_df = pd.read_csv(skip_path)
            existing_ids = set(existing_df['SKILL_ID'])
            skills_df = skills_df[~skills_df['SKILL_ID'].isin(existing_ids)]
            print(f"Skipping {len(existing_ids)} already processed skills")
            print(f"Remaining: {len(skills_df)} skills to process")
    
    # Apply batch limits
    if args.batch_size:
        end_index = min(args.start_index + args.batch_size, len(skills_df))
        skills_df = skills_df.iloc[args.start_index:end_index]
        print(f"Processing batch: skills {args.start_index} to {end_index-1} ({len(skills_df)} total)")
    
    if len(skills_df) == 0:
        print("No skills to process!")
        return 0
    
    # Initialize extractor
    print("\nInitializing metadata extractor...")
    extractor = MetadataExtractor()
    
    # Process skills
    print(f"\nProcessing {len(skills_df)} skills...")
    print("=" * 60)
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    start_time = time.time()
    
    for idx, (_, skill) in enumerate(skills_df.iterrows(), 1):
        print(f"[{idx}/{len(skills_df)}] Processing: {skill['SKILL_NAME'][:80]}...")
        
        result = extractor.extract_metadata(
            skill['SKILL_ID'],
            skill['SKILL_NAME'],
            skill['SKILL_AREA_NAME'],
            skill['GRADE_LEVEL_NAME']
        )
        
        if result:
            results.append(result)
            print(f"  ✓ Extracted with confidence: {result['extraction_confidence']}")
        else:
            print(f"  ✗ Extraction failed")
        
        # Checkpoint
        if idx % args.checkpoint_interval == 0 and results:
            checkpoint_path = output_dir / f"checkpoint_metadata_{timestamp}.csv"
            results_df = pd.DataFrame(results)
            results_df.to_csv(checkpoint_path, index=False)
            print(f"--- Checkpoint at {idx} skills ---")
            print(f"✓ Checkpoint saved: {checkpoint_path}")
            
            # Print usage stats
            stats = extractor.get_usage_stats()
            print("=" * 60)
            print("LLM USAGE STATISTICS")
            print("=" * 60)
            print(f"API Calls: {stats['api_calls']}")
            print(f"Total Tokens: {stats['total_tokens']:,}")
            print(f"Estimated Cost: ${stats['estimated_cost']:.2f}")
            print("=" * 60)
    
    # Save final results
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("BATCH COMPLETE")
    print("=" * 60)
    print(f"Processed: {len(results)} skills")
    print(f"Successful: {len(results)}")
    print(f"Errors: {len(skills_df) - len(results)}")
    print(f"Time Elapsed: {elapsed_time:.1f}s")
    print(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s" if results else "N/A")
    
    # Save final files
    if results:
        final_path = output_dir / f"skill_metadata_enriched_{timestamp}.csv"
        results_df = pd.DataFrame(results)
        results_df.to_csv(final_path, index=False)
        print(f"✓ Final results saved: {final_path}")
        
        # Save summary
        summary_path = output_dir / f"metadata_summary_{timestamp}.txt"
        with open(summary_path, 'w') as f:
            f.write("ROCK Skills Metadata Enrichment Summary\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Skills Processed: {len(results)}\n")
            f.write(f"Time Elapsed: {elapsed_time:.1f}s\n")
            f.write(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s\n\n")
            
            # Confidence distribution
            conf_dist = results_df['extraction_confidence'].value_counts()
            f.write("Confidence Distribution:\n")
            for conf, count in conf_dist.items():
                pct = (count / len(results)) * 100
                f.write(f"  {conf}: {count} ({pct:.1f}%)\n")
            
            # Domain distribution
            domain_dist = results_df['skill_domain'].value_counts()
            f.write("\nSkill Domain Distribution:\n")
            for domain, count in domain_dist.items():
                pct = (count / len(results)) * 100
                f.write(f"  {domain}: {count} ({pct:.1f}%)\n")
            
            # Text type distribution
            text_type_dist = results_df['text_type'].value_counts()
            f.write("\nText Type Distribution:\n")
            for text_type, count in text_type_dist.items():
                pct = (count / len(results)) * 100
                f.write(f"  {text_type}: {count} ({pct:.1f}%)\n")
            
            stats = extractor.get_usage_stats()
            f.write("\nLLM Usage:\n")
            f.write(f"  API Calls: {stats['api_calls']}\n")
            f.write(f"  Total Tokens: {stats['total_tokens']:,}\n")
            f.write(f"  Estimated Cost: ${stats['estimated_cost']:.2f}\n")
        
        print(f"✓ Summary report saved: {summary_path}")
    
    # Final stats
    stats = extractor.get_usage_stats()
    print("\n" + "=" * 60)
    print("LLM USAGE STATISTICS")
    print("=" * 60)
    print(f"API Calls: {stats['api_calls']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Estimated Cost: ${stats['estimated_cost']:.2f}")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("METADATA ENRICHMENT COMPLETE!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

