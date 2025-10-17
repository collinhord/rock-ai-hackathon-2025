# Comprehensive Metadata Schema Reference

## Overview

This document defines all 23 metadata fields extracted by the Enhanced Metadata Extractor, including their data types, allowed values, extraction methodology, and practical examples.

---

## Field Categories

| Category | Fields | Extraction Method | Cost |
|----------|--------|-------------------|------|
| **Core Identifiers** | 4 | Direct copy | Free |
| **Structural Components** | 8 | spaCy NLP | Free |
| **Educational Metadata** | 7 | LLM (Claude) | ~$0.003/skill |
| **Specifications** | 2 | Rule-based | Free |
| **Quality Metrics** | 2 | Automatic | Free |
| **Total** | **23** | **Hybrid** | **~$0.003/skill** |

---

## Core Identifiers

### SKILL_ID
- **Type**: String (UUID)
- **Source**: Direct from input dataset
- **Example**: `"11334c9c-a69f-e311-9503-005056801da1"`
- **Purpose**: Unique identifier for joining with other datasets

### SKILL_NAME
- **Type**: String (1-500 characters)
- **Source**: Direct from input dataset
- **Example**: `"Identify the basic elements of a story's plot (e.g., problem, important events)"`
- **Purpose**: Full skill description, primary input for all extraction methods

### SKILL_AREA_NAME
- **Type**: String
- **Source**: Direct from input dataset
- **Example**: `"Character and Plot"`, `"Phonemic Awareness"`, `"Author's Craft"`
- **Purpose**: Skill categorization, useful for filtering and grouping

### GRADE_LEVEL_SHORT_NAME
- **Type**: String
- **Source**: Direct from input dataset
- **Example**: `"K"`, `"1"`, `"3"`, `"9"`
- **Purpose**: Grade level indicator, used for complexity_band calculation

---

## Structural Components (spaCy)

### actions
- **Type**: Pipe-delimited string
- **Source**: spaCy verb extraction + educational verb dictionary
- **Example**: `"identify|analyze|determine"`
- **Allowed Values**: Any verbs, prioritizing educational verbs (identify, analyze, compare, evaluate, etc.)
- **Empty Value**: `""` (if no verbs found)
- **Extraction Logic**:
  ```python
  # Extract all verbs from skill description
  for token in doc:
      if token.pos_ == 'VERB':
          actions.append(token.lemma_)
  ```
- **Use Cases**:
  - Base skill clustering (skills with same root action)
  - Cognitive demand inference
  - Semantic similarity weighting

### targets
- **Type**: Pipe-delimited string
- **Source**: spaCy noun extraction + literacy target dictionary
- **Example**: `"character|plot|events|story"`
- **Allowed Values**: Any nouns, prioritizing literacy targets (phoneme, character, text, paragraph, etc.)
- **Empty Value**: `""` (if no nouns found)
- **Extraction Logic**:
  ```python
  # Extract nouns, especially educational domain terms
  for token in doc:
      if token.pos_ == 'NOUN':
          targets.append(token.text.lower())
  ```
- **Use Cases**:
  - Identifying what skills operate on (words vs sentences vs texts)
  - Semantic grouping by content focus
  - Filtering redundant skills

### qualifiers
- **Type**: Pipe-delimited string
- **Source**: spaCy adjective and number extraction
- **Example**: `"major|minor|key|basic"`
- **Allowed Values**: Any adjectives or numbers
- **Empty Value**: `""` (if no qualifiers found)
- **Use Cases**:
  - Identifying skill variants (basic vs advanced)
  - Specification extraction
  - Semantic differentiation

### root_verb
- **Type**: String (single word)
- **Source**: spaCy dependency parsing (identifies grammatical root)
- **Example**: `"identify"`, `"analyze"`, `"describe"`
- **Allowed Values**: Any verb
- **Empty Value**: `""` (if sentence has no clear root verb)
- **Extraction Logic**:
  ```python
  # Find root verb using dependency tree
  for token in doc:
      if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
          root_verb = token.lemma_
  ```
- **Use Cases**:
  - Primary action classification
  - Base skill naming
  - Cognitive demand inference

### direct_objects
- **Type**: Pipe-delimited string
- **Source**: spaCy dependency parsing (identifies grammatical objects)
- **Example**: `"elements"`, `"main idea"`, `"characters"`
- **Allowed Values**: Any nouns that are direct objects
- **Empty Value**: `""` (if no direct objects)
- **Extraction Logic**:
  ```python
  # Find direct objects of verbs
  for token in doc:
      if token.dep_ in ['dobj', 'pobj']:
          direct_objects.append(token.text.lower())
  ```
- **Use Cases**:
  - Identifying what action applies to
  - Semantic similarity with target awareness
  - Skill specification extraction

### prepositional_phrases
- **Type**: Pipe-delimited string
- **Source**: spaCy dependency parsing (identifies prepositional phrases)
- **Example**: `"of a story's plot|in a literary text"`
- **Allowed Values**: Prepositional phrases
- **Empty Value**: `""` (if no prepositional phrases)
- **Use Cases**:
  - Context extraction
  - Scope identification (in a sentence vs in a text)
  - Semantic enrichment

### key_concepts
- **Type**: Pipe-delimited string
- **Source**: spaCy extraction + educational domain vocabulary matching
- **Example**: `"identify|plot|story|character"`
- **Allowed Values**: Educational domain terms (verbs from educational_verbs set, nouns from literacy_targets set)
- **Empty Value**: `""` (if no domain terms found)
- **Extraction Logic**:
  ```python
  # Extract only domain-specific terms
  if lemma in self.educational_verbs:
      key_concepts.append(lemma)
  elif lemma in self.literacy_targets:
      key_concepts.append(lemma)
  ```
- **Use Cases**:
  - Semantic search optimization
  - Taxonomy mapping candidate filtering
  - Master concept association

### complexity_markers
- **Type**: Pipe-delimited string
- **Source**: spaCy extraction + complexity marker dictionary
- **Example**: `"basic|simple"`, `"multisyllabic|complex"`
- **Allowed Values**: Complexity indicators (simple, complex, basic, advanced, high-frequency, etc.)
- **Empty Value**: `""` (if no markers found)
- **Use Cases**:
  - Task complexity inference
  - Specification extraction
  - Difficulty classification

---

## Educational Metadata (LLM)

### text_type
- **Type**: Enumerated string
- **Source**: LLM classification (Claude Sonnet 4.5)
- **Allowed Values**:
  - `fictional` - Narrative, literary, imaginative texts (stories, novels, drama)
  - `informational` - Expository, scientific, technical texts (articles, textbooks)
  - `mixed` - Applies to both fiction and non-fiction
  - `not_applicable` - Skill doesn't specify or depend on text type
- **Example Classifications**:
  - `"Identify story plot"` → `fictional`
  - `"Determine main idea in articles"` → `informational`
  - `"Use context clues"` → `mixed`
  - `"Decode CVC words"` → `not_applicable`
- **Use Cases**:
  - Filtering skills by text applicability
  - Master concept categorization
  - Curriculum planning

### text_mode
- **Type**: Enumerated string
- **Source**: LLM classification
- **Allowed Values**:
  - `prose` - Standard written text (default for most reading/writing)
  - `poetry` - Poems, verse, rhyme, stanzas
  - `drama` - Plays, scripts, dialogue, theatrical text
  - `mixed` - Applies to multiple modes
  - `not_applicable` - Doesn't involve text modes
- **Example Classifications**:
  - `"Analyze narrative structure"` → `prose`
  - `"Identify rhyme schemes"` → `poetry`
  - `"Understand stage directions"` → `drama`
  - `"Use punctuation correctly"` → `mixed`
- **Use Cases**:
  - Genre-specific skill identification
  - Specialized instruction planning
  - Scope of applicability

### text_genre
- **Type**: Enumerated string
- **Source**: LLM classification
- **Allowed Values**:
  - `narrative` - Tells a story (character, plot, setting)
  - `expository` - Explains or informs
  - `argumentative` - Persuades, debates, presents claims
  - `procedural` - Gives instructions, how-to
  - `literary` - Fiction, poetry, creative writing
  - `not_applicable` - Doesn't specify genre
- **Example Classifications**:
  - `"Identify story problem and resolution"` → `narrative`
  - `"Determine cause and effect in science text"` → `expository`
  - `"Evaluate author's claims"` → `argumentative`
  - `"Follow multi-step directions"` → `procedural`
- **Use Cases**:
  - Fine-grained genre classification
  - Standard alignment
  - Content-area differentiation

### skill_domain
- **Type**: Enumerated string
- **Source**: LLM classification
- **Allowed Values**:
  - `reading` - Comprehension, decoding, fluency, analysis of text
  - `writing` - Composition, mechanics, process, production
  - `speaking` - Oral language, presentation, discussion
  - `listening` - Comprehension, following directions
  - `language` - Grammar, vocabulary, conventions, syntax
  - `not_applicable` - Cross-domain or unclear
- **Example Classifications**:
  - `"Determine main idea"` → `reading`
  - `"Write narrative with dialogue"` → `writing`
  - `"Present findings orally"` → `speaking`
  - `"Follow oral directions"` → `listening`
  - `"Use correct verb tenses"` → `language`
- **Use Cases**:
  - Primary domain filtering
  - Curriculum strand mapping
  - Standard alignment

### task_complexity
- **Type**: Enumerated string
- **Source**: LLM classification considering skill characteristics and grade level
- **Allowed Values**:
  - `basic` - Foundational skills, identification, recognition, simple application
  - `intermediate` - Application, comparison, interpretation, multi-step processes
  - `advanced` - Synthesis, evaluation, creation, critique, complex reasoning
- **Example Classifications**:
  - `"Recognize letters"` → `basic`
  - `"Compare two characters"` → `intermediate`
  - `"Evaluate author's argument quality"` → `advanced`
- **Determination Factors**:
  - Number of steps required
  - Cognitive processing depth
  - Independence expected
  - Abstractness of concepts
- **Use Cases**:
  - Difficulty classification
  - Learning progression modeling
  - Differentiation planning

### cognitive_demand
- **Type**: Enumerated string
- **Source**: LLM classification using Bloom's Taxonomy
- **Allowed Values** (in order of complexity):
  - `recall` - Retrieve facts, definitions, recognize patterns
  - `comprehension` - Understand meaning, explain, summarize, interpret
  - `application` - Use knowledge in new situations, apply rules
  - `analysis` - Break down, identify relationships, compare/contrast
  - `synthesis` - Combine elements, create new, integrate ideas
  - `evaluation` - Judge, critique, assess quality, make decisions
- **Example Classifications**:
  - `"Identify letters"` → `recall`
  - `"Explain main idea"` → `comprehension`
  - `"Apply decoding strategies"` → `application`
  - `"Analyze character motivations"` → `analysis`
  - `"Create narrative with theme"` → `synthesis`
  - `"Evaluate argument effectiveness"` → `evaluation`
- **Use Cases**:
  - Bloom's taxonomy alignment
  - Assessment design
  - Learning objective classification
  - Cognitive progression tracking

### scope
- **Type**: Enumerated string
- **Source**: LLM classification
- **Allowed Values**:
  - `word` - Operates at word level (vocabulary, word recognition, decoding)
  - `sentence` - Operates at sentence level (sentence structure, grammar)
  - `paragraph` - Operates at paragraph level (main idea, topic sentences)
  - `text` - Operates on whole text (theme, structure, author's purpose)
  - `multi_text` - Compares or synthesizes multiple texts
  - `not_applicable` - Doesn't specify scope
- **Example Classifications**:
  - `"Decode multisyllabic words"` → `word`
  - `"Use correct capitalization in sentences"` → `sentence`
  - `"Identify topic sentence"` → `paragraph`
  - `"Determine theme of story"` → `text`
  - `"Compare themes across two texts"` → `multi_text`
- **Use Cases**:
  - Granularity classification
  - Skill progression within domain
  - Assessment scope definition

---

## Specifications (Rule-Based)

### support_level
- **Type**: Enumerated string
- **Source**: Pattern matching on SKILL_NAME
- **Allowed Values**:
  - `with_support` - With support, assistance, help, adult support
  - `with_prompting` - With prompting, teacher prompting, guidance, cues
  - `with_scaffolding` - With scaffolding, using graphic organizers
  - `independent` - Independently, without support, autonomously (DEFAULT)
  - `not_applicable` - Doesn't specify support
- **Patterns**:
  ```python
  'with_support': ['with support', 'with assistance', 'with help']
  'with_prompting': ['with prompting', 'with teacher prompting', 'with guidance']
  'with_scaffolding': ['with scaffolding', 'using graphic organizers']
  'independent': Default if no patterns match
  ```
- **Example Classifications**:
  - `"With support, identify rhymes"` → `with_support`
  - `"Determine main idea with prompting"` → `with_prompting`
  - `"Identify characters"` → `independent`
- **Use Cases**:
  - Scaffolding specification
  - Learning progression tracking
  - Skill variant identification

### complexity_band
- **Type**: Enumerated string
- **Source**: Grade level mapping
- **Allowed Values**:
  - `K-2` - Kindergarten through Grade 2
  - `3-5` - Grades 3 through 5
  - `6-8` - Grades 6 through 8
  - `9-12` - Grades 9 through 12
  - `Unknown` - Grade level not specified or not mappable
- **Mapping**:
  ```python
  {
    'K', 'PK', 'Pre-K', 'Kindergarten', '1', '2': 'K-2',
    '3', '4', '5': '3-5',
    '6', '7', '8': '6-8',
    '9', '10', '11', '12': '9-12'
  }
  ```
- **Use Cases**:
  - Broad grade-band classification
  - Vertical alignment analysis
  - Learning progression modeling

---

## Quality Metrics

### llm_confidence
- **Type**: Enumerated string
- **Source**: LLM self-assessment
- **Allowed Values**:
  - `high` - Clear, unambiguous skill description
  - `medium` - Some ambiguity or missing context
  - `low` - Significant ambiguity, LLM extraction failed, or fallback used
- **Interpretation**:
  - **high (80%+ target)**: Educational metadata highly reliable
  - **medium (15%)**: Review recommended
  - **low (<5%)**: Manual review required
- **Use Cases**:
  - Quality control
  - Prioritizing manual review
  - Filtering for high-confidence analyses

### extraction_method
- **Type**: String
- **Source**: Automatic based on configuration
- **Allowed Values**:
  - `hybrid_spacy_llm` - Full extraction with all methods
  - `partial` - Some methods disabled (e.g., --no-llm)
  - `spacy_only` - spaCy only, no LLM
  - `fallback` - LLM failed, fallback metadata used
- **Use Cases**:
  - Tracking extraction provenance
  - Identifying which skills need re-extraction
  - Quality assurance

### extraction_timestamp
- **Type**: ISO 8601 timestamp
- **Source**: Automatic at extraction time
- **Example**: `"2025-10-17T14:23:45.123456"`
- **Use Cases**:
  - Tracking extraction date
  - Version control
  - Audit trail

### llm_notes
- **Type**: Free text string
- **Source**: LLM explanation or system warnings
- **Example**: `"Character-focused narrative skill"`, `"Fallback values - LLM extraction failed"`
- **Use Cases**:
  - Debugging extraction issues
  - Understanding edge cases
  - Quality review

---

## Field Relationships

### Correlated Fields

**Cognitive Demand ↔ Task Complexity**
- `recall` / `comprehension` → typically `basic`
- `application` / `analysis` → typically `intermediate`
- `synthesis` / `evaluation` → typically `advanced`

**Text Type ↔ Text Genre**
- `fictional` → `narrative` or `literary`
- `informational` → `expository` or `argumentative`

**Actions ↔ Cognitive Demand**
- `identify`, `recognize`, `recall` → `recall`
- `explain`, `describe`, `summarize` → `comprehension`
- `analyze`, `compare`, `contrast` → `analysis`
- `evaluate`, `critique`, `judge` → `evaluation`

**Scope ↔ Complexity Band**
- K-2: Often `word` or `sentence`
- 3-5: Often `paragraph` or `text`
- 6-8, 9-12: Often `text` or `multi_text`

---

## Validation Rules

### Required Fields (Must Not Be Empty)
- SKILL_ID
- SKILL_NAME
- extraction_method
- extraction_timestamp

### Expected Non-Empty (95%+ target)
- actions
- root_verb
- text_type
- skill_domain
- cognitive_demand

### May Be Empty
- targets (if skill doesn't operate on nouns)
- qualifiers (if no adjectives)
- prepositional_phrases (if simple sentence structure)
- complexity_markers (if no difficulty indicators)
- llm_notes (if no issues)

### Consistency Checks

1. **If text_type = not_applicable, then text_mode should = not_applicable**
2. **If skill_domain = language, scope often = word or sentence**
3. **If support_level ≠ independent, consider if task_complexity should be adjusted**
4. **If cognitive_demand = recall, task_complexity should be basic or intermediate**

---

## Usage in Code

### Loading Metadata

```python
import pandas as pd

# Load enhanced metadata
metadata_df = pd.read_csv('skill_metadata_enhanced_20251017_143022.csv')

# Split pipe-delimited fields into lists
metadata_df['actions_list'] = metadata_df['actions'].str.split('|')
metadata_df['targets_list'] = metadata_df['targets'].str.split('|')
metadata_df['key_concepts_list'] = metadata_df['key_concepts'].str.split('|')
```

### Filtering by Metadata

```python
# Get all reading comprehension skills
reading_skills = metadata_df[
    (metadata_df['skill_domain'] == 'reading') &
    (metadata_df['cognitive_demand'].isin(['comprehension', 'analysis']))
]

# Get high-confidence fictional narrative skills
narrative_skills = metadata_df[
    (metadata_df['text_type'] == 'fictional') &
    (metadata_df['text_genre'] == 'narrative') &
    (metadata_df['llm_confidence'] == 'high')
]
```

### Aggregating Metadata

```python
# Count skills by cognitive demand and complexity band
summary = metadata_df.groupby(['cognitive_demand', 'complexity_band']).size()

# Get most common actions per skill area
metadata_df['actions_list'] = metadata_df['actions'].str.split('|')
metadata_df_exploded = metadata_df.explode('actions_list')
action_counts = metadata_df_exploded.groupby('SKILL_AREA_NAME')['actions_list'].value_counts()
```

---

## Version History

- **v1.0** (2025-10-17): Initial comprehensive 23-field schema with hybrid spaCy+LLM extraction

---

## Future Enhancements

Potential additional fields for future versions:

- **learning_progressions** - Prerequisite and subsequent skills
- **assessment_type** - Formative, summative, diagnostic
- **instructional_strategy** - Recommended teaching approaches
- **text_structure** - Chronological, cause-effect, compare-contrast
- **content_knowledge** - Domain-specific content requirements
- **language_features** - Figurative language, vocabulary level


