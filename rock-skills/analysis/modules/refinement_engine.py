#!/usr/bin/env python3
"""
Mapping Refinement Engine

Iteratively refines low-confidence mappings through re-prompting and gap analysis.
"""

import pandas as pd
from typing import Dict, List, Optional
import json


class MappingRefinement:
    """
    Refines low-confidence skill-to-taxonomy mappings through iterative LLM queries.
    """
    
    def __init__(self, llm_assistant):
        """
        Initialize refinement engine with LLM assistant.
        
        Args:
            llm_assistant: LLMMapperAssistant instance
        """
        self.assistant = llm_assistant
    
    def refine_low_confidence_mapping(
        self,
        skill: Dict,
        initial_suggestions: List[Dict],
        max_iterations: int = 2
    ) -> Dict:
        """
        Attempt to improve low confidence mappings through iterative refinement.
        
        Strategy:
        1. Re-prompt with expanded context (similar skills, taxonomy structure hints)
        2. Query for prerequisite/related skills already mapped
        3. If still low confidence after max_iterations, classify as taxonomy gap
        
        Args:
            skill: Dict with SKILL_ID, SKILL_NAME, GRADE_LEVEL_NAME, etc.
            initial_suggestions: List of initial mapping suggestions
            max_iterations: Maximum refinement attempts
            
        Returns:
            Refined mapping dict or gap classification
        """
        print(f"    Refining low-confidence mapping (max {max_iterations} iterations)...")
        
        best_suggestion = initial_suggestions[0] if initial_suggestions else None
        current_confidence = best_suggestion['confidence'] if best_suggestion else 'Low'
        
        iteration = 0
        while iteration < max_iterations and current_confidence == 'Low':
            iteration += 1
            print(f"      Iteration {iteration}: Attempting refinement...")
            
            # Strategy 1: Re-prompt with more context
            refined_prompt = self._build_refinement_prompt(skill, initial_suggestions, iteration)
            
            try:
                response_text, tokens = self.assistant.call_bedrock_llm(refined_prompt, max_tokens=3000)
                
                # Parse response
                refined_suggestions = self.assistant.parse_llm_response(response_text)
                
                if refined_suggestions:
                    best_refined = refined_suggestions[0]
                    current_confidence = best_refined['confidence']
                    
                    if current_confidence != 'Low':
                        print(f"      ✓ Refinement successful: {current_confidence} confidence")
                        # Add metadata about refinement
                        best_refined['refinement_iteration'] = iteration
                        best_refined['skill_id'] = skill.get('SKILL_ID')
                        best_refined['skill_name'] = skill.get('SKILL_NAME')
                        return best_refined
                    else:
                        print(f"      Still low confidence after iteration {iteration}")
                
            except Exception as e:
                print(f"      Error in refinement iteration {iteration}: {e}")
                break
        
        # If we get here, refinement failed
        print(f"      ✗ Refinement failed after {iteration} iterations")
        
        # Classify as taxonomy gap
        gap_analysis = self.extract_gap_characteristics(skill, initial_suggestions)
        
        return {
            'skill_id': skill.get('SKILL_ID'),
            'skill_name': skill.get('SKILL_NAME'),
            'taxonomy_path': best_suggestion['taxonomy_path'] if best_suggestion else 'UNMAPPABLE',
            'confidence': 'Low',
            'rationale': f"Refinement failed after {iteration} iterations. {gap_analysis['gap_reason']}",
            'semantic_similarity': initial_suggestions[0].get('semantic_similarity', 0) if initial_suggestions else 0,
            'needs_review': True,
            'gap_analysis': json.dumps(gap_analysis),
            'refinement_iterations': iteration,
            'status': 'gap_candidate'
        }
    
    def _build_refinement_prompt(
        self,
        skill: Dict,
        initial_suggestions: List[Dict],
        iteration: int
    ) -> str:
        """
        Build a refinement prompt with additional context.
        """
        skill_name = skill.get('SKILL_NAME', '')
        skill_area = skill.get('SKILL_AREA_NAME', 'N/A')
        grade_level = skill.get('GRADE_LEVEL_NAME', 'N/A')
        
        # Format initial suggestions
        initial_mappings_text = ""
        for i, sug in enumerate(initial_suggestions[:3], 1):
            initial_mappings_text += f"\n{i}. {sug['taxonomy_path']} (Confidence: {sug['confidence']})"
        
        prompt = f"""You are an expert in literacy education and the Science of Reading framework.

PREVIOUS MAPPING ATTEMPT:
A ROCK skill was mapped to the Science of Reading taxonomy, but the mapping had LOW confidence.
We need your help to either find a better mapping or confirm this skill doesn't fit the taxonomy.

ROCK SKILL:
- Name: {skill_name}
- Skill Area: {skill_area}
- Grade Level: {grade_level}

PREVIOUS SUGGESTIONS (Low Confidence):
{initial_mappings_text}

REFINEMENT STRATEGY (Iteration {iteration}):
1. Reconsider the skill's CORE learning objective (what is it really teaching?)
2. Think about developmental progressions (is this a foundational, developing, or advanced skill?)
3. Consider if this skill bridges multiple SoR pillars
4. Check if this might be outside traditional literacy (e.g., digital literacy, SEL, metacognition)

INSTRUCTIONS:
Provide ONE of the following:

A) If you can find a BETTER mapping:
   - Full taxonomy path
   - Confidence: High or Medium (explain why it's better than previous)
   - Rationale: Why this mapping is more appropriate

B) If no good mapping exists:
   - Taxonomy path: "UNMAPPABLE"
   - Confidence: Low
   - Rationale: Explain why this skill doesn't fit the Science of Reading taxonomy
   - Gap type: One of [digital-literacy, SEL, metacognition, assessment-only, writing-conventions, other]

OUTPUT FORMAT:
[Taxonomy Path or UNMAPPABLE] | Confidence: [High/Medium/Low] | Rationale: [Explanation] | Gap Type: [if unmappable]
"""
        
        return prompt
    
    def extract_gap_characteristics(
        self,
        skill: Dict,
        failed_candidates: List[Dict]
    ) -> Dict:
        """
        Extract characteristics of why a skill couldn't be mapped.
        
        Args:
            skill: The ROCK skill that failed to map
            failed_candidates: List of candidates that were tried
            
        Returns:
            Dict with gap analysis
        """
        skill_name = skill.get('SKILL_NAME', '').lower()
        skill_area = skill.get('SKILL_AREA_NAME', '').lower()
        grade_level = skill.get('GRADE_LEVEL_NAME', '')
        
        # Analyze why mapping failed
        gap_type = 'unknown'
        gap_reason = 'Unable to map to Science of Reading taxonomy'
        potential_taxonomy_node = None
        
        # Check for common patterns
        digital_keywords = ['digital', 'online', 'computer', 'technology', 'internet', 'website', 'multimedia']
        sel_keywords = ['collaborate', 'cooperate', 'empathy', 'self-regulate', 'emotional', 'social']
        metacog_keywords = ['monitor', 'self-assess', 'reflect', 'evaluate own', 'set goals']
        writing_keywords = ['handwriting', 'cursive', 'letter formation', 'keyboard', 'typing']
        assessment_keywords = ['assessment', 'test', 'measure', 'benchmark', 'screen']
        
        if any(kw in skill_name for kw in digital_keywords):
            gap_type = 'digital-literacy'
            gap_reason = 'Skill involves digital/technology components outside traditional SoR scope'
            potential_taxonomy_node = 'Digital Literacy > Online Research/Media Literacy'
            
        elif any(kw in skill_name for kw in sel_keywords):
            gap_type = 'social-emotional'
            gap_reason = 'Skill involves social-emotional learning, not core literacy'
            potential_taxonomy_node = 'SEL > Collaboration/Communication Skills'
            
        elif any(kw in skill_name for kw in metacog_keywords):
            gap_type = 'metacognition'
            gap_reason = 'Skill involves metacognitive strategies beyond reading comprehension'
            potential_taxonomy_node = 'Metacognition > Learning Strategies'
            
        elif any(kw in skill_name for kw in writing_keywords):
            gap_type = 'writing-conventions'
            gap_reason = 'Skill focuses on writing mechanics, not reading'
            potential_taxonomy_node = 'Writing > Conventions/Mechanics'
            
        elif any(kw in skill_name for kw in assessment_keywords):
            gap_type = 'assessment-only'
            gap_reason = 'Skill describes assessment procedure rather than instructional objective'
            potential_taxonomy_node = None
        
        # Check if candidates were all low similarity
        if failed_candidates:
            best_similarity = max((c.get('similarity_score', 0) for c in failed_candidates), default=0)
            if best_similarity < 0.3:
                gap_reason += f" (Best semantic similarity: {best_similarity:.2f})"
        
        return {
            'skill_id': skill.get('SKILL_ID'),
            'skill_name': skill.get('SKILL_NAME'),
            'skill_area': skill.get('SKILL_AREA_NAME'),
            'grade_level': grade_level,
            'gap_type': gap_type,
            'gap_reason': gap_reason,
            'potential_taxonomy_node': potential_taxonomy_node,
            'best_candidate_similarity': best_similarity if failed_candidates else 0,
            'num_candidates_tried': len(failed_candidates)
        }
    
    def suggest_taxonomy_extension(self, gap_characteristics: Dict) -> Optional[str]:
        """
        Suggest a potential taxonomy extension based on gap analysis.
        
        Args:
            gap_characteristics: Gap analysis dict
            
        Returns:
            Suggested taxonomy node structure or None
        """
        gap_type = gap_characteristics.get('gap_type')
        potential_node = gap_characteristics.get('potential_taxonomy_node')
        
        if potential_node:
            return f"Suggested Extension: {potential_node}\nJustification: {gap_characteristics['gap_reason']}"
        
        return None


def test_refinement():
    """
    Test function for refinement engine (requires LLM assistant).
    """
    print("Refinement Engine Test")
    print("=" * 60)
    print("Note: Full testing requires LLMMapperAssistant instance")
    print("This is a structure validation only.")
    
    # Mock skill and suggestions
    mock_skill = {
        'SKILL_ID': 'test-123',
        'SKILL_NAME': 'Use digital tools to research online',
        'SKILL_AREA_NAME': 'Research Skills',
        'GRADE_LEVEL_NAME': 'Grade 8'
    }
    
    mock_suggestions = [{
        'taxonomy_path': 'Comprehension > Research Skills',
        'confidence': 'Low',
        'rationale': 'Weak match',
        'semantic_similarity': 0.4
    }]
    
    # Mock assistant (placeholder)
    class MockAssistant:
        def call_bedrock_llm(self, prompt, max_tokens):
            return "Mock response", 100
        
        def parse_llm_response(self, text):
            return []
    
    refiner = MappingRefinement(MockAssistant())
    gap = refiner.extract_gap_characteristics(mock_skill, mock_suggestions)
    
    print("\nGap Analysis:")
    print(f"  Type: {gap['gap_type']}")
    print(f"  Reason: {gap['gap_reason']}")
    print(f"  Suggested Node: {gap['potential_taxonomy_node']}")
    
    print("\n✓ Refinement engine structure validated")


if __name__ == '__main__':
    test_refinement()

