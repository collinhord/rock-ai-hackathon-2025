#!/usr/bin/env python3
"""
MECE Validator & Redundancy Analyzer

Validates Mutually Exclusive, Collectively Exhaustive properties and
identifies redundant/ambiguous skills.

Features:
- Level 1: ROCK skill redundancy detection
- Level 2: Base skill ambiguity detection
- Level 3: LLM-powered semantic grooming

Usage:
    python3 validate_mece.py --base-skills base_skills/ --mappings mappings/ --output validation_report.json
"""

import sys
import json
import pandas as pd
import spacy
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime
from itertools import combinations
import argparse

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not available. LLM analysis disabled.")

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using fallback similarity.")


class MECEValidator:
    """Validate MECE properties and detect redundancies."""
    
    def __init__(self, use_llm: bool = True):
        """Initialize the validator."""
        self.use_llm = use_llm and BEDROCK_AVAILABLE
        
        # Load spaCy model for similarity
        try:
            self.nlp = spacy.load("en_core_web_lg")
            print("✓ Loaded spaCy model: en_core_web_lg")
        except OSError:
            print("⚠ spaCy model 'en_core_web_lg' not found")
            self.nlp = None
        
        # Load sentence transformer for enhanced embeddings
        if EMBEDDINGS_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Loaded sentence transformer: all-MiniLM-L6-v2")
        else:
            self.embedder = None
        
        # Initialize Bedrock if available
        if self.use_llm:
            try:
                self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
                print("✓ Initialized AWS Bedrock client")
            except Exception as e:
                print(f"⚠ Could not initialize Bedrock: {e}")
                self.use_llm = False
        
        # Track findings
        self.conflicts = []
        self.redundancies = []
        self.ambiguities = []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if self.embedder:
            # Use sentence transformer for better semantic similarity
            emb1 = self.embedder.encode([text1])
            emb2 = self.embedder.encode([text2])
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        elif self.nlp:
            # Use spaCy similarity
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            return doc1.similarity(doc2)
        else:
            # Fallback to simple string similarity
            from difflib import SequenceMatcher
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def calculate_overlap_signals(self, skill_a: Dict, skill_b: Dict) -> Dict:
        """
        Calculate multiple overlap signals for comprehensive detection.
        
        Args:
            skill_a: First base skill
            skill_b: Second base skill
            
        Returns:
            Dictionary with overlap signals and aggregate score
        """
        signals = {}
        
        # Signal 1: Semantic similarity (embeddings)
        name_a = skill_a.get('base_skill_name', '')
        name_b = skill_b.get('base_skill_name', '')
        signals['semantic_similarity'] = self.calculate_similarity(name_a, name_b)
        
        # Signal 2: Structural overlap (same root verb + similar targets)
        root_verb_a = skill_a.get('root_verb', '')
        root_verb_b = skill_b.get('root_verb', '')
        signals['root_verb_match'] = (root_verb_a == root_verb_b and root_verb_a != '')
        
        # Signal 3: Skill family match
        family_a = skill_a.get('skill_family', '')
        family_b = skill_b.get('skill_family', '')
        signals['skill_family_match'] = (family_a == family_b and family_a != '')
        
        # Signal 4: Member skill overlap (do they share ROCK skills?)
        members_a = set(skill_a.get('member_skill_ids', []))
        members_b = set(skill_b.get('member_skill_ids', []))
        shared_members = members_a & members_b
        signals['member_overlap'] = len(shared_members) > 0
        signals['shared_member_count'] = len(shared_members)
        
        # Signal 5: Specification profile similarity
        specs_a = set(skill_a.get('specifications', {}).keys())
        specs_b = set(skill_b.get('specifications', {}).keys())
        if specs_a and specs_b:
            intersection = len(specs_a & specs_b)
            union = len(specs_a | specs_b)
            signals['spec_profile_similarity'] = intersection / union if union > 0 else 0
        else:
            signals['spec_profile_similarity'] = 0.0
        
        # Aggregate overall score
        overall_score = (
            signals['semantic_similarity'] * 0.40 +
            (1.0 if signals['root_verb_match'] else 0.0) * 0.25 +
            (1.0 if signals['skill_family_match'] else 0.5) * 0.10 +
            (0.5 if signals['member_overlap'] else 0.0) * 0.15 +
            signals['spec_profile_similarity'] * 0.10
        )
        
        signals['overall_overlap_score'] = overall_score
        
        # Confidence based on signal agreement
        signal_agreement = sum([
            signals['semantic_similarity'] > 0.75,
            signals['root_verb_match'],
            signals['skill_family_match'],
            signals['member_overlap']
        ]) / 4
        
        signals['confidence'] = 'high' if signal_agreement >= 0.75 else 'medium' if signal_agreement >= 0.5 else 'low'
        
        return signals
    
    def detect_rock_skill_redundancy(self, mappings_df: pd.DataFrame, 
                                     base_skill_id: str) -> List[Dict]:
        """
        Detect redundant ROCK skills within the same base skill group.
        
        Args:
            mappings_df: DataFrame with ROCK skill mappings
            base_skill_id: Base skill ID to check
            
        Returns:
            List of redundancy findings
        """
        redundancies = []
        
        # Get all ROCK skills mapped to this base skill
        rock_skills = mappings_df[mappings_df['base_skill_id'] == base_skill_id]
        
        if len(rock_skills) < 2:
            return redundancies
        
        # Check all pairs
        for (idx1, skill1), (idx2, skill2) in combinations(rock_skills.iterrows(), 2):
            similarity = self.calculate_similarity(
                skill1['SKILL_NAME'],
                skill2['SKILL_NAME']
            )
            
            # Check if same grade + state
            same_context = False
            if 'GRADE_LEVEL_NAME' in skill1 and 'GRADE_LEVEL_NAME' in skill2:
                same_context = (
                    skill1.get('GRADE_LEVEL_NAME') == skill2.get('GRADE_LEVEL_NAME')
                )
            
            # Flag if high similarity or same context
            if similarity > 0.90 or (similarity > 0.80 and same_context):
                redundancy = {
                    'redundancy_id': f"RED-{len(self.redundancies) + 1:03d}",
                    'base_skill_id': base_skill_id,
                    'skill_a': {
                        'id': skill1['SKILL_ID'],
                        'name': skill1['SKILL_NAME'],
                        'grade': skill1.get('GRADE_LEVEL_NAME', 'Unknown'),
                        'state': skill1.get('STANDARD_SET_NAME', 'Unknown')
                    },
                    'skill_b': {
                        'id': skill2['SKILL_ID'],
                        'name': skill2['SKILL_NAME'],
                        'grade': skill2.get('GRADE_LEVEL_NAME', 'Unknown'),
                        'state': skill2.get('STANDARD_SET_NAME', 'Unknown')
                    },
                    'similarity': float(similarity),
                    'same_context': same_context,
                    'redundancy_type': 'wording_variation' if similarity > 0.90 else 'context_overlap',
                    'recommendation': 'merge_or_differentiate',
                    'status': 'auto_flagged'
                }
                
                redundancies.append(redundancy)
                self.redundancies.append(redundancy)
        
        return redundancies
    
    def detect_base_skill_ambiguity(self, base_skills: List[Dict]) -> List[Dict]:
        """
        Detect base skills that may overlap or need specification refinement (ENHANCED).
        
        Args:
            base_skills: List of base skill definitions
            
        Returns:
            List of ambiguity findings with comprehensive overlap signals
        """
        ambiguities = []
        
        # Ambiguous keywords that often indicate specification needs
        ambiguous_terms = [
            'perspective', 'point of view', 'viewpoint', 'stance',
            'analyze', 'evaluate', 'assess', 'examine',
            'identify', 'determine', 'recognize',
            'idea', 'concept', 'theme', 'message',
            'text', 'passage', 'writing', 'story'
        ]
        
        print(f"Checking {len(base_skills)} base skills for ambiguity (enhanced detection)...")
        
        for (skill_a, skill_b) in combinations(base_skills, 2):
            name_a = skill_a.get('base_skill_name', '')
            name_b = skill_b.get('base_skill_name', '')
            
            # Use enhanced overlap detection
            overlap_signals = self.calculate_overlap_signals(skill_a, skill_b)
            
            # Check for shared ambiguous terms
            has_ambiguous_term = any(
                term in name_a.lower() and term in name_b.lower()
                for term in ambiguous_terms
            )
            
            # Flag if overall overlap score is significant OR shared ambiguous terms
            if overlap_signals['overall_overlap_score'] > 0.70 or (has_ambiguous_term and overlap_signals['semantic_similarity'] > 0.60):
                print(f"  Found overlap: '{name_a}' vs '{name_b}' (score: {overlap_signals['overall_overlap_score']:.2f}, confidence: {overlap_signals['confidence']})")
                
                # Get LLM analysis if available
                llm_analysis = self.analyze_ambiguity_with_llm(skill_a, skill_b)
                
                ambiguity = {
                    'conflict_id': f"CONFLICT-{len(self.conflicts) + 1:03d}",
                    'skill_a': {
                        'id': skill_a.get('base_skill_id'),
                        'name': name_a,
                        'description': skill_a.get('base_skill_description', ''),
                        'rock_skills_count': skill_a.get('rock_skills_count', 0)
                    },
                    'skill_b': {
                        'id': skill_b.get('base_skill_id'),
                        'name': name_b,
                        'description': skill_b.get('base_skill_description', ''),
                        'rock_skills_count': skill_b.get('rock_skills_count', 0)
                    },
                    'overlap_score': float(overlap_signals['overall_overlap_score']),
                    'overlap_signals': overlap_signals,
                    'has_ambiguous_term': has_ambiguous_term,
                    'llm_analysis': llm_analysis,
                    'confidence': overlap_signals['confidence'],
                    'status': 'pending_human_review'
                }
                
                ambiguities.append(ambiguity)
                self.conflicts.append(ambiguity)
        
        return ambiguities
    
    def analyze_ambiguity_with_llm(self, skill_a: Dict, skill_b: Dict) -> Dict:
        """
        Use LLM to analyze if two base skills are redundant or distinct.
        
        Args:
            skill_a: First base skill
            skill_b: Second base skill
            
        Returns:
            Dictionary with LLM analysis
        """
        if not self.use_llm:
            return {
                'category': 'AMBIGUOUS',
                'confidence': 'low',
                'reasoning': 'LLM analysis not available',
                'action': {'type': 'REVIEW'}
            }
        
        prompt = f"""You are an expert in literacy taxonomy design.

TASK: Determine if these base skills are redundant, need specifications, or are distinct.

BASE SKILL A: {skill_a.get('base_skill_name', '')}
Description: {skill_a.get('base_skill_description', '')}
Number of ROCK skills: {skill_a.get('rock_skills_count', 0)}

BASE SKILL B: {skill_b.get('base_skill_name', '')}
Description: {skill_b.get('base_skill_description', '')}
Number of ROCK skills: {skill_b.get('rock_skills_count', 0)}

ANALYSIS CATEGORIES:

1. TRUE_DUPLICATE: Same concept, different wording
   Example: "Determine Main Idea" ≈ "Identify Central Concept"
   → Recommendation: MERGE

2. SPECIFICATION_NEEDED: Same base, different contexts need specification
   Example: "Analyze Perspective" could be:
     - perspective_type: "narrative_pov" (1st/3rd person technical POV)
     - perspective_type: "character_viewpoint" (character bias/background)
     - perspective_type: "author_stance" (author's implicit ideology)
   → Recommendation: CREATE_SPECIFICATION

3. DISTINCT_SKILLS: Different concepts, similar wording
   Example: "Analyze POV" (narrative technique) vs "Analyze Character Bias" (character psychology)
   → Recommendation: CLARIFY definitions

4. AMBIGUOUS: Needs human review

IMPORTANT: "Perspective" is often ambiguous:
- Narrative perspective = POV technique (1st/3rd person, limited/omniscient)
- Character perspective = worldview/bias influenced by background
- Author perspective = implicit ideology/stance in text

RESPOND ONLY WITH JSON:
{{
    "category": "TRUE_DUPLICATE|SPECIFICATION_NEEDED|DISTINCT_SKILLS|AMBIGUOUS",
    "confidence": "high|medium|low",
    "reasoning": "Explain your analysis in 2-3 sentences",
    "action": {{
        "type": "MERGE|CREATE_SPEC|CLARIFY|REVIEW",
        "details": {{
            "merged_name": "if MERGE, proposed merged name",
            "new_specification": {{
                "spec_type": "if CREATE_SPEC, the specification type",
                "spec_values": ["value1", "value2", "value3"]
            }},
            "clarifications": {{
                "skill_a": "if CLARIFY, how to clarify skill A",
                "skill_b": "if CLARIFY, how to clarify skill B"
            }}
        }}
    }}
}}

Start your response IMMEDIATELY with "{{" - no preamble!"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-sonnet-4-5-v2:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "temperature": 0.3,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                })
            )
            
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in LLM response")
                
        except Exception as e:
            print(f"⚠ LLM analysis failed: {e}")
            return {
                'category': 'AMBIGUOUS',
                'confidence': 'low',
                'reasoning': f'LLM error: {str(e)}',
                'action': {'type': 'REVIEW'},
                'error': str(e)
            }
    
    def validate_mutual_exclusivity(self, base_skills: List[Dict], 
                                     mappings_df: pd.DataFrame) -> Dict:
        """
        Validate that base skills are mutually exclusive.
        
        Returns:
            Dictionary with mutual exclusivity metrics
        """
        print("\n=== MUTUAL EXCLUSIVITY VALIDATION ===\n")
        
        # Check 1: Base skill conflicts (semantic overlap)
        print("Checking for base skill conflicts...")
        conflicts = self.detect_base_skill_ambiguity(base_skills)
        print(f"✓ Found {len(conflicts)} potential conflicts")
        
        # Check 2: ROCK skill redundancies
        print("\nChecking for ROCK skill redundancies...")
        all_redundancies = []
        for base_skill in base_skills:
            base_id = base_skill['base_skill_id']
            redundancies = self.detect_rock_skill_redundancy(mappings_df, base_id)
            all_redundancies.extend(redundancies)
        print(f"✓ Found {len(all_redundancies)} potential redundancies")
        
        # Check 3: Each ROCK skill maps to exactly ONE base skill
        duplicate_mappings = mappings_df[mappings_df['base_skill_id'].notna()].duplicated(
            subset=['SKILL_ID'], keep=False
        )
        num_duplicates = duplicate_mappings.sum()
        
        # Calculate score
        total_checks = len(base_skills) * (len(base_skills) - 1) / 2  # All pairs
        conflicts_ratio = len(conflicts) / total_checks if total_checks > 0 else 0
        me_score = 1.0 - conflicts_ratio
        
        return {
            'score': float(me_score),
            'base_skill_conflicts': conflicts,
            'rock_skill_redundancies': all_redundancies,
            'duplicate_mappings': int(num_duplicates)
        }
    
    def validate_collective_exhaustiveness(self, base_skills: List[Dict],
                                          mappings_df: pd.DataFrame,
                                          skills_df: pd.DataFrame) -> Dict:
        """
        Validate that base skills collectively cover all ROCK skills.
        
        Returns:
            Dictionary with collective exhaustiveness metrics
        """
        print("\n=== COLLECTIVE EXHAUSTIVENESS VALIDATION ===\n")
        
        # Check 1: Unmapped ROCK skills
        total_rock_skills = len(skills_df)
        mapped_skills = mappings_df['base_skill_id'].notna().sum()
        unmapped_skills = total_rock_skills - mapped_skills
        
        print(f"Total ROCK skills: {total_rock_skills}")
        print(f"Mapped skills: {mapped_skills}")
        print(f"Unmapped skills: {unmapped_skills}")
        
        # Calculate score
        ce_score = mapped_skills / total_rock_skills if total_rock_skills > 0 else 0
        
        return {
            'score': float(ce_score),
            'unmapped_rock_skills': int(unmapped_skills),
            'total_rock_skills': int(total_rock_skills),
            'mapped_rock_skills': int(mapped_skills)
        }
    
    def generate_validation_report(self, base_skills: List[Dict],
                                   mappings_df: pd.DataFrame,
                                   skills_df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive MECE validation report.
        
        Returns:
            Complete validation report
        """
        print("\n" + "="*60)
        print("MECE VALIDATION & REDUNDANCY ANALYSIS")
        print("="*60)
        
        # Validate mutual exclusivity
        me_results = self.validate_mutual_exclusivity(base_skills, mappings_df)
        
        # Validate collective exhaustiveness
        ce_results = self.validate_collective_exhaustiveness(
            base_skills, mappings_df, skills_df
        )
        
        # Calculate overall MECE score
        mece_score = (me_results['score'] + ce_results['score']) / 2
        
        # Grooming queue summary
        grooming_summary = {
            'total_conflicts': len(me_results['base_skill_conflicts']),
            'total_redundancies': len(me_results['rock_skill_redundancies']),
            'high_confidence_merges': sum(
                1 for c in me_results['base_skill_conflicts']
                if c.get('llm_analysis', {}).get('category') == 'TRUE_DUPLICATE'
                and c.get('llm_analysis', {}).get('confidence') == 'high'
            ),
            'spec_needed': sum(
                1 for c in me_results['base_skill_conflicts']
                if c.get('llm_analysis', {}).get('category') == 'SPECIFICATION_NEEDED'
            ),
            'human_review_required': sum(
                1 for c in me_results['base_skill_conflicts']
                if c.get('llm_analysis', {}).get('category') == 'AMBIGUOUS'
            )
        }
        
        # Generate report
        report = {
            'generated_timestamp': datetime.utcnow().isoformat() + 'Z',
            'mece_score': float(mece_score),
            'mutual_exclusivity': me_results,
            'collective_exhaustiveness': ce_results,
            'grooming_queue_summary': grooming_summary,
            'statistics': {
                'total_base_skills': len(base_skills),
                'total_rock_skills': len(skills_df),
                'average_skills_per_base': len(skills_df) / len(base_skills) if base_skills else 0
            }
        }
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"MECE Score: {mece_score:.2f} / 1.00")
        print(f"  - Mutual Exclusivity: {me_results['score']:.2f}")
        print(f"  - Collective Exhaustiveness: {ce_results['score']:.2f}")
        print(f"\nGrooming Queue:")
        print(f"  - Total conflicts: {grooming_summary['total_conflicts']}")
        print(f"  - Total redundancies: {grooming_summary['total_redundancies']}")
        print(f"  - High confidence merges: {grooming_summary['high_confidence_merges']}")
        print(f"  - Specs needed: {grooming_summary['spec_needed']}")
        print(f"  - Human review required: {grooming_summary['human_review_required']}")
        print("="*60 + "\n")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Validate MECE properties and detect redundancies')
    parser.add_argument('--base-skills', required=True,
                       help='Directory with base skills JSON files')
    parser.add_argument('--mappings', required=True,
                       help='CSV file with ROCK skill mappings')
    parser.add_argument('--skills', default='../../rock_schemas/SKILLS.csv',
                       help='CSV file with all ROCK skills')
    parser.add_argument('--output', default='../../taxonomy/validation_report.json',
                       help='Output file for validation report')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM analysis')
    
    args = parser.parse_args()
    
    # Load base skills
    print(f"Loading base skills from {args.base_skills}...")
    base_skills = []
    base_skills_dir = Path(args.base_skills)
    
    for json_file in base_skills_dir.glob('BS-*.json'):
        with open(json_file) as f:
            base_skills.append(json.load(f))
    
    print(f"Loaded {len(base_skills)} base skills")
    
    # Load mappings
    print(f"Loading mappings from {args.mappings}...")
    mappings_df = pd.read_csv(args.mappings)
    print(f"Loaded {len(mappings_df)} mappings")
    
    # Load all ROCK skills
    print(f"Loading ROCK skills from {args.skills}...")
    skills_df = pd.read_csv(args.skills)
    print(f"Loaded {len(skills_df)} ROCK skills")
    
    # Initialize validator
    validator = MECEValidator(use_llm=not args.no_llm)
    
    # Generate validation report
    report = validator.generate_validation_report(base_skills, mappings_df, skills_df)
    
    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Saved validation report to {output_path}")
    
    # Also save conflicts and redundancies separately for UI
    conflicts_file = output_path.parent / 'conflicts.json'
    redundancies_file = output_path.parent / 'redundancies.json'
    
    with open(conflicts_file, 'w') as f:
        json.dump(report['mutual_exclusivity']['base_skill_conflicts'], f, indent=2)
    
    with open(redundancies_file, 'w') as f:
        json.dump(report['mutual_exclusivity']['rock_skill_redundancies'], f, indent=2)
    
    print(f"✓ Saved conflicts to {conflicts_file}")
    print(f"✓ Saved redundancies to {redundancies_file}")


if __name__ == '__main__':
    main()

