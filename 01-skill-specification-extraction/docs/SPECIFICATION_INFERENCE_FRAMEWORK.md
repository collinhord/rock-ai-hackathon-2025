# Specification Inference Framework

**Version**: 1.0  
**Date**: October 17, 2025  
**Status**: Design Phase - Awaiting Phase 1.4 Data  
**Purpose**: Define inferred specification fields derived via deterministic rules

---

## Overview

This framework defines a **third layer of metadata** beyond spaCy extraction and LLM classification: **Inferred Specifications** derived through deterministic logic applied to existing metadata.

### Three-Layer Metadata Architecture

```
Layer 1: Structural Extraction (spaCy)
├── Fast, deterministic, linguistic parsing
├── Cost: Free (local processing)
└── Output: actions, targets, qualifiers, root_verb, etc.

Layer 2: Educational Classification (LLM)
├── Context-aware pedagogical metadata
├── Cost: ~$0.003 per skill
└── Output: cognitive_demand, task_complexity, skill_domain, etc.

Layer 3: Specification Inference (Rules) ← NEW
├── Higher-level semantic classification
├── Cost: Free (deterministic logic)
└── Output: text_dependent, skill_type, transfer_potential, etc.
```

---

## Candidate Inferred Specification Fields

### Tier 1: High-Value Specifications (Implement First)

#### 1. text_dependent
**Definition**: Whether the skill requires specific reading material vs. general application

**Values**: `true | false`

**Business Value**: 
- **Content Licensing**: Skills with text_dependent=false don't require purchasing texts
- **Assessment Design**: Independent skills can be assessed without content restrictions
- **Curriculum Planning**: Mix of text-dependent and independent skills

**Examples**:
- TRUE: "Analyze the structure of the informational text" (needs specific text)
- TRUE: "Compare themes across two stories" (needs specific stories)
- FALSE: "Capitalize the pronoun 'I' in sentences" (any sentence works)
- FALSE: "Determine the missing angle in a triangle" (any triangle works)
- FALSE: "Use commas to separate items in a series" (general rule)

**Detection Logic**:
```python
def infer_text_dependent(metadata):
    """
    TRUE if skill requires specific reading material.
    FALSE if skill is generally applicable.
    """
    # Strong TRUE indicators
    if metadata['scope'] in ['text', 'multi_text']:
        return True
    
    if ('analyze' in metadata['actions'] or 'interpret' in metadata['actions']) and \
       ('text' in metadata['targets'] or 'passage' in metadata['targets']):
        return True
    
    # Check for "the text", "this story" in skill description
    specific_text_patterns = [
        'the text', 'the passage', 'the story', 'this poem',
        'the article', 'the selection', 'a given text'
    ]
    if any(pattern in metadata['SKILL_NAME'].lower() for pattern in specific_text_patterns):
        return True
    
    # Strong FALSE indicators
    if metadata['skill_domain'] == 'language':  # Grammar/conventions
        return False
    
    if metadata['CONTENT_AREA'] == 'Mathematics':
        # Most Math skills are not text-dependent
        # Exception: word problems with specific scenarios
        return 'problem' in metadata['targets'] and 'story' in metadata['SKILL_NAME'].lower()
    
    if metadata['root_verb'] in ['capitalize', 'punctuate', 'spell', 'format']:
        return False
    
    # Default: ambiguous
    return None  # Flag for manual review
```

**Validation Questions**:
- What % of ELA skills are text_dependent? (Predict: 60-70%)
- What % of Math skills are text_dependent? (Predict: <5%)
- Do content libraries align with text_dependent skills?
- Does this help prioritize curriculum development?

---

#### 2. skill_type
**Definition**: Primary cognitive operation required by the skill

**Values**: `analytical | procedural | generative | comparative`

**Business Value**:
- **Assessment Design**: Balance different skill types on tests
- **Instructional Strategy**: Different teaching approaches per type
- **Adaptive Learning**: Procedural skills good for drill-and-practice
- **Learning Progressions**: Sequence from procedural → analytical → generative

**Examples**:
- **analytical**: "Analyze how the author's word choice creates mood"
- **procedural**: "Multiply two-digit numbers using the standard algorithm"
- **generative**: "Write a narrative with dialogue and descriptive details"
- **comparative**: "Compare and contrast two characters from different stories"

**Detection Logic**:
```python
def infer_skill_type(metadata):
    """
    Classify primary skill operation type.
    """
    # Generative: Creating new content
    if metadata['root_verb'] in ['write', 'create', 'compose', 'design', 'develop', 'produce']:
        return 'generative'
    
    # Comparative: Comparing multiple items
    if metadata['root_verb'] in ['compare', 'contrast'] or \
       metadata['scope'] == 'multi_text' or \
       'compare' in metadata['actions']:
        return 'comparative'
    
    # Analytical: Deep analysis, interpretation, evaluation
    if metadata['cognitive_demand'] in ['analysis', 'evaluation', 'synthesis'] and \
       metadata['text_dependent'] == True:
        return 'analytical'
    
    # Procedural: Rule/algorithm application (default for Math, language conventions)
    if metadata['cognitive_demand'] in ['recall', 'application'] or \
       metadata['CONTENT_AREA'] == 'Mathematics' or \
       metadata['skill_domain'] == 'language':
        return 'procedural'
    
    # Default
    return 'procedural'
```

**Validation Questions**:
- Is the distribution reasonable across content areas?
- Do K-2 skills skew procedural? (Expected)
- Do 9-12 skills skew analytical/generative? (Expected)
- Does this inform instructional resource needs?

---

#### 3. transfer_potential
**Definition**: How readily the skill generalizes across contexts

**Values**: `low | medium | high`

**Business Value**:
- **Core Curriculum**: High-transfer skills are essential across subjects
- **Intervention Priority**: Focus on high-transfer foundational skills
- **Cross-Curricular Planning**: Identify skills used in multiple domains
- **ROI Analysis**: High-transfer skills yield greater student benefit

**Examples**:
- **high**: "Use commas correctly" (applies to all writing contexts)
- **high**: "Solve linear equations" (applies to many problem types)
- **medium**: "Identify main idea" (strategy works across texts but requires comprehension)
- **medium**: "Calculate area of rectangles" (generalizes within geometry)
- **low**: "Analyze symbolism in *The Great Gatsby*" (text-specific)
- **low**: "Interpret data in the graph on page 42" (context-specific)

**Detection Logic**:
```python
def infer_transfer_potential(metadata):
    """
    Assess generalizability across contexts.
    """
    # High transfer: Procedural rules that apply broadly
    if metadata['skill_type'] == 'procedural' and \
       metadata['text_dependent'] == False and \
       metadata['skill_domain'] in ['language', 'not_applicable']:
        return 'high'
    
    # High transfer: Fundamental Math operations
    if metadata['CONTENT_AREA'] == 'Mathematics' and \
       metadata['complexity_band'] in ['K-2', '3-5'] and \
       metadata['cognitive_demand'] in ['recall', 'application']:
        return 'high'
    
    # Low transfer: Text-dependent analytical skills
    if metadata['text_dependent'] == True and \
       metadata['skill_type'] == 'analytical':
        return 'low'
    
    # Medium transfer: Strategies and approaches
    return 'medium'
```

**Validation Questions**:
- Do high-transfer skills appear in state standards more frequently?
- Are these skills prioritized in curriculum maps?
- Does transfer potential correlate with assessment frequency?
- Should high-transfer skills get more instructional time?

---

### Tier 2: Moderate-Value Specifications (Evaluate in Phase 2.1)

#### 4. content_required
**Definition**: Level of content specificity needed to assess the skill

**Values**: `specific | generic | none`

**Relationship**: Closely related to text_dependent but more granular

**Examples**:
- **specific**: "Analyze Atticus's character development in *To Kill a Mockingbird*"
- **generic**: "Identify the main idea in an informational text"
- **none**: "Use correct capitalization for proper nouns"

**Business Value**: TBD - May be redundant with text_dependent

---

#### 5. context_independent
**Definition**: Can be assessed without additional context

**Values**: `true | false`

**Relationship**: Inverse of text_dependent with slight nuance

**Business Value**: TBD - May be redundant with text_dependent

---

#### 6. receptive_productive
**Definition**: Direction of information flow

**Values**: `receptive | productive | both`

**Examples**:
- **receptive**: Reading, listening, analyzing
- **productive**: Writing, speaking, creating
- **both**: "Respond to questions about the text"

**Business Value**: 
- Modality planning (balance input vs. output)
- Instructional design (explicit teaching per modality)

**Evaluation Needed**: Is this more useful than skill_domain categorization?

---

### Tier 3: Explore After Data Analysis (Phase 1.4)

#### 7. multi_step
**Values**: `true | false`

**Detection**: Look for "multi-step", "several", "multiple" keywords

**Business Value**: Complexity assessment, time allocation

---

#### 8. collaborative_potential
**Values**: `individual | pair | group | flexible`

**Detection**: Keywords like "discuss", "collaborate", "share"

**Business Value**: Group work planning

**Evaluation Needed**: How often do skills specify collaboration? Is this useful?

---

#### 9. real_world_connection
**Values**: `true | false`

**Detection**: "real-world", "everyday", "authentic" keywords

**Business Value**: Engagement, relevance

**Evaluation Needed**: Do standards reliably indicate this?

---

#### 10. technology_enhanced
**Values**: `required | optional | not_applicable`

**Detection**: "digital", "online", "calculator", "software" keywords

**Business Value**: Technology planning, device requirements

---

#### 11. assessment_format
**Values**: `selected_response | constructed_response | performance | portfolio`

**Inference**: Based on root_verb and skill_type

**Business Value**: Assessment design, item bank organization

---

#### 12. prerequisite_intensity
**Values**: `low | medium | high`

**Inference**: Combination of cognitive_demand + complexity_band + grade_level

**Business Value**: Learning progression modeling, intervention planning

---

## Specification Evaluation Framework

### Evaluation Criteria

For each candidate specification, evaluate:

#### 1. Utility Dimensions

**Instructional Value**:
- Does this inform teaching practice?
- Would teachers use this to plan lessons?
- Does it clarify instructional approach?

**Assessment Value**:
- Does this guide assessment design?
- Would assessment developers find this useful?
- Does it help balance test blueprints?

**Content Development Value**:
- Does this guide content creation?
- Would content teams use this for gap analysis?
- Does it inform resource allocation?

**System Integration Value**:
- Would users filter/search by this field?
- Does it enable new product features?
- Does it improve recommendations/matching?

**Analytics Value**:
- Does this enable meaningful data analysis?
- Would research teams use this?
- Does it inform strategic decisions?

#### 2. Feasibility Assessment

**Detection Accuracy**:
- Can we write deterministic rules with >85% accuracy?
- Are edge cases manageable?
- Can experts validate this reliably?

**Rule Complexity**:
- How complex is the detection logic?
- How many dependencies on other fields?
- How maintainable are the rules?

**Computational Cost**:
- Processing time per skill?
- Can this run at scale?

#### 3. Prioritization Matrix

| Specification | Instructional | Assessment | Content Dev | System | Analytics | Feasibility | **PRIORITY** |
|---------------|---------------|------------|-------------|--------|-----------|-------------|--------------|
| text_dependent | HIGH | HIGH | HIGH | HIGH | HIGH | HIGH | **TIER 1** |
| skill_type | HIGH | HIGH | MED | HIGH | HIGH | HIGH | **TIER 1** |
| transfer_potential | HIGH | MED | HIGH | MED | HIGH | MED | **TIER 1** |
| content_required | MED | LOW | HIGH | LOW | MED | HIGH | TIER 2 |
| context_independent | LOW | LOW | MED | LOW | LOW | HIGH | TIER 2 |
| receptive_productive | MED | MED | LOW | MED | MED | HIGH | TIER 2 |
| multi_step | MED | MED | LOW | LOW | MED | HIGH | TIER 3 |
| collaborative_potential | MED | LOW | LOW | LOW | LOW | MED | TIER 3 |
| real_world_connection | LOW | LOW | LOW | LOW | MED | LOW | TIER 3 |
| technology_enhanced | MED | LOW | MED | LOW | LOW | MED | TIER 3 |
| assessment_format | LOW | HIGH | LOW | MED | MED | MED | TIER 3 |
| prerequisite_intensity | MED | LOW | MED | LOW | HIGH | MED | TIER 3 |

---

## Implementation Roadmap

### Phase 2.1: Specification Evaluation

**After Phase 1.4 data analysis complete**, conduct formal evaluation:

1. **Review actual extraction data** for patterns that validate or refute specification utility
2. **Stakeholder interviews**: 
   - Teachers (instructional value)
   - Assessment designers (assessment value)
   - Content developers (content value)
   - Product managers (system value)
   - Researchers (analytics value)

3. **Prototype detection rules** for Tier 1 specifications
4. **Test accuracy** on 200-skill validation sample
5. **Document findings** in specification evaluation report

### Phase 2.2: Implement Tier 1 Only

**For schema v2.0**, implement only validated Tier 1 specifications:
- text_dependent
- skill_type  
- transfer_potential

**Rationale**: Start with high-value, high-confidence fields. Add others incrementally based on usage data.

### Phase 2.3: Create Inference Engine

Build `specification_inference_engine.py` with:
- Modular rule functions (one per specification)
- Unit tests per rule
- Confidence scoring
- Edge case flagging
- Rule versioning (can update rules independently of extraction)

### Phase 3.2: Validate Inferred Specifications

Include Tier 1 specifications in 200-skill expert validation:
- Measure rule accuracy
- Identify systematic errors
- Refine rules based on expert feedback
- Document edge cases

### Phase 5: Iterative Enhancement

**After production deployment**:
1. Monitor usage patterns (which specifications are actually used?)
2. Collect user feedback on specification accuracy
3. A/B test Tier 2/3 specifications with subset of users
4. Promote useful specifications to production
5. Deprecate unused specifications

---

## Success Metrics for Inferred Specifications

### Accuracy Targets

- **text_dependent**: ≥90% accuracy (critical for business value)
- **skill_type**: ≥85% accuracy (subjective, expect more variance)
- **transfer_potential**: ≥80% accuracy (somewhat subjective)

### Usage Metrics

Track after deployment:
- % of API queries that filter by inferred specifications
- User satisfaction scores for search/filter results
- Frequency of specification-based features in product

### Business Impact Metrics

- Reduction in content licensing costs (text_dependent=false skills)
- Improvement in curriculum alignment (using transfer_potential)
- Increased assessment quality (balanced skill_types)

---

## Open Questions for Phase 2.1 Evaluation

### text_dependent
1. What % of ELA skills are actually text-dependent vs. general strategies?
2. Do text-dependent skills correlate with content availability?
3. Should we have gradations (e.g., text-dependent_level: high|medium|low)?
4. How does this align with standards' "complexity" indicators?

### skill_type
1. Is 4-way classification sufficient or too coarse?
2. Should we allow multiple types (e.g., analytical + comparative)?
3. Does distribution vary meaningfully by grade band?
4. How stable is this classification across validators?

### transfer_potential
1. Does transfer_potential correlate with standards appearing in multiple states?
2. Should this be continuous (0-100 scale) vs. categorical?
3. How does cognitive demand interact with transfer potential?
4. Can we validate against research on transfer of learning?

### General
1. Which specifications are redundant with existing fields?
2. Which specifications have low inter-rater reliability?
3. Which specifications enable new product features?
4. What's the minimum viable specification set for v2.0?

---

## Next Steps

**Immediate** (After Phase 1.4 Analysis):
1. Review actual extraction results for specification patterns
2. Validate or refute predictions about field distributions
3. Identify which specifications have clearest detection signals

**Phase 2.1** (Specification Evaluation):
1. Conduct stakeholder interviews on specification utility
2. Prototype detection rules for top 3 specifications
3. Test accuracy on sample skills
4. Document evaluation findings

**Phase 2.2** (Schema Design):
1. Incorporate validated specifications into schema v2.0
2. Document detection rules with examples
3. Plan iterative enhancement for Tier 2/3 specs

**Phase 2.3** (Implementation):
1. Build specification_inference_engine.py
2. Unit test each rule
3. Integrate with extraction pipeline

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Next Review**: After Phase 1.4 analysis complete (~4 hours)  
**Status**: Awaiting extraction completion to validate specifications

