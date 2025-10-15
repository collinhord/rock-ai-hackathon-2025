#!/usr/bin/env python3
"""
LLM-Assisted Taxonomy Mapping Tool

Uses AWS Bedrock (Claude Sonnet 4.5) to accelerate ROCK skill-to-taxonomy mapping.
Hybrid approach: Embedding-based retrieval + LLM reasoning for ranking.

Configuration matches textbook-schema-generator pattern for consistency.
"""

import pandas as pd
import numpy as np
import json
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')


class LLMMapperAssistant:
    """
    LLM-assisted mapper for ROCK skills to Science of Reading taxonomy.
    
    Two-stage approach:
    1. Embedding-based semantic search (narrow to top 20 candidates)
    2. LLM reasoning and ranking (pick top 5 with confidence)
    """
    
    def __init__(
        self,
        taxonomy_df: pd.DataFrame,
        model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        region_name: str = "us-east-1"
    ):
        """
        Initialize LLM mapping assistant.
        
        Args:
            taxonomy_df: DataFrame with Science of Reading taxonomy
            model_id: Bedrock model ID
            region_name: AWS region
        """
        self.taxonomy_df = taxonomy_df
        self.model_id = model_id
        self.region_name = region_name
        
        # Initialize Bedrock client (matches textbook-schema-generator pattern)
        config = boto3.session.Config(
            read_timeout=600,
            connect_timeout=60,
            retries={'max_attempts': 3}
        )
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=region_name,
            config=config
        )
        
        # Initialize sentence transformer for embedding-based search
        print("Loading sentence transformer model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pre-compute taxonomy embeddings for efficiency
        print("Pre-computing taxonomy embeddings...")
        self._compute_taxonomy_embeddings()
        
        # Track API usage for cost monitoring
        self.api_calls = 0
        self.total_tokens = 0
        
        print("✓ LLM Mapper Assistant initialized")
    
    def _compute_taxonomy_embeddings(self):
        """
        Pre-compute embeddings for all taxonomy entries.
        This allows fast semantic search without recomputing each time.
        """
        # Combine relevant taxonomy fields into searchable text
        self.taxonomy_df['SEARCH_TEXT'] = (
            self.taxonomy_df['Strand'].fillna('') + ' | ' +
            self.taxonomy_df['Pillar'].fillna('') + ' | ' +
            self.taxonomy_df['Domain'].fillna('') + ' | ' +
            self.taxonomy_df['Skill Area'].fillna('') + ' | ' +
            self.taxonomy_df['Skill Set'].fillna('') + ' | ' +
            self.taxonomy_df['Skill Subset'].fillna('') + ' | ' +
            self.taxonomy_df['Skill Subset Annotation'].fillna('')
        )
        
        # Compute embeddings
        search_texts = self.taxonomy_df['SEARCH_TEXT'].tolist()
        self.taxonomy_embeddings = self.embedder.encode(
            search_texts,
            show_progress_bar=True,
            batch_size=32
        )
        
        print(f"✓ Computed embeddings for {len(self.taxonomy_df)} taxonomy entries")
    
    def semantic_search(
        self,
        skill_name: str,
        skill_area: str = None,
        content_area: str = None,
        top_k: int = 20
    ) -> List[Dict]:
        """
        Stage 1: Embedding-based semantic search.
        
        Args:
            skill_name: ROCK skill name
            skill_area: Optional skill area for filtering
            content_area: Optional content area for filtering
            top_k: Number of candidates to return
            
        Returns:
            List of top-k taxonomy candidates with similarity scores
        """
        # Create query text
        query_parts = [skill_name]
        if skill_area:
            query_parts.append(skill_area)
        if content_area:
            query_parts.append(content_area)
        query_text = ' | '.join(query_parts)
        
        # Compute query embedding
        query_embedding = self.embedder.encode([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.taxonomy_embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build candidate list
        candidates = []
        for idx in top_indices:
            row = self.taxonomy_df.iloc[idx]
            candidates.append({
                'index': int(idx),
                'similarity_score': float(similarities[idx]),
                'strand': row['Strand'],
                'pillar': row['Pillar'],
                'domain': row['Domain'],
                'skill_area': row['Skill Area'],
                'skill_set': row['Skill Set'],
                'skill_subset': row['Skill Subset'],
                'annotation': row['Skill Subset Annotation']
            })
        
        return candidates
    
    def format_candidates_for_llm(self, candidates: List[Dict]) -> str:
        """
        Format candidates into readable text for LLM prompt.
        """
        formatted = []
        for i, candidate in enumerate(candidates, 1):
            entry = f"""
Candidate {i} (Similarity: {candidate['similarity_score']:.3f}):
  Strand: {candidate['strand']}
  Pillar: {candidate['pillar']}
  Domain: {candidate['domain']}
  Skill Area: {candidate['skill_area']}
  Skill Set: {candidate['skill_set']}
  Skill Subset: {candidate['skill_subset']}
  Description: {candidate['annotation'][:200]}...
"""
            formatted.append(entry.strip())
        
        return '\n\n'.join(formatted)
    
    def call_bedrock_llm(self, prompt: str, max_tokens: int = 4000) -> Tuple[str, int]:
        """
        Call AWS Bedrock with Claude (matches textbook-schema-generator pattern).
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            
        Returns:
            Tuple of (response_text, token_count)
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Track usage
            self.api_calls += 1
            # Estimate tokens (actual token count would require tokenizer)
            estimated_tokens = len(prompt.split()) + len(response_text.split())
            self.total_tokens += estimated_tokens
            
            return response_text, estimated_tokens
            
        except ClientError as e:
            raise Exception(f"AWS Bedrock error: {e}")
    
    def parse_llm_response(self, response_text: str) -> List[Dict]:
        """
        Parse LLM response into structured suggestions.
        
        Expected format:
        1. Taxonomy Path | Confidence: High | Rationale: ...
        2. Taxonomy Path | Confidence: Medium | Rationale: ...
        ...
        """
        suggestions = []
        
        lines = response_text.strip().split('\n')
        
        current_suggestion = {}
        for line in lines:
            line = line.strip()
            
            # Look for numbered entries
            if line and (line[0].isdigit() or line.startswith('-')):
                # Save previous suggestion if exists
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    current_suggestion = {}
                
                # Parse new suggestion
                # Remove leading number/dash
                content = line.lstrip('0123456789.-) ').strip()
                
                # Try to extract confidence
                confidence = "Medium"  # default
                if "confidence:" in content.lower():
                    if "high" in content.lower():
                        confidence = "High"
                    elif "low" in content.lower():
                        confidence = "Low"
                
                # Try to extract taxonomy path and rationale
                if '|' in content:
                    parts = content.split('|')
                    taxonomy_path = parts[0].strip()
                    
                    # Extract rationale
                    rationale = ""
                    for part in parts[1:]:
                        if "rationale" in part.lower():
                            rationale = part.split(':', 1)[-1].strip()
                            break
                    
                    current_suggestion = {
                        'taxonomy_path': taxonomy_path,
                        'confidence': confidence,
                        'rationale': rationale if rationale else content
                    }
                else:
                    # Fallback: treat whole line as taxonomy path
                    current_suggestion = {
                        'taxonomy_path': content,
                        'confidence': confidence,
                        'rationale': content
                    }
        
        # Add last suggestion
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions
    
    def suggest_mappings(
        self,
        skill_id: str,
        skill_name: str,
        skill_area: str = None,
        content_area: str = None,
        grade_level: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Main function: Suggest taxonomy mappings for a ROCK skill.
        
        Two-stage process:
        1. Semantic search (narrow to 20 candidates)
        2. LLM ranking (pick top 5 with reasoning)
        
        Args:
            skill_id: ROCK SKILL_ID
            skill_name: ROCK skill name
            skill_area: Optional ROCK skill area
            content_area: Optional content area
            grade_level: Optional grade level
            top_k: Number of suggestions to return
            
        Returns:
            List of top-k mapping suggestions with confidence and rationale
        """
        print(f"\nMapping: {skill_name}")
        
        # Stage 1: Semantic search
        print("  Stage 1: Semantic search...")
        candidates = self.semantic_search(skill_name, skill_area, content_area, top_k=20)
        print(f"  Found {len(candidates)} candidates")
        
        # Stage 2: LLM ranking
        print("  Stage 2: LLM ranking...")
        
        sor_context = """
SCIENCE OF READING FRAMEWORK CONTEXT:
The Science of Reading taxonomy is organized around five pillars:
1. Phonological Awareness (sounds in spoken language, no print involved)
2. Phonics & Decoding (letter-sound relationships, applying to read words)
3. Fluency (accurate, automatic reading with prosody)
4. Vocabulary (word meanings, relationships, context clues, morphology)
5. Comprehension (understanding, interpreting, analyzing text)

MAPPING PRINCIPLES:
- Match skill scope to appropriate taxonomy granularity (broad skills → parent nodes, specific skills → granular child nodes)
- Not all skills map to all 6 hierarchy levels—map only to levels that accurately match the skill's scope
- Distinguish grade-agnostic skills (e.g., "decode word families") from grade-dependent skills (e.g., "analyze grade-level text")
  * Grade-agnostic: Map without grade penalty—skill is same across grades
  * Grade-dependent: Verify developmental appropriateness—skill complexity tied to grade
- Distinguish receptive (listening/reading) vs. productive (speaking/writing) skills
- Consider prerequisite relationships (e.g., phoneme blending before syllable blending)
- Watch for skills outside literacy scope (digital literacy, SEL, metacognition)

CONFIDENCE CRITERIA:
- High: Direct semantic + developmental match (similarity >0.75), clear SoR pillar alignment, grade-appropriate
- Medium: Good semantic match (0.5-0.75), slight developmental/scope adjustment needed, reasonable interpretation
- Low: Weak semantic match (<0.5), developmental mismatch, or outside literacy scope → flag as potential taxonomy gap

COMMON PITFALLS TO AVOID:
- Don't confuse Phonological Awareness (oral/no letters) with Phonics (involves print)
- Don't map receptive skills (identify, recognize) to productive nodes (write, compose)
- Don't impose grade restrictions on grade-agnostic skills (most decoding/phonics/vocabulary skills are same across grades)
- Only verify grade alignment for grade-dependent skills (e.g., comprehension tied to text complexity)
- Flag non-literacy skills (digital tools, collaboration, SEL) as outside scope
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
2. Determine the skill's scope: Is it broad (pillar-level), mid-level (domain/skill area), or fine-grained (specific skill subset)?
3. Review the candidate taxonomy nodes
4. Select the top {top_k} best matches at the appropriate granularity level
5. For each match, provide:
   - Taxonomy path at appropriate level (may be 2-6 levels deep depending on skill scope)
   - Confidence level (High/Medium/Low)
   - Brief rationale (1-2 sentences explaining the match and why this granularity is appropriate)

OUTPUT FORMAT - YOU MUST FOLLOW THIS EXACTLY:

Example for skill "Blend spoken phonemes into CVC words":
1. Phonological Awareness > Phoneme Blending > CVC Words | Confidence: High | Rationale: Direct match for CVC blending at appropriate granularity level
2. Phonological Awareness > Phoneme Blending | Confidence: Medium | Rationale: Good match but less specific than skill requires
3. Phonological Awareness > Syllable and Phoneme Awareness | Confidence: Medium | Rationale: Parent category, too broad for specific CVC focus

Your output for this skill (COPY THIS FORMAT EXACTLY, replacing only the taxonomy paths and text):
1. [Full Taxonomy Path with > separators] | Confidence: [High/Medium/Low] | Rationale: [1-2 sentence explanation]
2. [Full Taxonomy Path with > separators] | Confidence: [High/Medium/Low] | Rationale: [1-2 sentence explanation]
...

CRITICAL REQUIREMENTS:
- YOU MUST start each line with a number (1., 2., 3., etc.)
- YOU MUST include the FULL taxonomy path from candidates above (copy the exact path with > separators)
- YOU MUST include the pipe character | to separate sections
- YOU MUST include "Confidence: High", "Confidence: Medium", or "Confidence: Low" 
- YOU MUST include "Rationale:" followed by your explanation
- DO NOT write explanatory paragraphs - only use the numbered format shown above
- DO NOT explain your reasoning before listing the mappings - jump straight to the numbered list
- Match skill scope to taxonomy granularity (don't force all skills into deepest level)
- Examples:
  * Broad: "Read fluently" → Fluency (2 levels)
  * Mid-level: "Use context clues" → Vocabulary > Context Clues (3 levels)
  * Fine-grained: "Blend CVC words" → Phonological Awareness > Phoneme Blending > CVC Words (4+ levels)
- High confidence: Direct match at appropriate granularity, clear alignment
- Medium confidence: Good match, requires slight interpretation
- Low confidence: Best available, but needs expert review
- Focus on the ROCK skill's actual learning objective, not just keyword matching
- Consider grade-level appropriateness

Remember: Start your response IMMEDIATELY with "1. [Taxonomy Path] | Confidence: ..." - no preamble!"""

        try:
            response_text, tokens = self.call_bedrock_llm(prompt)
            print(f"  LLM response received ({tokens} tokens)")
            
            # Parse response
            suggestions = self.parse_llm_response(response_text)
            print(f"  Parsed {len(suggestions)} suggestions")
            
            # Add original candidates' similarity scores
            for suggestion in suggestions:
                # Try to find matching candidate
                for candidate in candidates:
                    if candidate['skill_subset'] in suggestion['taxonomy_path']:
                        suggestion['semantic_similarity'] = candidate['similarity_score']
                        suggestion['taxonomy_index'] = candidate['index']
                        break
                
                # Add ROCK skill info
                suggestion['skill_id'] = skill_id
                suggestion['skill_name'] = skill_name
            
            return suggestions[:top_k]
            
        except Exception as e:
            print(f"  Error in LLM mapping: {e}")
            # Fallback to semantic search only
            return [{
                'skill_id': skill_id,
                'skill_name': skill_name,
                'taxonomy_path': f"{c['strand']} > {c['pillar']} > {c['domain']} > {c['skill_area']} > {c['skill_set']} > {c['skill_subset']}",
                'confidence': 'Medium' if c['similarity_score'] > 0.7 else 'Low',
                'rationale': f"Semantic similarity: {c['similarity_score']:.3f} (LLM unavailable, fallback to embedding-based match)",
                'semantic_similarity': c['similarity_score'],
                'taxonomy_index': c['index']
            } for c in candidates[:top_k]]
    
    def get_usage_stats(self) -> Dict:
        """
        Get API usage statistics for cost tracking.
        """
        return {
            'api_calls': self.api_calls,
            'total_tokens': self.total_tokens,
            'estimated_cost_usd': self.total_tokens * 0.003 / 1000  # Rough estimate for Claude
        }
    
    def print_usage_stats(self):
        """
        Print usage statistics.
        """
        stats = self.get_usage_stats()
        print("\n" + "=" * 60)
        print("LLM USAGE STATISTICS")
        print("=" * 60)
        print(f"API Calls: {stats['api_calls']:,}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Estimated Cost: ${stats['estimated_cost_usd']:.2f}")
        print("=" * 60)


def main():
    """
    Test function for LLM mapping assistant.
    """
    print("LLM-Assisted Taxonomy Mapping Tool")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    taxonomy_path = Path('../POC_science_of_reading_literacy_skills_taxonomy.csv')
    skills_path = Path('../rock_schemas/SKILLS.csv')
    
    taxonomy_df = pd.read_csv(taxonomy_path)
    skills_df = pd.read_csv(skills_path)
    
    print(f"Loaded {len(taxonomy_df)} taxonomy entries")
    print(f"Loaded {len(skills_df)} ROCK skills")
    
    # Initialize assistant
    assistant = LLMMapperAssistant(taxonomy_df)
    
    # Test with a few skills
    print("\n" + "=" * 60)
    print("TESTING WITH SAMPLE SKILLS")
    print("=" * 60)
    
    test_skills = skills_df[skills_df['CONTENT_AREA_NAME'] == 'ELA'].head(3)
    
    for _, skill in test_skills.iterrows():
        suggestions = assistant.suggest_mappings(
            skill_id=skill['SKILL_ID'],
            skill_name=skill['SKILL_NAME'],
            skill_area=skill.get('SKILL_AREA_NAME'),
            content_area=skill.get('CONTENT_AREA_NAME'),
            grade_level=skill.get('GRADE_LEVEL_NAME'),
            top_k=3
        )
        
        print(f"\nSuggestions for: {skill['SKILL_NAME']}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n  {i}. {suggestion['taxonomy_path']}")
            print(f"     Confidence: {suggestion['confidence']}")
            print(f"     Rationale: {suggestion['rationale']}")
            if 'semantic_similarity' in suggestion:
                print(f"     Semantic Similarity: {suggestion['semantic_similarity']:.3f}")
    
    # Print usage
    assistant.print_usage_stats()


if __name__ == '__main__':
    main()

