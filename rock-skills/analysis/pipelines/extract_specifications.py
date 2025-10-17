#!/usr/bin/env python3
"""
Specification Extraction Pipeline

Classifies ROCK skills by specifications using:
1. Rule-based extraction (fast, deterministic)
2. LLM classification (nuanced, semantic)

Specifications extracted:
- text_type: fictional | informational | mixed
- text_mode: prose | poetry | drama
- complexity_band: K-2 | 3-5 | 6-8 | 9-12
- support_level: with_support | with_prompting | independent | autonomous
- cognitive_demand: recall | comprehension | application | analysis | synthesis | evaluation
- skill_domain: reading | writing | speaking | listening | language

Usage:
    python3 extract_specifications.py --input mappings.csv --output specifications/
"""

import sys
import json
import pandas as pd
import spacy
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not available. LLM extraction disabled.")


class SpecificationExtractor:
    """Extract specifications from ROCK skills using rules + LLM."""
    
    def __init__(self, use_llm: bool = True):
        """Initialize the extractor."""
        self.use_llm = use_llm and BEDROCK_AVAILABLE
        
        # Load spaCy
        try:
            self.nlp = spacy.load("en_core_web_lg")
            print("✓ Loaded spaCy model")
        except OSError:
            print("⚠ spaCy model not found")
            self.nlp = None
        
        # Initialize Bedrock
        if self.use_llm:
            try:
                self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
                print("✓ Initialized AWS Bedrock client")
            except Exception as e:
                print(f"⚠ Could not initialize Bedrock: {e}")
                self.use_llm = False
        
        # Define patterns for rule-based extraction
        self.support_patterns = {
            'with_support': ['with support', 'with assistance', 'with help'],
            'with_prompting': ['with prompting', 'with teacher prompting', 'with guidance'],
            'independent': ['independently', 'without support', 'autonomously'],
            'with_scaffolding': ['with scaffolding', 'using graphic organizers']
        }
        
        self.text_mode_patterns = {
            'poetry': ['poem', 'poetry', 'verse', 'rhyme', 'stanza'],
            'drama': ['play', 'drama', 'script', 'dialogue', 'scene', 'act'],
            'prose': []  # Default
        }
    
    def extract_complexity_band(self, grade_level: str) -> str:
        """Map grade level to complexity band."""
        grade_map = {
            'Pre-K': 'K-2', 'PK': 'K-2', 'K': 'K-2', 'Kindergarten': 'K-2',
            '1': 'K-2', '2': 'K-2',
            '3': '3-5', '4': '3-5', '5': '3-5',
            '6': '6-8', '7': '6-8', '8': '6-8',
            '9': '9-12', '10': '9-12', '11': '9-12', '12': '9-12'
        }
        
        grade_str = str(grade_level).strip()
        return grade_map.get(grade_str, 'Unknown')
    
    def extract_support_level(self, skill_name: str) -> str:
        """Extract support level using pattern matching."""
        skill_lower = skill_name.lower()
        
        for level, patterns in self.support_patterns.items():
            if any(pattern in skill_lower for pattern in patterns):
                return level
        
        return 'independent'  # Default
    
    def extract_text_mode(self, skill_name: str) -> str:
        """Extract text mode using pattern matching."""
        skill_lower = skill_name.lower()
        
        for mode, patterns in self.text_mode_patterns.items():
            if any(pattern in skill_lower for pattern in patterns):
                return mode
        
        return 'prose'  # Default
    
    def extract_with_llm(self, skill: Dict) -> Dict:
        """
        Use LLM to extract nuanced specifications.
        
        Args:
            skill: Dictionary with skill information
            
        Returns:
            Dictionary with extracted specifications
        """
        if not self.use_llm:
            return {
                'text_type': 'mixed',
                'cognitive_demand': 'comprehension',
                'text_genre': 'not_applicable',
                'scope': 'not_applicable',
                'confidence': 'low',
                'method': 'fallback'
            }
        
        prompt = f"""You are an expert in literacy taxonomy and the Science of Reading.

TASK: Classify the following ROCK skill by specifications.

ROCK SKILL:
- Name: {skill.get('SKILL_NAME', '')}
- Skill Area: {skill.get('SKILL_AREA_NAME', '')}
- Grade: {skill.get('GRADE_LEVEL_NAME', '')}

BASE SKILL: {skill.get('base_skill_name', 'Unknown')}

EXTRACT SPECIFICATIONS:

1. text_type [REQUIRED]: 
   - fictional: narrative, literary, imaginative texts (stories, novels, drama)
   - informational: expository, scientific, technical texts (articles, textbooks)
   - mixed: applies to both fiction and non-fiction
   - not_applicable: skill doesn't specify text type
   
   Choose based on skill description semantics, NOT just keywords.

2. cognitive_demand [REQUIRED - Bloom's Taxonomy]:
   - recall: retrieve facts, definitions, basic information
   - comprehension: understand meaning, interpret, explain
   - application: use knowledge in new situations
   - analysis: break down information, identify relationships
   - synthesis: combine elements to form new whole
   - evaluation: judge value, critique, make decisions

3. text_genre [OPTIONAL]:
   - narrative: tells a story
   - expository: explains or informs
   - argumentative: persuades or debates
   - procedural: gives instructions
   - literary: fiction, poetry, drama
   - not_applicable: doesn't specify

4. scope [OPTIONAL]:
   - word: operates at word level
   - sentence: operates at sentence level
   - paragraph: operates at paragraph level
   - text: operates on whole text
   - multi_text: compares multiple texts
   - not_applicable: doesn't specify

RESPOND ONLY WITH JSON:
{{
    "text_type": "fictional|informational|mixed|not_applicable",
    "cognitive_demand": "recall|comprehension|application|analysis|synthesis|evaluation",
    "text_genre": "narrative|expository|argumentative|procedural|literary|not_applicable",
    "scope": "word|sentence|paragraph|text|multi_text|not_applicable",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation"
}}

Start your response IMMEDIATELY with "{{" - no preamble!"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-sonnet-4-5-v2:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "temperature": 0.3,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                })
            )
            
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['method'] = 'llm'
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"⚠ LLM extraction failed: {e}")
            return {
                'text_type': 'mixed',
                'cognitive_demand': 'comprehension',
                'text_genre': 'not_applicable',
                'scope': 'not_applicable',
                'confidence': 'low',
                'method': 'error',
                'error': str(e)
            }
    
    def extract_specifications(self, skills_df: pd.DataFrame) -> pd.DataFrame:
        """
        Main extraction pipeline.
        
        Args:
            skills_df: DataFrame with ROCK skills and base skill mappings
            
        Returns:
            DataFrame with specifications added
        """
        print("\n=== SPECIFICATION EXTRACTION PIPELINE ===\n")
        
        # Stage 1: Rule-based extraction
        print("Stage 1: Rule-based extraction...")
        
        skills_df['complexity_band'] = skills_df['GRADE_LEVEL_NAME'].apply(
            self.extract_complexity_band
        )
        
        skills_df['support_level'] = skills_df['SKILL_NAME'].apply(
            self.extract_support_level
        )
        
        skills_df['text_mode'] = skills_df['SKILL_NAME'].apply(
            self.extract_text_mode
        )
        
        # Infer skill_domain from SKILL_AREA_NAME
        skills_df['skill_domain'] = skills_df['SKILL_AREA_NAME'].apply(
            lambda x: 'reading' if 'reading' in str(x).lower() or 'comprehension' in str(x).lower()
            else 'writing' if 'writing' in str(x).lower()
            else 'language' if 'language' in str(x).lower() or 'vocabulary' in str(x).lower()
            else 'speaking' if 'speaking' in str(x).lower()
            else 'listening' if 'listening' in str(x).lower()
            else 'reading'  # Default
        )
        
        print(f"✓ Extracted rule-based specifications for {len(skills_df)} skills")
        
        # Stage 2: LLM extraction (if enabled)
        if self.use_llm:
            print("\nStage 2: LLM extraction...")
            print("Processing skills...")
            
            llm_results = []
            for idx, row in skills_df.iterrows():
                if idx > 0 and idx % 50 == 0:
                    print(f"  Processed {idx}/{len(skills_df)} skills...")
                
                llm_specs = self.extract_with_llm(row.to_dict())
                llm_results.append(llm_specs)
            
            # Add LLM results to DataFrame
            skills_df['text_type'] = [r.get('text_type', 'mixed') for r in llm_results]
            skills_df['cognitive_demand'] = [r.get('cognitive_demand', 'comprehension') for r in llm_results]
            skills_df['text_genre'] = [r.get('text_genre', 'not_applicable') for r in llm_results]
            skills_df['scope'] = [r.get('scope', 'not_applicable') for r in llm_results]
            skills_df['spec_confidence'] = [r.get('confidence', 'medium') for r in llm_results]
            skills_df['spec_method'] = [r.get('method', 'unknown') for r in llm_results]
            
            print(f"✓ Extracted LLM specifications for {len(skills_df)} skills")
        else:
            # Fallback values
            skills_df['text_type'] = 'mixed'
            skills_df['cognitive_demand'] = 'comprehension'
            skills_df['text_genre'] = 'not_applicable'
            skills_df['scope'] = 'not_applicable'
            skills_df['spec_confidence'] = 'low'
            skills_df['spec_method'] = 'fallback'
        
        print(f"\n✓ Total specifications extracted: {len(skills_df)}")
        
        return skills_df


def main():
    parser = argparse.ArgumentParser(description='Extract specifications from ROCK skills')
    parser.add_argument('--input', required=True,
                       help='CSV file with ROCK skill mappings')
    parser.add_argument('--output', default='../../taxonomy/specifications',
                       help='Output directory for specifications')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of skills (for testing)')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM extraction')
    parser.add_argument('--new-only', action='store_true',
                       help='Extract specifications only for new mappings')
    
    args = parser.parse_args()
    
    # Load mappings
    print(f"Loading mappings from {args.input}...")
    mappings_df = pd.read_csv(args.input)
    
    # New-only mode: filter to mappings without existing specifications
    if args.new_only:
        specs_file = Path(args.output) / "all_specifications.csv"
        if specs_file.exists():
            print("🔄 New-only mode: Loading existing specifications...")
            existing_specs = pd.read_csv(specs_file)
            existing_skill_ids = set(existing_specs['SKILL_ID'].values)
            
            original_count = len(mappings_df)
            mappings_df = mappings_df[~mappings_df['SKILL_ID'].isin(existing_skill_ids)]
            print(f"   Filtered to {len(mappings_df)} new mappings (out of {original_count} total)")
            
            if len(mappings_df) == 0:
                print("✓ No new mappings to process")
                return
        else:
            print("   ℹ️  No existing specifications found, processing all")
    
    if args.limit:
        mappings_df = mappings_df.head(args.limit)
        print(f"Limited to {args.limit} skills for testing")
    
    print(f"Loaded {len(mappings_df)} ROCK skills")
    
    # Initialize extractor
    extractor = SpecificationExtractor(use_llm=not args.no_llm)
    
    # Extract specifications
    specs_df = extractor.extract_specifications(mappings_df)
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "rock_skills_with_specs.csv"
    specs_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Saved specifications to {output_file}")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total skills: {len(specs_df)}")
    print(f"\nComplexity bands:")
    print(specs_df['complexity_band'].value_counts())
    print(f"\nSupport levels:")
    print(specs_df['support_level'].value_counts())
    print(f"\nText types:")
    print(specs_df['text_type'].value_counts())
    print(f"\nCognitive demand:")
    print(specs_df['cognitive_demand'].value_counts())


if __name__ == '__main__':
    main()

