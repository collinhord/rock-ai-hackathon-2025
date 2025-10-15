# Science of Reading Mapping Rubric

**Purpose**: Guide LLM-assisted mapping of ROCK skills to Science of Reading taxonomy with quality criteria and developmental appropriateness.

---

## Core Principles

### 1. Developmental Appropriateness
Skills must align with age-appropriate cognitive development:
- **Pre-K (Ages 3-5)**: Oral language, phonological awareness, print concepts
- **K-2 (Ages 5-8)**: Phonics, decoding, foundational reading skills
- **3-5 (Ages 8-11)**: Reading comprehension strategies, vocabulary expansion
- **6-8 (Ages 11-14)**: Complex text analysis, critical thinking
- **9-12 (Ages 14-18)**: Literary analysis, rhetorical devices, advanced composition

### 2. Cognitive Complexity Alignment
Match Bloom's taxonomy levels:
- **Remember/Understand**: Identify, recognize, recall (foundational)
- **Apply**: Use skills in context (developing)
- **Analyze/Evaluate**: Compare, critique, interpret (proficient)
- **Create**: Compose, synthesize (advanced)

### 3. Skill Prerequisite Relationships
Respect learning progressions:
- **Phonological Awareness** → Phonics → Fluency → Comprehension
- **Letter Recognition** → Letter-Sound Correspondence → Blending → Decoding
- **Vocabulary (context)** → Vocabulary (morphology) → Vocabulary (etymology)

---

## Five Pillars of Reading

### Pillar 1: Phonological Awareness
**Definition**: Ability to identify and manipulate sounds in spoken language

**Key Competencies**:
- Rhyme recognition and production
- Syllable segmentation and blending
- Phoneme isolation, blending, segmentation, manipulation
- Onset-rime awareness

**Typical Grade Range**: Pre-K through Grade 2

**Mapping Notes**:
- Focus on ORAL/SPOKEN language (no print involved)
- Watch for confusion with phonics (which involves letters)
- "Sound" often means phoneme in this context

### Pillar 2: Phonics & Decoding
**Definition**: Understanding letter-sound relationships and applying them to read words

**Key Competencies**:
- Letter-sound correspondence (consonants, vowels, digraphs)
- Decoding regular and irregular words
- Syllable types and division patterns
- Morphological awareness (prefixes, suffixes, roots)

**Typical Grade Range**: K through Grade 5 (foundational), ongoing for complex words

**Mapping Notes**:
- Requires PRINT (letters/written text)
- Distinguish encoding (spelling) from decoding (reading)
- Assessment vs. instruction: "identify" may map to instructional foundations

### Pillar 3: Fluency
**Definition**: Accurate, automatic reading with appropriate prosody

**Key Competencies**:
- Rate (words per minute)
- Accuracy (error-free reading)
- Prosody (expression, phrasing, intonation)
- Sight word automaticity

**Typical Grade Range**: Grade 1 through Grade 5 (development), maintained thereafter

**Mapping Notes**:
- Often measured via oral reading assessments
- ROCK "read fluently" skills map here directly
- Don't confuse with comprehension (separate pillar)

### Pillar 4: Vocabulary
**Definition**: Knowledge of word meanings and relationships

**Key Competencies**:
- Word meanings (definitions, multiple meanings)
- Word relationships (synonyms, antonyms, analogies)
- Context clues (inference from surrounding text)
- Morphological analysis (word parts)
- Academic and content-specific vocabulary

**Typical Grade Range**: All grades (ongoing expansion)

**Mapping Notes**:
- Distinguish receptive (understanding) vs. productive (using in writing/speaking)
- Tier 1 (everyday), Tier 2 (academic), Tier 3 (domain-specific)
- Context clues bridge vocabulary and comprehension

### Pillar 5: Comprehension
**Definition**: Understanding, interpreting, and analyzing text

**Key Competencies**:
- Literal comprehension (who, what, when, where)
- Inferential comprehension (why, how, conclusions)
- Text structure (narrative, expository, persuasive)
- Main idea and supporting details
- Author's purpose and perspective
- Critical analysis and evaluation

**Typical Grade Range**: All grades (increasing complexity)

**Mapping Notes**:
- Most complex pillar with many sub-skills
- Distinguish fiction vs. nonfiction comprehension
- Metacognitive strategies (monitoring, clarifying) also fit here

---

## Mapping Quality Criteria

### High Confidence Mapping
**Threshold**: Semantic similarity > 0.75 AND clear SoR alignment

**Characteristics**:
- Direct semantic match (e.g., "blend phonemes" → Phoneme Blending)
- Developmentally appropriate for grade level
- Clear pillar alignment (unambiguous which pillar)
- Skill type matches (receptive vs. productive)
- No significant scope mismatch

**Example**:
```
ROCK: "Blend spoken phonemes into one-syllable words" (Grade K)
Taxonomy: Phonological Awareness > Phoneme Blending
Confidence: HIGH
Rationale: Direct match, grade-appropriate, clear pillar
```

### Medium Confidence Mapping
**Threshold**: Semantic similarity 0.50-0.75 OR reasonable fit with slight adjustment

**Characteristics**:
- Good semantic match but requires interpretation
- Minor developmental level adjustment needed (±1 grade)
- Scope slightly broader or narrower than taxonomy node
- Assessment skill mapping to instructional foundation
- Multiple reasonable alternatives exist

**Example**:
```
ROCK: "Use context clues to determine meaning" (Grade 3)
Taxonomy: Vocabulary > Context Clues OR Comprehension > Inference
Confidence: MEDIUM
Rationale: Bridges two pillars, multiple valid placements
```

### Low Confidence Mapping
**Threshold**: Semantic similarity < 0.50 OR weak SoR alignment

**Characteristics**:
- Poor semantic match
- Developmental mismatch (off by 2+ grades)
- Skill outside literacy scope (e.g., SEL, digital literacy)
- No clear taxonomy node available
- Likely indicates taxonomy gap

**Example**:
```
ROCK: "Collaborate with peers to discuss text digitally" (Grade 8)
Taxonomy: ??? (No clear node)
Confidence: LOW
Rationale: Digital literacy + collaboration (outside SoR scope)
→ FLAG AS TAXONOMY GAP
```

---

## Common Mapping Pitfalls

### Pitfall 1: Confusing Receptive vs. Productive Skills
**Issue**: "Identify main idea" (receptive) vs. "Write a summary" (productive)

**Solution**: 
- Receptive skills (reading/listening) → Reading comprehension nodes
- Productive skills (writing/speaking) → Writing/composition nodes (if taxonomy has them)

**Example**:
- ❌ BAD: "Identify main idea" → Writing > Summarization
- ✅ GOOD: "Identify main idea" → Comprehension > Main Idea

### Pitfall 2: Confusing Grade-Agnostic vs. Grade-Dependent Skills
**Issue**: Imposing grade restrictions where they're not essential

**Solution**:
- **Grade-Agnostic Skills**: Same skill across grades (e.g., "decode word families", "use context clues")
  - Map without grade penalty - the skill competency is the same
  - Grade differences reflect when taught, not skill complexity
- **Grade-Dependent Skills**: Skill complexity tied to grade level (e.g., "analyze theme in grade-level text")
  - Grade alignment matters - skill changes with text complexity
  - Verify developmental appropriateness

**Examples**:
- ✅ GOOD (Grade-Agnostic): "Decode CVC words" (K-2) → Phonics > CVC Decoding (grade doesn't affect mapping)
- ✅ GOOD (Grade-Dependent): "Determine theme in informational text" (Grade 4) → Comprehension > Theme Analysis (grade matters for text complexity)
- ❌ BAD: Penalizing "Use context clues" (Grade 3) → Vocabulary > Context Clues because taxonomy shows Grade 2-5 (skill is grade-agnostic)

### Pitfall 3: Mapping to Wrong Taxonomy Granularity Level
**Issue**: Forcing skills to map at too specific or too broad a level

**Solution**:
- Match skill scope to appropriate taxonomy level
- Broad skills → Parent nodes (e.g., "Comprehension" or "Fluency")
- Specific skills → Granular child nodes (e.g., "Phoneme Segmentation > CVC Words")
- Not all skills need to map to all 6 hierarchy levels
- Map only to the levels that accurately represent the skill's scope

**Examples**:
- ✅ GOOD (Broad): "Read fluently" → Fluency (top-level pillar)
- ✅ GOOD (Specific): "Blend CVC words" → Phonological Awareness > Phoneme Blending > CVC Words
- ✅ GOOD (Mid-level): "Use context clues" → Vocabulary > Context Clues
- ❌ BAD: Forcing "Read fluently" into "Fluency > Rate > Grade 3 Benchmark" (too specific)

### Pitfall 4: Phonological Awareness vs. Phonics Confusion
**Issue**: Both involve sounds, but PA is oral only, phonics involves letters

**Solution**:
- No print mentioned → Phonological Awareness
- Letters/print mentioned → Phonics

**Example**:
- ✅ "Blend spoken phonemes" → Phonological Awareness (no letters)
- ✅ "Decode CVC words" → Phonics (letters involved)

### Pitfall 5: Non-Literacy Skills
**Issue**: Some ROCK skills fall outside reading/literacy scope

**Categories to Watch**:
- **Digital literacy**: Using technology, online research
- **SEL (Social-Emotional)**: Collaboration, empathy, self-regulation
- **Metacognition**: General learning strategies beyond reading
- **Writing conventions**: Handwriting, typing (not reading)

**Solution**: Flag as "Outside SoR Scope" with category label

---

## Mapping Workflow

### Step 1: Analyze ROCK Skill
- What is the core learning objective?
- Is it receptive (input) or productive (output)?
- What is the skill's scope (broad, mid-level, or fine-grained)?
- What grade level? Developmentally appropriate?
- Which SoR pillar(s) does it relate to?

### Step 2: Semantic Search
- Retrieve top 20 taxonomy candidates
- Review for semantic + developmental match

### Step 3: Apply Rubric Criteria
- Check grade alignment
- Check pillar alignment
- Check skill type (receptive/productive)
- Calculate confidence level

### Step 4: Generate Mapping
- Select best match
- Provide rationale using rubric language
- Include 2-3 alternatives
- Flag if confidence is low

### Step 5: Gap Detection (if Low Confidence)
- Why did mapping fail?
- Is this truly a literacy skill?
- What taxonomy node might be missing?
- Suggest potential taxonomy extension

---

## Confidence Decision Tree

```
START
  ↓
Is semantic similarity > 0.75?
  YES → Is grade alignment good? → YES → Is pillar clear? → YES → HIGH
  YES → Is grade alignment good? → YES → Is pillar clear? → NO → MEDIUM
  YES → Is grade alignment good? → NO → Is it ±1 grade? → YES → MEDIUM
  YES → Is grade alignment good? → NO → Is it ±1 grade? → NO → LOW
  NO → Is semantic similarity > 0.50?
    YES → Is there reasonable interpretation? → YES → MEDIUM
    YES → Is there reasonable interpretation? → NO → LOW
    NO → LOW (flag as gap)
```

---

## Validation Checklist

Before finalizing a mapping, verify:

- [ ] Semantic match makes sense (not just keyword overlap)
- [ ] Developmental level is appropriate for grade
- [ ] Pillar assignment is clear and justified
- [ ] Receptive vs. productive distinction is correct
- [ ] No obvious prerequisite violations (e.g., mapping advanced skill before foundational)
- [ ] Rationale explains the mapping decision
- [ ] Alternatives are provided for medium/low confidence
- [ ] Low confidence mappings are flagged with gap analysis

---

## Example Mappings

### Example 1: High Confidence
**ROCK Skill**: "Segment spoken words into individual phonemes" (Grade 1)
**Taxonomy**: Phonological Awareness > Phoneme Segmentation
**Semantic Similarity**: 0.92
**Grade Alignment**: ✓ (Grade 1 appropriate for phoneme segmentation)
**Pillar Alignment**: ✓ (Clear PA skill)
**Confidence**: HIGH
**Rationale**: Direct semantic and developmental match. "Segment...into individual phonemes" maps exactly to Phoneme Segmentation taxonomy node. Grade 1 is appropriate for this foundational PA skill.

### Example 2: Medium Confidence
**ROCK Skill**: "Use knowledge of word families to read unfamiliar words" (Grade 2)
**Taxonomy**: Phonics > Word Families (or) Phonics > Onset-Rime
**Semantic Similarity**: 0.68
**Grade Alignment**: ✓ (Grade 2 appropriate)
**Pillar Alignment**: ✓ (Phonics)
**Confidence**: MEDIUM
**Rationale**: Good match but taxonomy has two potential nodes. Word families could map to either dedicated Word Families node or broader Onset-Rime patterns. Requires judgment call on taxonomy structure.

### Example 3: Low Confidence (Gap Candidate)
**ROCK Skill**: "Use digital tools to research and synthesize information from multiple online sources" (Grade 8)
**Taxonomy**: ??? (No clear node)
**Semantic Similarity**: 0.32
**Grade Alignment**: N/A
**Pillar Alignment**: ✗ (Outside traditional SoR pillars)
**Confidence**: LOW
**Rationale**: This skill combines digital literacy, research strategies, and synthesis—all outside the core Science of Reading framework. Potential gap: Digital Literacy or 21st Century Literacies branch missing from taxonomy.

---

**Last Updated**: October 14, 2025  
**Version**: 1.0  
**Purpose**: Guide enhanced LLM-assisted taxonomy mapping for ROCK skills

