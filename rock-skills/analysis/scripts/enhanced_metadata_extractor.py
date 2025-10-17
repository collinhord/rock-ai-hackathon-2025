#!/usr/bin/env python3
"""
Enhanced ROCK Skills Metadata Extraction Pipeline

Combines three complementary approaches for comprehensive skill metadata:
1. spaCy structural analysis (actions, targets, qualifiers, grammar)
2. LLM educational classification (text_type, cognitive_demand, skill_domain)
3. Rule-based specification extraction (support_level, complexity_band)

Output: 23 metadata fields per skill covering structural, educational, and contextual dimensions

Usage:
    # Test on 10 skills
    python3 enhanced_metadata_extractor.py \\
        --input ../../rock_data/skill_list_filtered_data_set.csv \\
        --output ./test_outputs/enhanced_metadata \\
        --limit 10

    # Full filtered dataset (336 skills)
    python3 enhanced_metadata_extractor.py \\
        --input ../../rock_data/skill_list_filtered_data_set.csv \\
        --output ./outputs/filtered_enhanced_metadata \\
        --checkpoint-interval 50

    # Full ELA corpus
    python3 enhanced_metadata_extractor.py \\
        --input ../../rock_schemas/SKILLS.csv \\
        --content-area "English Language Arts" \\
        --output ./outputs/full_enhanced_metadata \\
        --checkpoint-interval 100
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from botocore.config import Config

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import boto3
    from spacy_processor import SkillProcessor, SkillConcepts, SkillStructure
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("Install with: pip install boto3 spacy")
    print("Then run: python -m spacy download en_core_web_sm")
    DEPENDENCIES_AVAILABLE = False


class EnhancedMetadataExtractor:
    """
    Comprehensive metadata extraction combining:
    - spaCy structural analysis (fast, deterministic)
    - LLM educational classification (nuanced, expensive)
    - Rule-based specification extraction (fast, patterns)
    """
    
    def __init__(self, use_llm: bool = True, use_spacy: bool = True):
        """Initialize the enhanced metadata extractor."""
        self.use_llm = use_llm
        self.use_spacy = use_spacy
        
        # Initialize spaCy processor
        if self.use_spacy:
            print("Initializing spaCy processor...")
            self.spacy_processor = SkillProcessor()
        else:
            self.spacy_processor = None
        
        # Initialize Bedrock client (with increased timeout)
        if self.use_llm:
            print("Initializing AWS Bedrock client...")
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name='us-west-2',
                config=Config(read_timeout=300)
            )
            self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        
        # Define patterns for rule-based extraction
        self.support_patterns = {
            'with_support': ['with support', 'with assistance', 'with help', 'with adult support'],
            'with_prompting': ['with prompting', 'with teacher prompting', 'with guidance', 'with cues'],
            'with_scaffolding': ['with scaffolding', 'using graphic organizers', 'with organizers'],
            'independent': ['independently', 'without support', 'autonomously']
        }
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
        self.spacy_extraction_count = 0
        self.llm_extraction_count = 0
    
    def extract_complexity_band(self, grade_level: str) -> str:
        """Map grade level to complexity band."""
        if pd.isna(grade_level):
            return 'Unknown'
        
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
    
    def build_llm_prompt(self, skill: Dict, concepts: Optional[SkillConcepts], 
                        structure: Optional[SkillStructure]) -> str:
        """
        Build enhanced LLM prompt with spaCy context.
        
        Including structural analysis improves LLM accuracy by providing:
        - Extracted actions and targets
        - Root verb and grammatical structure
        - Domain-specific key concepts
        """
        
        # Build structural context if available
        if concepts and structure:
            structural_context = f"""
STRUCTURAL ANALYSIS (from NLP):
- Primary Action: {structure.root_verb or 'N/A'}
- Actions: {', '.join(concepts.actions[:5]) if concepts.actions else 'N/A'}
- Targets: {', '.join(concepts.targets[:5]) if concepts.targets else 'N/A'}
- Key Concepts: {', '.join(concepts.key_concepts[:5]) if concepts.key_concepts else 'N/A'}
- Complexity Markers: {', '.join(concepts.complexity_markers) if concepts.complexity_markers else 'N/A'}
"""
        else:
            structural_context = ""
        
        prompt = f"""You are an expert in literacy education and pedagogical taxonomy.

TASK: Extract educational metadata for this ROCK skill.

SKILL INFORMATION:
- Name: {skill['SKILL_NAME']}
- Skill Area: {skill.get('SKILL_AREA_NAME', 'Unknown')}
- Grade: {skill.get('GRADE_LEVEL_SHORT_NAME', 'Unknown')}
{structural_context}
EXTRACT METADATA (respond with JSON only):
{{
  "text_type": "fictional|informational|mixed|not_applicable",
  "text_mode": "prose|poetry|drama|mixed|not_applicable",
  "text_genre": "narrative|expository|argumentative|procedural|literary|not_applicable",
  "skill_domain": "reading|writing|speaking|listening|language|not_applicable",
  "task_complexity": "basic|intermediate|advanced",
  "cognitive_demand": "recall|comprehension|application|analysis|synthesis|evaluation",
  "scope": "word|sentence|paragraph|text|multi_text|not_applicable",
  "confidence": "high|medium|low",
  "notes": "brief explanation if needed"
}}

CLASSIFICATION GUIDELINES:

1. text_type:
   - fictional: narrative, literary, imaginative texts (stories, novels, drama)
   - informational: expository, scientific, technical texts (articles, textbooks)
   - mixed: applies to both fiction and non-fiction
   - not_applicable: skill doesn't specify or depend on text type

2. text_mode:
   - prose: standard written text (default for most reading/writing)
   - poetry: poems, verse, rhyme, stanzas
   - drama: plays, scripts, dialogue, theatrical text
   - mixed: applies to multiple modes
   - not_applicable: doesn't involve text modes

3. text_genre:
   - narrative: tells a story (character, plot, setting)
   - expository: explains or informs
   - argumentative: persuades, debates, presents claims
   - procedural: gives instructions, how-to
   - literary: fiction, poetry, creative writing
   - not_applicable: doesn't specify genre

4. skill_domain:
   - reading: comprehension, decoding, fluency, analysis of text
   - writing: composition, mechanics, process, production
   - speaking: oral language, presentation, discussion
   - listening: comprehension, following directions
   - language: grammar, vocabulary, conventions, syntax
   - not_applicable: cross-domain or unclear

5. task_complexity:
   - basic: foundational skills, identification, recognition, simple application
   - intermediate: application, comparison, interpretation, multi-step processes
   - advanced: synthesis, evaluation, creation, critique, complex reasoning

6. cognitive_demand (Bloom's Taxonomy):
   - recall: retrieve facts, definitions, recognize patterns
   - comprehension: understand meaning, explain, summarize, interpret
   - application: use knowledge in new situations, apply rules
   - analysis: break down, identify relationships, compare/contrast
   - synthesis: combine elements, create new, integrate ideas
   - evaluation: judge, critique, assess quality, make decisions

7. scope:
   - word: operates at word level (vocabulary, word recognition)
   - sentence: operates at sentence level (sentence structure, grammar)
   - paragraph: operates at paragraph level (main idea, topic sentences)
   - text: operates on whole text (theme, structure, author's purpose)
   - multi_text: compares or synthesizes multiple texts
   - not_applicable: doesn't specify scope

ANALYSIS HINTS:
- Use structural analysis to inform classification
- If targets include "character", "plot", "story" → likely fictional/narrative
- If targets include "article", "information", "facts" → likely informational
- If actions are "identify", "recognize", "recall" → likely recall/comprehension
- If actions are "analyze", "evaluate", "critique" → likely analysis/evaluation
- If actions are "create", "write", "compose" → likely synthesis
- Consider skill-specific characteristics, not just grade level
- Grade level affects task_complexity but not necessarily cognitive_demand

RESPOND WITH ONLY THE JSON OBJECT (no preamble, no markdown):"""
        
        return prompt
    
    def call_bedrock(self, prompt: str) -> Dict:
        """Call AWS Bedrock API."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 600,
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
        
        self.api_calls += 1
        
        return response_body
    
    def parse_llm_response(self, response_text: str) -> Optional[Dict]:
        """Parse LLM response into structured metadata."""
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Remove 'json' label if present
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            metadata = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                'text_type', 'text_mode', 'text_genre', 'skill_domain',
                'task_complexity', 'cognitive_demand', 'scope', 'confidence'
            ]
            
            for field in required_fields:
                if field not in metadata:
                    print(f"  ⚠ Missing required field: {field}")
                    return None
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parsing error: {e}")
            print(f"  Response text: {response_text[:200]}")
            return None
    
    def extract_with_llm(self, skill: Dict, concepts: Optional[SkillConcepts],
                        structure: Optional[SkillStructure]) -> Dict:
        """Extract educational metadata using LLM with spaCy context."""
        
        if not self.use_llm:
            return self._fallback_educational_metadata()
        
        try:
            prompt = self.build_llm_prompt(skill, concepts, structure)
            response = self.call_bedrock(prompt)
            
            # Parse LLM response
            metadata = self.parse_llm_response(response['content'][0]['text'])
            
            if metadata:
                self.llm_extraction_count += 1
                return {
                    'text_type': metadata.get('text_type', 'not_applicable'),
                    'text_mode': metadata.get('text_mode', 'not_applicable'),
                    'text_genre': metadata.get('text_genre', 'not_applicable'),
                    'skill_domain': metadata.get('skill_domain', 'not_applicable'),
                    'task_complexity': metadata.get('task_complexity', 'basic'),
                    'cognitive_demand': metadata.get('cognitive_demand', 'comprehension'),
                    'scope': metadata.get('scope', 'not_applicable'),
                    'llm_confidence': metadata.get('confidence', 'medium'),
                    'llm_notes': metadata.get('notes', '')
                }
            else:
                print("  ⚠ LLM parsing failed, using fallback")
                return self._fallback_educational_metadata()
                
        except Exception as e:
            print(f"  ✗ LLM error: {e}")
            return self._fallback_educational_metadata()
    
    def _fallback_educational_metadata(self) -> Dict:
        """Provide fallback metadata when LLM is unavailable or fails."""
        return {
            'text_type': 'mixed',
            'text_mode': 'not_applicable',
            'text_genre': 'not_applicable',
            'skill_domain': 'not_applicable',
            'task_complexity': 'intermediate',
            'cognitive_demand': 'comprehension',
            'scope': 'not_applicable',
            'llm_confidence': 'low',
            'llm_notes': 'Fallback values - LLM extraction failed or disabled'
        }
    
    def extract_comprehensive_metadata(self, skill: Dict) -> Dict:
        """
        Extract all metadata for a single skill.
        
        Pipeline:
        1. spaCy structural analysis (always run if enabled)
        2. Rule-based specifications (always run)
        3. LLM educational metadata (if enabled)
        4. Combine and validate results
        
        Returns:
            Dictionary with 23 metadata fields
        """
        
        # Stage 1: Structural analysis (spaCy)
        if self.use_spacy and self.spacy_processor:
            concepts = self.spacy_processor.extract_concepts(skill['SKILL_NAME'])
            structure = self.spacy_processor.extract_structure(skill['SKILL_NAME'])
            self.spacy_extraction_count += 1
        else:
            concepts = None
            structure = None
        
        # Stage 2: Rule-based specifications
        support_level = self.extract_support_level(skill['SKILL_NAME'])
        complexity_band = self.extract_complexity_band(skill.get('GRADE_LEVEL_SHORT_NAME'))
        
        # Stage 3: LLM educational metadata
        educational_metadata = self.extract_with_llm(skill, concepts, structure)
        
        # Stage 4: Combine results
        result = {
            # Core identifiers
            'SKILL_ID': skill['SKILL_ID'],
            'SKILL_NAME': skill['SKILL_NAME'],
            'SKILL_AREA_NAME': skill.get('SKILL_AREA_NAME', ''),
            'GRADE_LEVEL_SHORT_NAME': skill.get('GRADE_LEVEL_SHORT_NAME', ''),
            
            # Specifications (Rules)
            'support_level': support_level,
            'complexity_band': complexity_band,
            
            # Educational metadata (LLM)
            **educational_metadata,
            
            # Quality metrics
            'extraction_method': 'hybrid_spacy_llm' if (self.use_spacy and self.use_llm) else 'partial',
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Add structural components (spaCy) if available
        if concepts and structure:
            result.update({
                'actions': '|'.join(concepts.actions) if concepts.actions else '',
                'targets': '|'.join(concepts.targets) if concepts.targets else '',
                'qualifiers': '|'.join(concepts.qualifiers) if concepts.qualifiers else '',
                'root_verb': structure.root_verb or '',
                'direct_objects': '|'.join(structure.direct_objects) if structure.direct_objects else '',
                'prepositional_phrases': '|'.join(structure.prepositional_phrases) if structure.prepositional_phrases else '',
                'key_concepts': '|'.join(concepts.key_concepts) if concepts.key_concepts else '',
                'complexity_markers': '|'.join(concepts.complexity_markers) if concepts.complexity_markers else ''
            })
        else:
            result.update({
                'actions': '',
                'targets': '',
                'qualifiers': '',
                'root_verb': '',
                'direct_objects': '',
                'prepositional_phrases': '',
                'key_concepts': '',
                'complexity_markers': ''
            })
        
        return result
    
    def get_usage_stats(self) -> Dict:
        """Get token usage and processing statistics."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        # Sonnet 4.5 pricing: $3/M input, $15/M output
        cost = (self.total_input_tokens / 1_000_000 * 3.0) + (self.total_output_tokens / 1_000_000 * 15.0)
        
        return {
            'api_calls': self.api_calls,
            'total_tokens': total_tokens,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'estimated_cost': cost,
            'spacy_extractions': self.spacy_extraction_count,
            'llm_extractions': self.llm_extraction_count
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract comprehensive metadata from ROCK skills using spaCy + LLM hybrid approach"
    )
    
    # Input/output
    parser.add_argument('--input', required=True,
                        help='Path to input CSV (SKILLS.csv or skill_list_filtered_data_set.csv)')
    parser.add_argument('--output-dir', default='./outputs/enhanced_metadata',
                        help='Output directory for results')
    
    # Filtering
    parser.add_argument('--content-area', default=None,
                        help='Filter skills by content area (e.g., "English Language Arts")')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of skills to process (for testing)')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Start index for batch processing')
    
    # Skip existing
    parser.add_argument('--skip-existing',
                        help='Path to existing metadata CSV to skip already processed skills')
    
    # Checkpointing
    parser.add_argument('--checkpoint-interval', type=int, default=50,
                        help='Save checkpoint every N skills')
    
    # Control flags
    parser.add_argument('--no-llm', action='store_true',
                        help='Disable LLM extraction (faster, lower quality)')
    parser.add_argument('--no-spacy', action='store_true',
                        help='Disable spaCy extraction (not recommended)')
    
    args = parser.parse_args()
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not installed")
        return 1
    
    print("=" * 70)
    print("ENHANCED ROCK SKILLS METADATA EXTRACTION PIPELINE")
    print("=" * 70)
    print(f"Hybrid Approach: spaCy + LLM + Rules")
    print(f"Target: 23 comprehensive metadata fields per skill")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\nLoading data...")
    input_path = Path(args.input)
    
    # Determine which columns are available
    sample_df = pd.read_csv(input_path, nrows=1)
    available_columns = sample_df.columns.tolist()
    
    # Build column list based on what's available
    essential_columns = ['SKILL_ID', 'SKILL_NAME']
    optional_columns = ['SKILL_AREA_NAME', 'GRADE_LEVEL_SHORT_NAME', 
                       'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME', 'CONTENT_AREA_SHORT_NAME']
    
    columns_to_load = essential_columns + [col for col in optional_columns if col in available_columns]
    
    skills_df = pd.read_csv(input_path, usecols=columns_to_load)
    print(f"Loaded {len(skills_df):,} skills")
    
    # Filter by content area if specified
    if args.content_area:
        if 'CONTENT_AREA_NAME' in skills_df.columns:
            skills_df = skills_df[skills_df['CONTENT_AREA_NAME'] == args.content_area]
        elif 'CONTENT_AREA_SHORT_NAME' in skills_df.columns:
            skills_df = skills_df[skills_df['CONTENT_AREA_SHORT_NAME'] == args.content_area]
        print(f"Filtered to {len(skills_df)} {args.content_area} skills")
    
    # Skip existing metadata
    if args.skip_existing:
        skip_path = Path(args.skip_existing)
        if skip_path.exists():
            existing_df = pd.read_csv(skip_path)
            existing_ids = set(existing_df['SKILL_ID'])
            skills_df = skills_df[~skills_df['SKILL_ID'].isin(existing_ids)]
            print(f"Skipping {len(existing_ids)} already processed skills")
            print(f"Remaining: {len(skills_df)} skills to process")
    
    # Apply limits
    if args.limit:
        end_index = min(args.start_index + args.limit, len(skills_df))
        skills_df = skills_df.iloc[args.start_index:end_index]
        print(f"Processing batch: skills {args.start_index} to {end_index-1} ({len(skills_df)} total)")
    
    if len(skills_df) == 0:
        print("No skills to process!")
        return 0
    
    # Initialize extractor
    print("\nInitializing Enhanced Metadata Extractor...")
    extractor = EnhancedMetadataExtractor(
        use_llm=not args.no_llm,
        use_spacy=not args.no_spacy
    )
    
    # Process skills
    print(f"\nProcessing {len(skills_df)} skills...")
    print("=" * 70)
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()
    
    for idx, (_, skill) in enumerate(skills_df.iterrows(), 1):
        skill_name_display = skill['SKILL_NAME'][:70] + "..." if len(skill['SKILL_NAME']) > 70 else skill['SKILL_NAME']
        print(f"[{idx}/{len(skills_df)}] Processing: {skill_name_display}")
        
        result = extractor.extract_comprehensive_metadata(skill.to_dict())
        
        if result:
            results.append(result)
            confidence = result.get('llm_confidence', 'unknown')
            print(f"  ✓ Extracted (confidence: {confidence})")
        else:
            print(f"  ✗ Extraction failed")
        
        # Checkpoint
        if idx % args.checkpoint_interval == 0 and results:
            checkpoint_path = output_dir / f"checkpoint_enhanced_metadata_{timestamp}.csv"
            results_df = pd.DataFrame(results)
            results_df.to_csv(checkpoint_path, index=False)
            print(f"\n{'='*70}")
            print(f"CHECKPOINT at {idx} skills")
            print(f"{'='*70}")
            print(f"✓ Checkpoint saved: {checkpoint_path}")
            
            # Print usage stats
            stats = extractor.get_usage_stats()
            print(f"\nProcessing Statistics:")
            print(f"  spaCy extractions: {stats['spacy_extractions']}")
            print(f"  LLM extractions: {stats['llm_extractions']}")
            if stats['api_calls'] > 0:
                print(f"  API Calls: {stats['api_calls']}")
                print(f"  Total Tokens: {stats['total_tokens']:,}")
                print(f"  Estimated Cost: ${stats['estimated_cost']:.2f}")
            print(f"{'='*70}\n")
    
    # Save final results
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("BATCH COMPLETE")
    print("=" * 70)
    print(f"Processed: {len(results)} skills")
    print(f"Time Elapsed: {elapsed_time:.1f}s")
    print(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s" if results else "N/A")
    
    # Save final files
    if results:
        final_path = output_dir / f"skill_metadata_enhanced_{timestamp}.csv"
        results_df = pd.DataFrame(results)
        results_df.to_csv(final_path, index=False)
        print(f"\n✓ Final results saved: {final_path}")
        
        # Generate summary report
        summary_path = output_dir / f"extraction_summary_{timestamp}.txt"
        with open(summary_path, 'w') as f:
            f.write("Enhanced ROCK Skills Metadata Extraction Summary\n")
            f.write("=" * 70 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Skills Processed: {len(results)}\n")
            f.write(f"Time Elapsed: {elapsed_time:.1f}s\n")
            f.write(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s\n\n")
            
            # Confidence distribution
            if 'llm_confidence' in results_df.columns:
                conf_dist = results_df['llm_confidence'].value_counts()
                f.write("LLM Confidence Distribution:\n")
                for conf, count in conf_dist.items():
                    pct = (count / len(results)) * 100
                    f.write(f"  {conf}: {count} ({pct:.1f}%)\n")
                f.write("\n")
            
            # Metadata distributions
            categorical_fields = ['skill_domain', 'text_type', 'text_mode', 'cognitive_demand',
                                'task_complexity', 'support_level', 'complexity_band']
            
            for field in categorical_fields:
                if field in results_df.columns:
                    dist = results_df[field].value_counts()
                    f.write(f"{field.replace('_', ' ').title()} Distribution:\n")
                    for value, count in dist.head(10).items():
                        pct = (count / len(results)) * 100
                        f.write(f"  {value}: {count} ({pct:.1f}%)\n")
                    f.write("\n")
            
            # Structural analysis summary
            if 'actions' in results_df.columns:
                non_empty_actions = results_df[results_df['actions'] != ''].shape[0]
                f.write("Structural Analysis Coverage:\n")
                f.write(f"  Skills with actions extracted: {non_empty_actions} ({non_empty_actions/len(results)*100:.1f}%)\n")
                if 'root_verb' in results_df.columns:
                    non_empty_root = results_df[results_df['root_verb'] != ''].shape[0]
                    f.write(f"  Skills with root verb extracted: {non_empty_root} ({non_empty_root/len(results)*100:.1f}%)\n")
                f.write("\n")
            
            # LLM usage
            stats = extractor.get_usage_stats()
            f.write("Processing Statistics:\n")
            f.write(f"  spaCy extractions: {stats['spacy_extractions']}\n")
            f.write(f"  LLM extractions: {stats['llm_extractions']}\n")
            if stats['api_calls'] > 0:
                f.write(f"  API Calls: {stats['api_calls']}\n")
                f.write(f"  Total Tokens: {stats['total_tokens']:,}\n")
                f.write(f"  Input Tokens: {stats['input_tokens']:,}\n")
                f.write(f"  Output Tokens: {stats['output_tokens']:,}\n")
                f.write(f"  Estimated Cost: ${stats['estimated_cost']:.2f}\n")
        
        print(f"✓ Summary report saved: {summary_path}")
    
    # Final stats
    stats = extractor.get_usage_stats()
    print("\n" + "=" * 70)
    print("PROCESSING STATISTICS")
    print("=" * 70)
    print(f"spaCy extractions: {stats['spacy_extractions']}")
    print(f"LLM extractions: {stats['llm_extractions']}")
    if stats['api_calls'] > 0:
        print(f"API Calls: {stats['api_calls']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Estimated Cost: ${stats['estimated_cost']:.2f}")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("✅ ENHANCED METADATA EXTRACTION COMPLETE!")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

