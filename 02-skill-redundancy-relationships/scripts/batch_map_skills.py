"""
ROCK Skills Batch Mapping Pipeline

Maps ROCK skills to Science of Reading taxonomy using AWS Bedrock (Claude Sonnet 4.5).
Supports filtering by skill IDs, content area, and skipping existing mappings.

Usage:
    python batch_map_skills.py \\
        --skill-ids-file ./temp_priority_skill_ids.txt \\
        --content-area "English Language Arts" \\
        --checkpoint-interval 10 \\
        --output-dir ./outputs/priority_ela_78 \\
        --skip-existing ./llm_skill_mappings.csv
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
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import boto3
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Error: Missing dependencies: {e}")
    print("Install with: pip install boto3 sentence-transformers scikit-learn")
    DEPENDENCIES_AVAILABLE = False


class LLMMapperAssistant:
    """LLM-assisted taxonomy mapping using AWS Bedrock."""
    
    def __init__(self, taxonomy_df: pd.DataFrame, model='all-MiniLM-L6-v2'):
        """Initialize the LLM mapper."""
        self.taxonomy_df = taxonomy_df
        self.model_name = model
        
        # Load sentence transformer
        print(f"Loading embedding model: {model}")
        self.encoder = SentenceTransformer(model)
        
        # Pre-compute taxonomy embeddings
        self.taxonomy_texts = []
        self.taxonomy_paths = []
        
        for _, row in taxonomy_df.iterrows():
            # Build taxonomy path
            path_parts = []
            for level in ['Strand', 'Pillar', 'Domain', 'Skill Area', 'Skill Set', 'Skill Subset']:
                if pd.notna(row.get(level)) and row.get(level):
                    path_parts.append(str(row[level]))
            
            if path_parts:
                taxonomy_path = ' > '.join(path_parts)
                self.taxonomy_paths.append(taxonomy_path)
                
                # Create rich text for embedding
                annotation = row.get('Skill Subset Annotation', '')
                text = f"{taxonomy_path}"
                if pd.notna(annotation) and annotation:
                    text += f". {annotation}"
                self.taxonomy_texts.append(text)
        
        print(f"Computing embeddings for {len(self.taxonomy_texts)} taxonomy nodes...")
        self.taxonomy_embeddings = self.encoder.encode(self.taxonomy_texts, show_progress_bar=True)
        
        # Initialize Bedrock client
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        # Use Claude Sonnet 4.5 (cross-region inference profile)
        self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
    
    def find_semantic_candidates(self, skill_text: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Find top-k semantically similar taxonomy nodes."""
        skill_embedding = self.encoder.encode([skill_text])
        similarities = cosine_similarity(skill_embedding, self.taxonomy_embeddings)[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        candidates = [
            (self.taxonomy_paths[idx], similarities[idx])
            for idx in top_indices
        ]
        
        return candidates
    
    def format_candidates_for_llm(self, candidates: List[Tuple[str, float]]) -> str:
        """Format candidates for LLM prompt."""
        lines = []
        for i, (path, score) in enumerate(candidates, 1):
            lines.append(f"{i}. {path} (similarity: {score:.3f})")
        return '\n'.join(lines)
    
    def map_skill_with_llm(
        self,
        skill_id: str,
        skill_name: str,
        skill_area: Optional[str],
        content_area: Optional[str],
        grade_level: Optional[str],
        top_k: int = 3
    ) -> Dict:
        """Map a single skill using LLM ranking of semantic candidates."""
        
        # Stage 1: Semantic search
        skill_text = f"{skill_name}"
        if skill_area:
            skill_text += f" [{skill_area}]"
        
        candidates = self.find_semantic_candidates(skill_text, top_k=20)
        
        # Stage 2: LLM ranking
        prompt = self.build_llm_prompt(skill_id, skill_name, skill_area, content_area, grade_level, candidates, top_k)
        
        try:
            response = self.call_bedrock(prompt)
            self.api_calls += 1
            
            # Parse LLM response
            mappings = self.parse_llm_response(response['content'][0]['text'])
            
            if mappings:
                best_mapping = mappings[0]
                return {
                    'SKILL_ID': skill_id,
                    'SKILL_NAME': skill_name,
                    'TAXONOMY_PATH': best_mapping['taxonomy_path'],
                    'CONFIDENCE': best_mapping['confidence'],
                    'SEMANTIC_SIMILARITY': candidates[0][1],  # Best semantic match
                    'NEEDS_REVIEW': best_mapping['confidence'] in ['Low', 'Medium'],
                    'ALTERNATIVE_1': mappings[1]['taxonomy_path'] if len(mappings) > 1 else '',
                    'ALTERNATIVE_2': mappings[2]['taxonomy_path'] if len(mappings) > 2 else '',
                    'RATIONALE': best_mapping['rationale']
                }
            else:
                return None
            
        except Exception as e:
            print(f"  ✗ Error mapping skill: {e}")
            return None
    
    def build_llm_prompt(self, skill_id, skill_name, skill_area, content_area, grade_level, candidates, top_k):
        """Build the LLM prompt for skill mapping."""
        
        sor_context = """
SCIENCE OF READING FRAMEWORK CONTEXT:
The Science of Reading taxonomy is organized around five pillars:
1. Phonological Awareness (sounds in spoken language, no print involved)
2. Phonics & Decoding (letter-sound relationships, applying to read words)
3. Fluency (accurate, automatic reading with prosody)
4. Vocabulary (word meanings, relationships, context clues, morphology)
5. Comprehension (understanding, interpreting, analyzing text)

MAPPING PRINCIPLES:
- Match skill scope to appropriate taxonomy granularity
- Distinguish grade-agnostic vs. grade-dependent skills
- Consider prerequisite relationships
- Watch for skills outside literacy scope
"""
        
        prompt = f"""You are an expert in literacy education and the Science of Reading framework.

{sor_context}

Your task: Map the following ROCK skill to the most appropriate Science of Reading taxonomy node(s).

ROCK SKILL:
- Skill ID: {skill_id}
- Skill Name: {skill_name}
- Skill Area: {skill_area or 'N/A'}
- Content Area: {content_area or 'N/A'}
- Grade Level: {grade_level or 'N/A'}

CANDIDATE TAXONOMY NODES (from semantic search):
{self.format_candidates_for_llm(candidates)}

INSTRUCTIONS:
1. Analyze the ROCK skill and identify its core learning objective
2. Select the top {top_k} best matches
3. For each match, provide:
   - Taxonomy path
   - Confidence level (High/Medium/Low)
   - Brief rationale

OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:
1. [Full Taxonomy Path] | Confidence: [High/Medium/Low] | Rationale: [explanation]
2. [Full Taxonomy Path] | Confidence: [High/Medium/Low] | Rationale: [explanation]
...

Start your response IMMEDIATELY with "1. " - no preamble!"""
        
        return prompt
    
    def call_bedrock(self, prompt: str) -> Dict:
        """Call AWS Bedrock API."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
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
    
    def parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse LLM response into structured mappings."""
        mappings = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            
            # Parse format: "1. Path | Confidence: High | Rationale: explanation"
            parts = line.split('|')
            if len(parts) >= 3:
                # Extract taxonomy path (remove number prefix)
                path_part = parts[0].strip()
                path = re.sub(r'^\d+\.\s*', '', path_part).strip()
                
                # Extract confidence
                conf_part = parts[1].strip()
                conf_match = re.search(r'Confidence:\s*(High|Medium|Low)', conf_part, re.IGNORECASE)
                confidence = conf_match.group(1).capitalize() if conf_match else 'Unknown'
                
                # Extract rationale
                rationale = parts[2].strip()
                if rationale.startswith('Rationale:'):
                    rationale = rationale[10:].strip()
                
                mappings.append({
                    'taxonomy_path': path,
                    'confidence': confidence,
                    'rationale': rationale
                })
        
        return mappings
    
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
        description="Batch map ROCK skills to Science of Reading taxonomy using LLM assistance"
    )
    
    # Input/output
    parser.add_argument('--skills-path', default='rock_schemas/SKILLS.csv',
                        help='Path to SKILLS.csv')
    parser.add_argument('--taxonomy-path', default='POC_science_of_reading_literacy_skills_taxonomy.csv',
                        help='Path to Science of Reading taxonomy CSV')
    parser.add_argument('--output-dir', default='./outputs/batch_mapping',
                        help='Output directory for results')
    
    # Filtering
    parser.add_argument('--skill-ids-file',
                        help='Path to text file with one SKILL_ID per line (filters to only these skills)')
    parser.add_argument('--content-area', default='English Language Arts',
                        help='Filter skills by content area')
    parser.add_argument('--start-index', type=int, default=0,
                        help='Start index for batch processing')
    parser.add_argument('--batch-size', type=int,
                        help='Number of skills to process (default: all remaining)')
    
    # Skip existing
    parser.add_argument('--skip-existing',
                        help='Path to existing mappings CSV to skip (e.g., llm_skill_mappings.csv)')
    
    # Checkpointing
    parser.add_argument('--checkpoint-interval', type=int, default=25,
                        help='Save checkpoint every N skills')
    
    args = parser.parse_args()
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not installed")
        return 1
    
    print("=" * 60)
    print("ROCK SKILLS BATCH MAPPING PIPELINE")
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
    
    if not Path(args.taxonomy_path).is_absolute():
        taxonomy_path = project_root / args.taxonomy_path
    else:
        taxonomy_path = Path(args.taxonomy_path)
    
    essential_columns = [
        'SKILL_ID', 'SKILL_NAME', 'SKILL_AREA_NAME',
        'CONTENT_AREA_NAME', 'GRADE_LEVEL_NAME', 'GRADE_LEVEL_SHORT_NAME'
    ]
    skills_df = pd.read_csv(skills_path, usecols=essential_columns)
    taxonomy_df = pd.read_csv(taxonomy_path)
    
    print(f"Loaded {len(skills_df):,} skills")
    print(f"Loaded {len(taxonomy_df):,} taxonomy nodes")
    
    # Filter by skill IDs file if provided
    if args.skill_ids_file:
        skill_ids_file = Path(args.skill_ids_file)
        if not skill_ids_file.is_absolute():
            skill_ids_file = base_dir / skill_ids_file
        
        with open(skill_ids_file, 'r') as f:
            target_skill_ids = set(line.strip() for line in f if line.strip())
        
        print(f"Filtering to {len(target_skill_ids)} specific SKILL_IDs from {args.skill_ids_file}")
        skills_df = skills_df[skills_df['SKILL_ID'].isin(target_skill_ids)]
        print(f"Filtered to {len(skills_df)} skills")
    
    # Filter by content area
    if args.content_area:
        skills_df = skills_df[skills_df['CONTENT_AREA_NAME'] == args.content_area]
        print(f"Filtered to {len(skills_df)} {args.content_area} skills")
    
    # Skip existing mappings
    if args.skip_existing:
        skip_path = Path(args.skip_existing)
        if not skip_path.is_absolute():
            skip_path = base_dir / skip_path
        
        if skip_path.exists():
            existing_df = pd.read_csv(skip_path)
            existing_ids = set(existing_df['SKILL_ID'])
            skills_df = skills_df[~skills_df['SKILL_ID'].isin(existing_ids)]
            print(f"Skipping {len(existing_ids)} already mapped skills")
            print(f"Remaining: {len(skills_df)} skills to map")
    
    # Apply batch limits
    if args.batch_size:
        end_index = min(args.start_index + args.batch_size, len(skills_df))
        skills_df = skills_df.iloc[args.start_index:end_index]
        print(f"Processing batch: skills {args.start_index} to {end_index-1} ({len(skills_df)} total)")
    
    if len(skills_df) == 0:
        print("No skills to process!")
        return 0
    
    # Initialize mapper
    print("\nInitializing LLM mapper...")
    mapper = LLMMapperAssistant(taxonomy_df)
    
    # Process skills
    print(f"\nProcessing {len(skills_df)} skills...")
    print("=" * 60)
    
    results = []
    review_queue = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    start_time = time.time()
    
    for idx, (_, skill) in enumerate(skills_df.iterrows(), 1):
        print(f"[{idx}/{len(skills_df)}] Processing: {skill['SKILL_NAME'][:80]}...")
        
        result = mapper.map_skill_with_llm(
            skill['SKILL_ID'],
            skill['SKILL_NAME'],
            skill['SKILL_AREA_NAME'],
            skill['CONTENT_AREA_NAME'],
            skill['GRADE_LEVEL_NAME']
        )
        
        if result:
            # Add skill metadata
            result['SKILL_AREA_NAME'] = skill['SKILL_AREA_NAME']
            result['CONTENT_AREA_NAME'] = skill['CONTENT_AREA_NAME']
            result['GRADE_LEVEL_NAME'] = skill['GRADE_LEVEL_NAME']
            result['GRADE_LEVEL_SHORT_NAME'] = skill['GRADE_LEVEL_SHORT_NAME']
            
            # Parse taxonomy levels
            path_parts = result['TAXONOMY_PATH'].split(' > ')
            result['strand'] = path_parts[0] if len(path_parts) > 0 else ''
            result['pillar'] = path_parts[1] if len(path_parts) > 1 else ''
            result['domain'] = path_parts[2] if len(path_parts) > 2 else ''
            result['skill_area'] = path_parts[3] if len(path_parts) > 3 else ''
            result['skill_set'] = path_parts[4] if len(path_parts) > 4 else ''
            result['skill_subset'] = path_parts[5] if len(path_parts) > 5 else ''
            
            results.append(result)
            print(f"  ✓ Mapped with confidence: {result['CONFIDENCE']}")
            
            if result['NEEDS_REVIEW']:
                review_queue.append(result)
                print(f"  ⚠ Added to review queue")
        else:
            print(f"  ✗ Mapping failed")
        
        # Checkpoint
        if idx % args.checkpoint_interval == 0 and results:
            checkpoint_path = output_dir / f"checkpoint_{timestamp}.csv"
            results_df = pd.DataFrame(results)
            results_df.to_csv(checkpoint_path, index=False)
            print(f"--- Checkpoint at {idx} skills ---")
            print(f"✓ Checkpoint saved: {checkpoint_path}")
            
            if review_queue:
                review_path = output_dir / f"review_queue_{timestamp}.csv"
                review_df = pd.DataFrame(review_queue)
                review_df.to_csv(review_path, index=False)
                print(f"✓ Review queue saved: {len(review_queue)} items -> {review_path}")
            
            # Print usage stats
            stats = mapper.get_usage_stats()
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
    print(f"Review Queue: {len(review_queue)} skills")
    print(f"Time Elapsed: {elapsed_time:.1f}s")
    print(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s" if results else "N/A")
    
    # Save final files
    if results:
        final_path = output_dir / f"llm_assisted_mappings_{timestamp}.csv"
        results_df = pd.DataFrame(results)
        results_df.to_csv(final_path, index=False)
        print(f"✓ Final results saved: {final_path}")
        
        # Save summary
        summary_path = output_dir / f"mapping_summary_{timestamp}.txt"
        with open(summary_path, 'w') as f:
            f.write("ROCK Skills Batch Mapping Summary\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Skills Processed: {len(results)}\n")
            f.write(f"Time Elapsed: {elapsed_time:.1f}s\n")
            f.write(f"Avg Time per Skill: {elapsed_time/len(results):.1f}s\n\n")
            
            # Confidence distribution
            conf_dist = results_df['CONFIDENCE'].value_counts()
            f.write("Confidence Distribution:\n")
            for conf, count in conf_dist.items():
                pct = (count / len(results)) * 100
                f.write(f"  {conf}: {count} ({pct:.1f}%)\n")
            
            f.write(f"\nReview Queue: {len(review_queue)} skills\n")
            
            stats = mapper.get_usage_stats()
            f.write("\nLLM Usage:\n")
            f.write(f"  API Calls: {stats['api_calls']}\n")
            f.write(f"  Total Tokens: {stats['total_tokens']:,}\n")
            f.write(f"  Estimated Cost: ${stats['estimated_cost']:.2f}\n")
        
        print(f"✓ Summary report saved: {summary_path}")
        
        # Final checkpoint
        checkpoint_path = output_dir / f"checkpoint_{timestamp}.csv"
        results_df.to_csv(checkpoint_path, index=False)
        print(f"✓ Checkpoint saved: {checkpoint_path}")
        
        if review_queue:
            review_path = output_dir / f"review_queue_{timestamp}.csv"
            review_df = pd.DataFrame(review_queue)
            review_df.to_csv(review_path, index=False)
            print(f"✓ Review queue saved: {len(review_queue)} items -> {review_path}")
    
    # Final stats
    stats = mapper.get_usage_stats()
    print("\n" + "=" * 60)
    print("LLM USAGE STATISTICS")
    print("=" * 60)
    print(f"API Calls: {stats['api_calls']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Estimated Cost: ${stats['estimated_cost']:.2f}")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("BATCH MAPPING COMPLETE!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

