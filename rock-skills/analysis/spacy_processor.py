"""
spaCy Processor for ROCK Skills Analysis

Shared utility module for spaCy-based text processing, concept extraction,
and skill structure analysis. Used across semantic similarity and LLM mapping pipelines.

Usage:
    from spacy_processor import SkillProcessor
    
    processor = SkillProcessor()
    concepts = processor.extract_concepts("Blend phonemes to form words")
    structure = processor.extract_structure("Blend phonemes to form words")
"""

import spacy
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class SkillConcepts:
    """Structured representation of skill concepts."""
    actions: List[str]           # Verbs: blend, decode, identify
    targets: List[str]            # Nouns: phonemes, words, syllables
    qualifiers: List[str]         # Adjectives: one-syllable, CVC, multisyllabic
    grade_indicators: List[str]   # Grade-related terms
    complexity_markers: List[str] # Difficulty indicators
    cleaned_text: str             # Preprocessed text for embeddings
    key_concepts: List[str]       # Main content words


@dataclass
class SkillStructure:
    """Grammatical structure of a skill description."""
    root_verb: Optional[str]      # Main action
    direct_objects: List[str]     # What's being acted upon
    modifiers: List[str]          # Descriptive terms
    prepositional_phrases: List[str]  # Context phrases
    sentence_type: str            # declarative, imperative, etc.


class SkillProcessor:
    """
    spaCy-based processor for educational skill descriptions.
    
    Provides preprocessing, concept extraction, and structural analysis
    optimized for ROCK skills and Science of Reading taxonomy.
    """
    
    def __init__(self, model_name: str = 'en_core_web_sm'):
        """
        Initialize the processor with spaCy model.
        
        Args:
            model_name: spaCy model name (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(model_name)
            print(f"✓ Loaded spaCy model: {model_name}")
        except OSError:
            print(f"✗ Model '{model_name}' not found. Run: python -m spacy download {model_name}")
            raise
        
        # Educational domain vocabulary
        self.educational_verbs = {
            'blend', 'segment', 'decode', 'encode', 'identify', 'recognize',
            'analyze', 'synthesize', 'compare', 'contrast', 'infer', 'predict',
            'summarize', 'explain', 'describe', 'interpret', 'evaluate',
            'apply', 'demonstrate', 'produce', 'determine', 'distinguish'
        }
        
        self.literacy_targets = {
            'phoneme', 'grapheme', 'morpheme', 'syllable', 'word', 'sentence',
            'paragraph', 'text', 'passage', 'letter', 'sound', 'pattern',
            'vowel', 'consonant', 'blend', 'digraph', 'diphthong'
        }
        
        self.grade_indicators = {
            'kindergarten', 'k', 'pre-k', 'prek', 'first', 'second', 'third',
            'grade', 'early', 'beginning', 'emergent'
        }
        
        self.complexity_markers = {
            'simple', 'complex', 'multisyllabic', 'one-syllable', 'two-syllable',
            'cvc', 'ccvc', 'cvce', 'basic', 'advanced', 'high-frequency'
        }
    
    def preprocess_for_embeddings(self, text: str) -> str:
        """
        Preprocess text for better semantic embeddings.
        
        Removes noise, normalizes terms, focuses on content words.
        
        Args:
            text: Raw skill description
            
        Returns:
            Cleaned text optimized for embedding models
            
        Example:
            >>> processor.preprocess_for_embeddings(
            ...     "The student will blend spoken phonemes into one-syllable words"
            ... )
            'blend phoneme one-syllable word'
        """
        if not text or not text.strip():
            return ""
        
        doc = self.nlp(text.lower())
        
        # Extract content words (nouns, verbs, adjectives)
        content_words = []
        for token in doc:
            # Skip stop words and punctuation
            if token.is_stop or token.is_punct or token.is_space:
                continue
            
            # Keep important POS tags
            if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'NUM']:
                # Use lemma for normalization (phonemes -> phoneme)
                content_words.append(token.lemma_)
        
        return ' '.join(content_words)
    
    def extract_concepts(self, text: str) -> SkillConcepts:
        """
        Extract structured educational concepts from skill text.
        
        Args:
            text: Skill description
            
        Returns:
            SkillConcepts object with categorized concepts
            
        Example:
            >>> concepts = processor.extract_concepts(
            ...     "Blend spoken phonemes into one-syllable words"
            ... )
            >>> concepts.actions
            ['blend']
            >>> concepts.targets
            ['phonemes', 'words']
        """
        if not text or not text.strip():
            return SkillConcepts([], [], [], [], [], "", [])
        
        doc = self.nlp(text.lower())
        
        actions = []
        targets = []
        qualifiers = []
        grade_indicators = []
        complexity_markers = []
        key_concepts = []
        
        for token in doc:
            lemma = token.lemma_
            text_lower = token.text.lower()
            
            # Actions (verbs)
            if token.pos_ == 'VERB':
                actions.append(lemma)
                if lemma in self.educational_verbs:
                    key_concepts.append(lemma)
            
            # Targets (nouns)
            elif token.pos_ == 'NOUN':
                targets.append(text_lower)
                if lemma in self.literacy_targets:
                    key_concepts.append(lemma)
            
            # Qualifiers (adjectives, numbers)
            elif token.pos_ in ['ADJ', 'NUM']:
                qualifiers.append(text_lower)
            
            # Grade indicators
            if text_lower in self.grade_indicators:
                grade_indicators.append(text_lower)
            
            # Complexity markers
            if text_lower in self.complexity_markers:
                complexity_markers.append(text_lower)
        
        cleaned_text = self.preprocess_for_embeddings(text)
        
        return SkillConcepts(
            actions=actions,
            targets=targets,
            qualifiers=qualifiers,
            grade_indicators=grade_indicators,
            complexity_markers=complexity_markers,
            cleaned_text=cleaned_text,
            key_concepts=key_concepts
        )
    
    def extract_structure(self, text: str) -> SkillStructure:
        """
        Extract grammatical structure using dependency parsing.
        
        Useful for identifying structurally equivalent skills across
        different phrasings (state variants).
        
        Args:
            text: Skill description
            
        Returns:
            SkillStructure object with parsed structure
            
        Example:
            >>> structure = processor.extract_structure(
            ...     "Blend phonemes to form words"
            ... )
            >>> structure.root_verb
            'blend'
            >>> structure.direct_objects
            ['phonemes']
        """
        if not text or not text.strip():
            return SkillStructure(None, [], [], [], 'unknown')
        
        doc = self.nlp(text)
        
        root_verb = None
        direct_objects = []
        modifiers = []
        prep_phrases = []
        
        # Find root verb
        for token in doc:
            if token.dep_ == 'ROOT':
                root_verb = token.lemma_
                break
        
        # Extract syntactic elements
        for token in doc:
            # Direct objects
            if token.dep_ in ['dobj', 'obj', 'pobj']:
                direct_objects.append(token.text.lower())
            
            # Modifiers (adjectives, adverbs)
            elif token.dep_ in ['amod', 'advmod', 'acomp']:
                modifiers.append(token.text.lower())
            
            # Prepositional phrases
            elif token.dep_ == 'prep':
                # Get the prep + its object
                prep_obj = [child.text for child in token.children if child.dep_ == 'pobj']
                if prep_obj:
                    prep_phrases.append(f"{token.text} {prep_obj[0]}")
        
        # Determine sentence type
        sentence_type = 'declarative'
        if doc[0].pos_ == 'VERB':
            sentence_type = 'imperative'
        
        return SkillStructure(
            root_verb=root_verb,
            direct_objects=direct_objects,
            modifiers=modifiers,
            prepositional_phrases=prep_phrases,
            sentence_type=sentence_type
        )
    
    def compare_skills_structurally(self, skill1: str, skill2: str) -> Dict:
        """
        Compare two skills based on grammatical structure.
        
        Useful for identifying state variants that express the same
        concept differently.
        
        Args:
            skill1: First skill description
            skill2: Second skill description
            
        Returns:
            Dict with comparison results and similarity score
            
        Example:
            >>> processor.compare_skills_structurally(
            ...     "Blend phonemes to form words",
            ...     "Orally produce words by blending sounds"
            ... )
            {
                'same_root_verb': True,
                'overlapping_objects': ['words'],
                'structural_similarity': 0.75
            }
        """
        struct1 = self.extract_structure(skill1)
        struct2 = self.extract_structure(skill2)
        concepts1 = self.extract_concepts(skill1)
        concepts2 = self.extract_concepts(skill2)
        
        # Compare root verbs (normalized)
        same_root = struct1.root_verb == struct2.root_verb
        
        # Compare direct objects
        objects1 = set(struct1.direct_objects)
        objects2 = set(struct2.direct_objects)
        overlapping_objects = objects1 & objects2
        
        # Compare key concepts
        concepts1_set = set(concepts1.key_concepts)
        concepts2_set = set(concepts2.key_concepts)
        overlapping_concepts = concepts1_set & concepts2_set
        
        # Calculate structural similarity score
        similarity_score = 0.0
        if same_root:
            similarity_score += 0.4
        if overlapping_objects:
            similarity_score += 0.3 * (len(overlapping_objects) / max(len(objects1), len(objects2)))
        if overlapping_concepts:
            similarity_score += 0.3 * (len(overlapping_concepts) / max(len(concepts1_set), len(concepts2_set)))
        
        return {
            'same_root_verb': same_root,
            'root_verbs': (struct1.root_verb, struct2.root_verb),
            'overlapping_objects': list(overlapping_objects),
            'overlapping_concepts': list(overlapping_concepts),
            'structural_similarity': similarity_score,
            'likely_variant': similarity_score > 0.5
        }
    
    def batch_preprocess(self, texts: List[str], show_progress: bool = True) -> List[str]:
        """
        Preprocess multiple texts efficiently using spaCy's pipe.
        
        Args:
            texts: List of skill descriptions
            show_progress: Show progress bar (requires tqdm)
            
        Returns:
            List of preprocessed texts
        """
        if show_progress:
            try:
                from tqdm import tqdm
                docs = list(tqdm(
                    self.nlp.pipe(texts), 
                    total=len(texts),
                    desc="Processing with spaCy"
                ))
            except ImportError:
                docs = list(self.nlp.pipe(texts))
        else:
            docs = list(self.nlp.pipe(texts))
        
        cleaned_texts = []
        for doc in docs:
            content_words = [
                token.lemma_ for token in doc
                if not token.is_stop and not token.is_punct 
                and token.pos_ in ['NOUN', 'VERB', 'ADJ', 'NUM']
            ]
            cleaned_texts.append(' '.join(content_words))
        
        return cleaned_texts
    
    def identify_state_variants(self, skills_df, group_by_cols=['SKILL_AREA_NAME']) -> List[List[str]]:
        """
        Identify potential state variants by grouping structurally similar skills.
        
        Args:
            skills_df: DataFrame with SKILL_ID, SKILL_NAME columns
            group_by_cols: Columns to group by before comparing
            
        Returns:
            List of variant groups (each group is a list of SKILL_IDs)
        """
        variant_groups = []
        
        # Group skills by skill area for efficiency
        for _, group in skills_df.groupby(group_by_cols):
            if len(group) < 2:
                continue
            
            skills = group[['SKILL_ID', 'SKILL_NAME']].values.tolist()
            
            # Compare all pairs within group
            processed = set()
            for i, (id1, name1) in enumerate(skills):
                if id1 in processed:
                    continue
                
                variant_group = [id1]
                for id2, name2 in skills[i+1:]:
                    if id2 in processed:
                        continue
                    
                    comparison = self.compare_skills_structurally(name1, name2)
                    if comparison['likely_variant']:
                        variant_group.append(id2)
                        processed.add(id2)
                
                if len(variant_group) > 1:
                    variant_groups.append(variant_group)
                    processed.add(id1)
        
        return variant_groups


def demo():
    """Demonstration of SkillProcessor capabilities."""
    print("=" * 70)
    print("ROCK SKILLS spaCy PROCESSOR DEMO")
    print("=" * 70)
    
    processor = SkillProcessor()
    
    # Test skills
    skills = [
        "Blend phonemes to form words",
        "Orally produce words by blending sounds",
        "Blend spoken phonemes into one-syllable words",
        "Identify the main idea of a text",
        "Determine the central idea in a passage"
    ]
    
    print("\n1. PREPROCESSING FOR EMBEDDINGS")
    print("-" * 70)
    for skill in skills:
        cleaned = processor.preprocess_for_embeddings(skill)
        print(f"Original:    {skill}")
        print(f"Cleaned:     {cleaned}\n")
    
    print("\n2. CONCEPT EXTRACTION")
    print("-" * 70)
    skill = "Blend spoken phonemes into one-syllable words"
    concepts = processor.extract_concepts(skill)
    print(f"Skill: {skill}")
    print(f"  Actions:    {concepts.actions}")
    print(f"  Targets:    {concepts.targets}")
    print(f"  Qualifiers: {concepts.qualifiers}")
    print(f"  Key Concepts: {concepts.key_concepts}")
    
    print("\n3. STRUCTURAL ANALYSIS")
    print("-" * 70)
    structure = processor.extract_structure(skill)
    print(f"Skill: {skill}")
    print(f"  Root Verb:  {structure.root_verb}")
    print(f"  Objects:    {structure.direct_objects}")
    print(f"  Modifiers:  {structure.modifiers}")
    
    print("\n4. VARIANT DETECTION")
    print("-" * 70)
    skill1 = "Blend phonemes to form words"
    skill2 = "Orally produce words by blending sounds"
    comparison = processor.compare_skills_structurally(skill1, skill2)
    print(f"Skill 1: {skill1}")
    print(f"Skill 2: {skill2}")
    print(f"  Same Root Verb: {comparison['same_root_verb']}")
    print(f"  Structural Similarity: {comparison['structural_similarity']:.2f}")
    print(f"  Likely Variant: {comparison['likely_variant']}")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    demo()

