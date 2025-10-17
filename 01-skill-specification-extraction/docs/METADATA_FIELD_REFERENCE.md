# ROCK Skills Metadata Field Reference

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Schema Version**: 1.0 (Baseline), 2.0 (In Development)  
**Scope**: Complete reference for all 23 metadata fields with ELA and Math examples

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Core Identifiers](#core-identifiers)
3. [Structural Components](#structural-components)
4. [Educational Metadata](#educational-metadata)
5. [Specifications](#specifications)
6. [Quality Metrics](#quality-metrics)
7. [Usage Examples](#usage-examples)

---

## Quick Reference

| # | Field Name | Type | Source | ELA Applicable | Math Applicable | Schema v2.0 Changes |
|---|------------|------|--------|----------------|-----------------|---------------------|
| 1 | SKILL_ID | UUID | Direct | ✓ | ✓ | None |
| 2 | SKILL_NAME | String | Direct | ✓ | ✓ | None |
| 3 | SKILL_AREA_NAME | String | Direct | ✓ | ✓ | None |
| 4 | GRADE_LEVEL_SHORT_NAME | String | Direct | ✓ | ✓ | None |
| 5 | actions | Pipe-delimited | spaCy | ✓ | ✓ | Extend dictionary |
| 6 | targets | Pipe-delimited | spaCy | ✓ | ✓ | Extend dictionary |
| 7 | qualifiers | Pipe-delimited | spaCy | ✓ | ✓ | Extend dictionary |
| 8 | root_verb | String | spaCy | ✓ | ✓ | None |
| 9 | direct_objects | Pipe-delimited | spaCy | ✓ | ✓ | None |
| 10 | prepositional_phrases | Pipe-delimited | spaCy | ✓ | ✓ | None |
| 11 | key_concepts | Pipe-delimited | spaCy+Dict | ✓ | ✓ | Extend dictionary |
| 12 | complexity_markers | Pipe-delimited | spaCy+Dict | ✓ | ✓ | Extend dictionary |
| 13 | text_type | Enum | LLM | ✓ | ✗ | Rename to content_type |
| 14 | text_mode | Enum | LLM | ✓ | ✗ | Rename to content_mode |
| 15 | text_genre | Enum | LLM | ✓ | Partial | Keep conditional |
| 16 | skill_domain | Enum | LLM | ✓ | Partial | Extend values |
| 17 | task_complexity | Enum | LLM | ✓ | ✓ | None |
| 18 | cognitive_demand | Enum | LLM | ✓ | ✓ | None |
| 19 | scope | Enum | LLM | ✓ | Partial | Extend values |
| 20 | support_level | Enum | Rules | ✓ | ✓ | None |
| 21 | complexity_band | Enum | Rules | ✓ | ✓ | None |
| 22 | llm_confidence | Enum | LLM | ✓ | ✓ | None |
| 23 | llm_notes | Text | LLM | ✓ | ✓ | None |
| 24 | extraction_method | String | Auto | ✓ | ✓ | None |
| 25 | extraction_timestamp | ISO 8601 | Auto | ✓ | ✓ | None |

---

## Core Identifiers

### 1. SKILL_ID

**Description**: Unique identifier for each skill (UUID format)

**Data Type**: String (UUID)

**Source**: Direct from SKILLS.csv

**ELA Example**:
```
2e1c483a-f6b6-46fa-8e57-e6f8226ab4c4
```

**Math Example**:
```
1c994db4-8307-4d65-8bcc-4d7428ce7006
```

**Usage**:
- Primary key for database joins
- Reference for content alignment
- Tracking skill evolution over time

**Validation**: Must be valid UUID format

---

### 2. SKILL_NAME

**Description**: Full natural language description of the skill

**Data Type**: String (1-500 characters)

**Source**: Direct from SKILLS.csv

**ELA Examples**:
```
"With support, identify some of the sounds of letters"
"Determine the main idea of a text and explain how it is supported by key details"
"Analyze how an author's choices concerning how to structure a text create effects such as mystery, tension, or surprise"
```

**Math Examples**:
```
"Identify examples of the identity properties for addition and multiplication"
"Solve multi-step real-world problems involving addition and subtraction of fractions"
"Apply the Pythagorean Theorem to determine unknown side lengths in right triangles"
```

**Usage**:
- Primary input for all extraction methods
- Display in user interfaces
- Semantic search corpus

---

### 3. SKILL_AREA_NAME

**Description**: High-level categorization of skill content

**Data Type**: String

**Source**: Direct from SKILLS.csv

**ELA Examples**:
```
"Alphabetic Knowledge"
"Character and Plot"
"Author's Craft"
"Vocabulary Acquisition"
"Writing Process"
```

**Math Examples**:
```
"Algebraic Thinking"
"Whole Numbers: Addition and Subtraction"
"Fraction Concepts and Operations"
"Data Representation and Analysis"
"Geometry: Shapes and Properties"
```

**Usage**:
- Grouping skills by topic
- Filtering search results
- Curriculum organization

---

### 4. GRADE_LEVEL_SHORT_NAME

**Description**: Target grade level for skill

**Data Type**: String

**Source**: Direct from SKILLS.csv

**Possible Values**: `PK`, `K`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`

**ELA Example**: 
- Grade 3 skill: `"3"`
- High school skill: `"11"`

**Math Example**:
- Kindergarten skill: `"K"`
- Algebra skill: `"8"`

**Usage**:
- Determining complexity_band
- Age-appropriate content filtering
- Learning progression analysis

---

## Structural Components (spaCy)

### 5. actions

**Description**: Verb phrases describing cognitive or physical actions

**Data Type**: Pipe-delimited string

**Source**: spaCy verb extraction + educational verb dictionary

**Extraction Method**: Identifies all verbs, prioritizes educational verbs

**ELA Examples**:
```
"identify|analyze"
"determine|explain"
"compare|contrast"
"evaluate|critique"
```

**Math Examples**:
```
"solve|apply"
"calculate|estimate"
"construct|measure"
"prove|justify"
```

**Common ELA Verbs**:
- Read/analyze: identify, recognize, determine, explain, describe
- Comprehension: understand, interpret, summarize, paraphrase
- Analysis: analyze, compare, contrast, evaluate, critique
- Creation: write, compose, develop, create, produce

**Common Math Verbs**:
- Computation: solve, calculate, compute, evaluate, simplify
- Construction: construct, draw, graph, plot, measure
- Reasoning: prove, justify, explain, verify, check
- Application: apply, model, represent, translate

**Usage**:
- Base skill clustering by similar actions
- Cognitive demand inference
- Semantic similarity matching

---

### 6. targets

**Description**: Noun phrases representing learning objects or concepts

**Data Type**: Pipe-delimited string

**Source**: spaCy noun extraction + domain vocabulary

**ELA Examples**:
```
"character|plot|events|story"
"main|idea|text|details"
"author|choices|structure|effects"
"vocabulary|context|meaning"
```

**Math Examples**:
```
"properties|addition|multiplication"
"fractions|denominators"
"triangle|sides|angles"
"data|graph|mean|median"
```

**Common ELA Targets**:
- Story elements: character, plot, setting, theme, conflict
- Text structures: paragraph, sentence, word, text, passage
- Literary devices: metaphor, simile, imagery, symbolism
- Writing elements: idea, organization, voice, conventions

**Common Math Targets**:
- Numbers: number, digit, fraction, decimal, percent
- Algebra: variable, expression, equation, inequality
- Geometry: shape, angle, line, triangle, circle, polygon
- Data: data, graph, chart, table, mean, median, mode

**Usage**:
- Identifying skill focus
- Content domain classification
- Redundancy detection

---

### 7. qualifiers

**Description**: Adjectives and modifiers that specify scope or characteristics

**Data Type**: Pipe-delimited string

**Source**: spaCy adjective and number extraction

**ELA Examples**:
```
"key|major"
"basic|simple"
"complex|multifaceted"
"literary|informational"
```

**Math Examples**:
```
"equivalent|equal"
"multi-step|complex"
"rational|irrational"
"positive|negative"
```

**Usage**:
- Identifying skill variants
- Complexity assessment
- Specification extraction

---

### 8. root_verb

**Description**: Primary grammatical verb of the sentence

**Data Type**: String (single word)

**Source**: spaCy dependency parsing

**ELA Examples**:
```
"identify"
"analyze"
"write"
"explain"
```

**Math Examples**:
```
"solve"
"calculate"
"apply"
"construct"
```

**Usage**:
- Primary action classification
- Base skill naming
- Cognitive demand inference (combined with other fields)

---

### 9. direct_objects

**Description**: Grammatical objects of action verbs

**Data Type**: Pipe-delimited string

**Source**: spaCy dependency parsing

**ELA Examples**:
```
"elements" (from "identify elements of plot")
"idea" (from "determine main idea")
"effects" (from "analyze effects")
```

**Math Examples**:
```
"examples" (from "identify examples")
"problems" (from "solve problems")
"theorem" (from "apply theorem")
```

**Usage**:
- Understanding action targets
- Semantic similarity
- Skill comparison

---

### 10. prepositional_phrases

**Description**: Phrases providing context and scope

**Data Type**: Pipe-delimited string

**Source**: spaCy dependency parsing

**ELA Examples**:
```
"of a story's plot"
"in a literary text"
"with evidence from the text"
"in multiple texts"
```

**Math Examples**:
```
"of the identity properties"
"for addition and multiplication"
"in right triangles"
"with fractions"
```

**Usage**:
- Context extraction
- Scope identification
- Semantic enrichment

---

### 11. key_concepts

**Description**: Domain-specific educational terms

**Data Type**: Pipe-delimited string

**Source**: spaCy + educational vocabulary matching

**ELA Examples**:
```
"identify|plot|story|character"
"comprehension|main|idea|text"
"analyze|author|structure"
```

**Math Examples**:
```
"identify|properties|addition|multiplication"
"solve|fractions|operations"
"theorem|triangle|calculate"
```

**Usage**:
- Semantic search optimization
- Taxonomy mapping
- Master concept association

---

### 12. complexity_markers

**Description**: Words indicating skill difficulty or complexity

**Data Type**: Pipe-delimited string

**Source**: spaCy + complexity marker dictionary

**ELA Examples**:
```
"basic"
"multisyllabic|complex"
"advanced|literary"
```

**Math Examples**:
```
"simple|basic"
"multi-step|complex"
"abstract"
```

**Common Markers**:
- Simple: simple, basic, foundational, elementary
- Intermediate: intermediate, grade-level, standard
- Advanced: complex, advanced, sophisticated, abstract, multi-step

**Usage**:
- Task complexity inference
- Difficulty classification
- Learning progression sequencing

---

## Educational Metadata (LLM)

### 13. text_type

**Description**: Type of text the skill operates on

**Data Type**: Enumerated string

**Source**: LLM classification (Claude Sonnet 4.5)

**Possible Values**:
- `fictional` - Narrative, literary, imaginative texts
- `informational` - Expository, scientific, technical texts
- `mixed` - Applies to both fiction and non-fiction
- `not_applicable` - Doesn't specify or depend on text type

**ELA Examples**:
```
"Identify story plot" → fictional
"Determine main idea in articles" → informational
"Use context clues" → mixed
"Decode CVC words" → not_applicable
```

**Math Examples**:
```
"Solve word problems" → not_applicable (default)
"Interpret graphs in scientific articles" → informational (rare)
Most Math skills → not_applicable
```

**Schema v2.0 Change**: Rename to `content_type`, add Math-appropriate values:
- ELA: fictional, informational, mixed, not_applicable
- Math: symbolic, visual, concrete, verbal, mixed, not_applicable

**Usage** (ELA):
- Filtering skills by text applicability
- Curriculum planning by genre
- Content discovery

**Usage** (Math):
- Currently limited (95%+ are not_applicable)
- v2.0 will capture representation type

---

### 14. text_mode

**Description**: Mode or form of text

**Data Type**: Enumerated string

**Source**: LLM classification

**Possible Values**:
- `prose` - Standard written text
- `poetry` - Poems, verse, rhyme
- `drama` - Plays, scripts, dialogue
- `mixed` - Multiple modes
- `not_applicable` - Doesn't involve text modes

**ELA Examples**:
```
"Analyze narrative structure" → prose
"Identify rhyme schemes" → poetry
"Understand stage directions" → drama
"Use punctuation correctly" → mixed
```

**Math Examples**:
```
Most skills → not_applicable
```

**Schema v2.0 Change**: Rename to `content_mode`:
- ELA: prose, poetry, drama, mixed, not_applicable
- Math: symbolic_only, visual_only, mixed, not_applicable

---

### 15. text_genre

**Description**: Genre or purpose of text

**Data Type**: Enumerated string

**Source**: LLM classification

**Possible Values**:
- `narrative` - Tells a story
- `expository` - Explains or informs
- `argumentative` - Persuades, presents claims
- `procedural` - Gives instructions
- `literary` - Fiction, poetry, creative
- `not_applicable` - Doesn't specify genre

**ELA Examples**:
```
"Identify story problem" → narrative
"Determine cause and effect" → expository
"Evaluate author's claims" → argumentative
"Follow multi-step directions" → procedural
```

**Math Examples**:
```
"Follow steps to solve equation" → procedural (rare)
Most skills → not_applicable
```

**Schema v2.0**: Keep as conditional field, mostly ELA-relevant

---

### 16. skill_domain

**Description**: Primary educational domain

**Data Type**: Enumerated string

**Source**: LLM classification

**Current Values** (ELA-focused):
- `reading` - Comprehension, decoding, fluency
- `writing` - Composition, mechanics, process
- `speaking` - Oral language, presentation
- `listening` - Comprehension, following directions
- `language` - Grammar, vocabulary, conventions
- `not_applicable` - Cross-domain or unclear

**ELA Examples**:
```
"Determine main idea" → reading
"Write narrative with dialogue" → writing
"Present findings orally" → speaking
"Follow oral directions" → listening
"Use correct verb tenses" → language
```

**Math Examples** (Current, v1.0):
```
Most skills → not_applicable (insufficient domain categories)
```

**Schema v2.0 Extension**:
Add Math-specific domains:
- `number_operations` - Arithmetic, computation
- `algebraic_thinking` - Patterns, equations, variables
- `geometry` - Shapes, measurement, spatial reasoning
- `data_analysis` - Statistics, probability, graphs
- `measurement` - Units, conversions, estimation

**Math Examples** (v2.0):
```
"Solve addition problems" → number_operations
"Identify patterns in sequences" → algebraic_thinking
"Calculate area of rectangle" → geometry
"Interpret bar graphs" → data_analysis
```

---

### 17. task_complexity

**Description**: Overall complexity of the skill task

**Data Type**: Enumerated string

**Source**: LLM classification considering multiple factors

**Possible Values**:
- `basic` - Foundational, identification, recognition
- `intermediate` - Application, comparison, multi-step
- `advanced` - Synthesis, evaluation, creation

**Determination Factors**:
- Number of steps required
- Cognitive processing depth
- Independence expected
- Abstractness of concepts

**ELA Examples**:
```
"Recognize letters" → basic
"Compare two characters" → intermediate
"Evaluate argument quality" → advanced
```

**Math Examples**:
```
"Count to 10" → basic
"Solve two-step equations" → intermediate
"Prove geometric theorems" → advanced
```

**Grade Level Correlation**:
- K-2: Mostly basic, some intermediate
- 3-5: Mix of basic and intermediate
- 6-8: Mostly intermediate, some advanced
- 9-12: Mix of intermediate and advanced

**Usage**:
- Difficulty classification
- Learning progression modeling
- Differentiation planning

---

### 18. cognitive_demand

**Description**: Cognitive complexity based on Bloom's Taxonomy

**Data Type**: Enumerated string

**Source**: LLM classification

**Possible Values** (in order of complexity):
- `recall` - Retrieve facts, recognize patterns
- `comprehension` - Understand meaning, explain, summarize
- `application` - Use knowledge in new situations
- `analysis` - Break down, identify relationships
- `synthesis` - Combine elements, create new
- `evaluation` - Judge, critique, assess quality

**ELA Examples**:
```
"Identify letters" → recall
"Explain main idea" → comprehension
"Apply decoding strategies" → application
"Analyze character motivations" → analysis
"Create narrative with theme" → synthesis
"Evaluate argument effectiveness" → evaluation
```

**Math Examples**:
```
"Recall multiplication facts" → recall
"Understand place value" → comprehension
"Apply Pythagorean Theorem" → application
"Analyze data patterns" → analysis
"Create mathematical model" → synthesis
"Evaluate solution strategies" → evaluation
```

**Action Verb Mapping**:
- Recall: identify, recognize, recall, list, name
- Comprehension: explain, describe, summarize, interpret
- Application: apply, solve, use, demonstrate, calculate
- Analysis: analyze, compare, contrast, examine
- Synthesis: create, design, construct, develop, compose
- Evaluation: evaluate, judge, critique, assess, justify

**Usage**:
- Bloom's taxonomy alignment
- Assessment design
- Cognitive progression tracking

---

### 19. scope

**Description**: Granularity level at which skill operates

**Data Type**: Enumerated string

**Source**: LLM classification

**Current Values** (ELA-focused):
- `word` - Operates at word level
- `sentence` - Operates at sentence level
- `paragraph` - Operates at paragraph level
- `text` - Operates on whole text
- `multi_text` - Compares multiple texts
- `not_applicable` - Doesn't specify scope

**ELA Examples**:
```
"Decode multisyllabic words" → word
"Use correct capitalization" → sentence
"Identify topic sentence" → paragraph
"Determine theme of story" → text
"Compare themes across texts" → multi_text
```

**Math Examples** (Current, v1.0):
```
Most skills → not_applicable (scope values are ELA-specific)
```

**Schema v2.0 Extension**:
Make domain-conditional with Math-specific values:
- ELA: word, sentence, paragraph, text, multi_text, not_applicable
- Math: number, expression, equation, problem, proof, multi_step, not_applicable

**Math Examples** (v2.0):
```
"Identify place value" → number
"Simplify algebraic expression" → expression
"Solve linear equation" → equation
"Solve word problem" → problem
"Prove theorem" → proof
"Solve multi-step problems" → multi_step
```

---

## Specifications (Rule-Based)

### 20. support_level

**Description**: Level of instructional support specified

**Data Type**: Enumerated string

**Source**: Pattern matching on SKILL_NAME

**Possible Values**:
- `with_support` - With support, assistance, help
- `with_prompting` - With prompting, teacher prompting
- `with_scaffolding` - With scaffolding, using graphic organizers
- `independent` - Independently, without support (DEFAULT)
- `not_applicable` - Doesn't specify support

**Detection Patterns**:
```python
patterns = {
    'with_support': ['with support', 'with assistance', 'with help'],
    'with_prompting': ['with prompting', 'with teacher prompting', 'with guidance'],
    'with_scaffolding': ['with scaffolding', 'using graphic organizers'],
    'independent': ['independently', 'without support', 'autonomously'],
}
```

**ELA Examples**:
```
"With support, identify rhymes" → with_support
"Determine main idea with prompting" → with_prompting
"Identify characters" → independent (default)
```

**Math Examples**:
```
"With assistance, count to 20" → with_support
"Solve equations using graphic organizer" → with_scaffolding
"Calculate area independently" → independent
"Multiply fractions" → independent (default)
```

**Usage**:
- Scaffolding specification
- Learning progression tracking
- Skill variant identification
- Differentiation planning

---

### 21. complexity_band

**Description**: Broad grade band for developmental level

**Data Type**: Enumerated string

**Source**: Deterministic mapping from GRADE_LEVEL_SHORT_NAME

**Possible Values**:
- `K-2` - Kindergarten through Grade 2
- `3-5` - Grades 3 through 5
- `6-8` - Grades 6 through 8
- `9-12` - Grades 9 through 12
- `Unknown` - Grade level not specified

**Mapping**:
```python
grade_map = {
    'PK': 'K-2', 'K': 'K-2', '1': 'K-2', '2': 'K-2',
    '3': '3-5', '4': '3-5', '5': '3-5',
    '6': '6-8', '7': '6-8', '8': '6-8',
    '9': '9-12', '10': '9-12', '11': '9-12', '12': '9-12',
}
```

**ELA & Math Examples**: Same mapping for both domains

**Usage**:
- Broad grade-band classification
- Vertical alignment analysis
- Learning progression modeling
- Standards grouping

---

## Quality Metrics

### 22. llm_confidence

**Description**: LLM's self-assessed confidence in classification

**Data Type**: Enumerated string

**Source**: LLM response

**Possible Values**:
- `high` - Clear, unambiguous skill description
- `medium` - Some ambiguity or missing context
- `low` - Significant ambiguity or unclear classification

**Interpretation**:
- **high (target 90%+)**: Metadata highly reliable, ready for production
- **medium (target ~10%)**: Review recommended for critical applications
- **low (target <5%)**: Manual review required

**Quality Indicators for High Confidence**:
- Skill description is clear and specific
- Classification criteria well-defined
- Grade level aligns with skill complexity
- No contradictory indicators

**Quality Indicators for Low Confidence**:
- Vague skill description
- Multiple possible interpretations
- Unusual or ambiguous terminology
- Insufficient context

**Usage**:
- Quality control filtering
- Prioritizing manual review
- Production readiness assessment
- Continuous improvement targeting

---

### 23. llm_notes

**Description**: LLM explanation or reasoning for classifications

**Data Type**: Free text string

**Source**: LLM response

**Purpose**:
- Explain classification rationale
- Note ambiguities or edge cases
- Provide context for review
- Debug extraction issues

**ELA Example (High Confidence)**:
```
"This skill focuses on character analysis in narrative fiction. The action 'analyze' 
combined with 'motivations' indicates analysis-level cognitive demand. Task complexity 
is intermediate as it requires examining multiple character traits and behaviors."
```

**ELA Example (Low Confidence)**:
```
"Ambiguous whether this skill applies to fictional or informational texts. The skill 
description doesn't specify text type, and 'analyze structure' could apply to either. 
Marked text_type as mixed due to lack of specificity."
```

**Math Example**:
```
"This is a mathematics skill focused on algebraic thinking, not literacy. Students 
investigate identity properties (0 for addition, 1 for multiplication) through 
exploration and application. Not applicable for literacy-specific fields."
```

**Usage**:
- Understanding classification decisions
- Identifying systematic issues
- Training data for future improvements
- Expert validation context

---

### 24. extraction_method

**Description**: Method used for extraction

**Data Type**: String

**Source**: Automatic based on configuration

**Possible Values**:
- `hybrid_spacy_llm` - Full extraction with all methods (standard)
- `partial` - Some methods disabled
- `spacy_only` - spaCy only, no LLM
- `fallback` - LLM failed, fallback metadata used

**Usage**:
- Tracking extraction provenance
- Quality assurance
- Identifying skills needing re-extraction

---

### 25. extraction_timestamp

**Description**: When metadata was extracted

**Data Type**: ISO 8601 timestamp

**Source**: Automatic at extraction time

**Example**: `"2025-10-17T14:23:45.123456"`

**Usage**:
- Version control
- Audit trail
- Identifying stale metadata
- Re-extraction scheduling

---

## Usage Examples

### Example 1: Querying by Educational Metadata

```python
import pandas as pd

# Load metadata
df = pd.read_csv('all_skills_metadata.csv')

# Find Grade 3-5 reading comprehension skills at analysis level
skills = df[
    (df['complexity_band'] == '3-5') &
    (df['skill_domain'] == 'reading') &
    (df['cognitive_demand'] == 'analysis') &
    (df['llm_confidence'] == 'high')
]

print(f"Found {len(skills)} matching skills")
print(skills[['SKILL_NAME', 'SKILL_AREA_NAME', 'task_complexity']])
```

### Example 2: Semantic Search with Metadata Filtering

```python
# Find skills about fractions at intermediate complexity
fraction_skills = df[
    (df['targets'].str.contains('fraction', case=False, na=False)) &
    (df['task_complexity'] == 'intermediate') &
    (df['CONTENT_AREA'] == 'Mathematics')
]

# Group by cognitive demand
print(fraction_skills.groupby('cognitive_demand').size())
```

### Example 3: Cross-Domain Skill Comparison

```python
# Compare structural differences between ELA and Math
ela = df[df['CONTENT_AREA'] == 'English Language Arts']
math = df[df['CONTENT_AREA'] == 'Mathematics']

print("=== Action Verb Comparison ===")
print(f"ELA - Most common actions:")
ela_actions = ela['actions'].str.split('|').explode()
print(ela_actions.value_counts().head(10))

print(f"\nMath - Most common actions:")
math_actions = math['actions'].str.split('|').explode()
print(math_actions.value_counts().head(10))
```

### Example 4: Quality Assessment

```python
# Assess extraction quality
print("=== Quality Metrics ===")
print(f"High confidence rate: {(df['llm_confidence'] == 'high').mean():.1%}")
print(f"Field completeness:")
print(f"  actions: {(df['actions'] != '').mean():.1%}")
print(f"  cognitive_demand: {(df['cognitive_demand'] != '').mean():.1%}")
print(f"  task_complexity: {(df['task_complexity'] != '').mean():.1%}")

# Flag skills needing review
low_conf = df[df['llm_confidence'] == 'low']
print(f"\nSkills needing review: {len(low_conf)}")
low_conf.to_csv('skills_for_review.csv', index=False)
```

---

## Field Dependencies and Relationships

### Correlated Fields

**Cognitive Demand ↔ Task Complexity**:
- `recall` / `comprehension` → typically `basic`
- `application` / `analysis` → typically `intermediate`
- `synthesis` / `evaluation` → typically `advanced`

**Text Type ↔ Text Genre** (ELA):
- `fictional` → `narrative` or `literary`
- `informational` → `expository` or `argumentative`

**Actions ↔ Cognitive Demand**:
- identify, recognize, recall → `recall`
- explain, describe, summarize → `comprehension`
- analyze, compare, evaluate → `analysis`
- create, design, construct → `synthesis`

**Scope ↔ Complexity Band**:
- K-2: Often `word` or `sentence`
- 3-5: Often `paragraph` or `text`
- 6-8, 9-12: Often `text` or `multi_text`

---

## Version History

**v1.0 (Current)**: 
- 23 fields optimized for ELA
- Limited Math applicability for text-specific fields
- Baseline schema for cross-domain analysis

**v2.0 (In Development)**:
- Rename text_* fields to content_*
- Extend skill_domain with Math domains
- Extend scope with Math-specific values
- Add Math representation and operation types
- Target: 20-25 fields with full cross-domain support

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Next Update**: After schema v2.0 design complete  
**Maintained By**: ROCK Skills Analysis Team

