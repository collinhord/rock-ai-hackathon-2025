# ROCK Skills Compound Architectural Problem: Problem Statement

**Document Status**: Analysis and Problem Definition (Solution-Neutral)

**Prepared For**: ROCK Skills List Advancement Team

**Date**: October 2025

---

## Executive Summary

The ROCK Skills List faces a **compound architectural problem** with two critical, interrelated dimensions:

### Problem 1: Horizontal Fragmentation (Cross-State Redundancy)
Skills are derived from state-specific educational standards rather than from science-based master competencies. This results in 5-15+ conceptually identical skills (one per state/standard) for each underlying learning objective, with no metadata connecting them.

### Problem 2: Vertical Granularity Mismatch (Assessment vs. Instruction)
ROCK skills are optimized for periodic assessment (Star) but too broad and coarse for daily instructional use (P&I). This forces P&I teams to bypass ROCK entirely and build custom skills from scratch.

### The Business Constraint
ROCK cannot be modified because Star Assessments (primary revenue source) depend on current structure, and years of historical student data are tied to existing skills. Any changes risk data integrity and business continuity.

### Combined Impact
- **Horizontal**: Curriculum developers cannot easily discover all skills teaching a given concept (60-75% redundancy)
- **Vertical**: P&I teams cannot use ROCK for daily instruction (too broad, periodic assessment focus)
- **Business Lock-In**: Cannot fix either problem by modifying ROCK (Star dependency)
- **Result**: Complete ecosystem fragmentation—ROCK serves assessment only, P&I builds parallel infrastructure

### Root Cause
ROCK's data model prioritizes standards compliance (WHERE skills came from) over learning science (WHAT students are learning). There is no taxonomic metadata layer connecting skills to evidence-based frameworks like the Science of Reading—which could solve both problems by providing:
1. Master concepts to group fragmented ROCK skills (horizontal)
2. Decomposition structure for P&I objectives (vertical)
3. Bridge layer that preserves ROCK immutability (business constraint)

---

## 1. The Problem in Detail

### 1.1 How Skills Enter ROCK Today

**Current Process**:
1. State legislature publishes educational standards (e.g., Texas TEKS, California CCSS)
2. ROCK team analyzes standards and creates skills aligned to them
3. Skills inherit state-specific language, grade assignments, and scope from standards
4. Skills are stored in ROCK with alignment to their originating standards
5. **No step links skills back to underlying science-based competencies**

**Result**: The same evidence-based learning objective appears 8-15 times across states, with no metadata indicating they teach the same thing.

### 1.2 The Science-Based Master Skills

Educational research defines core competencies students must master, independent of state politics:

**Science of Reading (Literacy)**:
- Hierarchical taxonomy: Strands → Pillars → Domains → Skill Areas → Skill Sets → Skill Subsets
- Evidence-based components: Phonological Awareness, Phonics, Fluency, Vocabulary, Comprehension, Executive Function
- Grade-independent: Focuses on cognitive/linguistic constructs, not grade-level standards
- Research-grounded: Based on decades of reading science

**Mathematics Learning Progressions**:
- Number sense development trajectories
- Algebraic thinking progressions
- Spatial reasoning and geometric understanding
- Grounded in cognitive development research

**These frameworks represent WHAT students learn**. State standards represent HOW states choose to document and organize those learnings.

### 1.3 The State Legislative Filter

Each state:
- Interprets master concepts through its own lens
- Uses different terminology and vocabulary
- Assigns concepts to different grade levels
- Combines or splits concepts differently
- Adds state-specific priorities or constraints

**Example**: Phoneme Blending (Science of Reading Master Concept)

| State | Standard Code | Description | Grade | Focus/Constraint |
|-------|--------------|-------------|-------|------------------|
| CCSS | RF.K.2c | "Blend two to three phonemes into recognizable words" | K | Specifies 2-3 phonemes |
| Texas | K.2.A.iv | "Blend spoken phonemes to form one-syllable words" | K | Emphasizes spoken, one-syllable |
| California | RF.K.2.c | "Orally blend two to three phonemes into words" | K | Adds "orally" qualifier |
| Virginia | K.4 | "Blend sounds to make one-syllable words" | K | Uses "sounds" not "phonemes" |
| Ohio | RF.K.2.c | "Orally produce single-syllable words by blending sounds" | K | Adds "produce" action |

All five standards teach **the same Science of Reading competency**, but with state-specific language.

### 1.4 ROCK Skill Derivation and Fragmentation

ROCK creates skills aligned to these standards, resulting in:

| ROCK Skill Name | State | Grade | Skill Area | SKILL_ID |
|----------------|-------|-------|------------|----------|
| Blend phonemes to form words | CCSS | K | Blending and Segmenting | [GUID-1] |
| Blend spoken phonemes into one-syllable words | TX | K | Phonological Awareness | [GUID-2] |
| Orally blend 2-3 phonemes into recognizable words | CA | K | Foundational Skills | [GUID-3] |
| Blend sounds to make one-syllable words | VA | K | Blending and Segmenting | [GUID-4] |
| Orally produce words by blending sounds | OH | K | Phonics and Word Recognition | [GUID-5] |

**Problem Analysis**:
- ✅ Each skill accurately represents its source standard
- ✅ Skills have unique IDs, descriptions, and standard alignments
- ❌ **No field indicates these five skills teach the same master competency**
- ❌ **No reference to "Phoneme Blending" from Science of Reading taxonomy**
- ❌ **No metadata linking them as conceptually equivalent**
- ❌ **Different SKILL_AREA_NAME values (even though same concept)**

**Critical Gap**: ROCK has no taxonomic metadata connecting skills to evidence-based master competencies.

### 1.5 The Vertical Granularity Problem: ROCK vs. P&I

**The Fundamental Mismatch:**

ROCK and P&I (Practice & Instruction) products serve the same users (teachers, students) but operate in different temporal and granular contexts:

| Dimension | ROCK Skills | P&I Needs |
|-----------|-------------|-----------|
| **Purpose** | Periodic assessment | Daily instruction |
| **Grain Size** | Broad competency | Micro-objective |
| **Temporal Cycle** | Weekly/monthly/semester | 1-3 day lessons |
| **Optimization** | Measurable, assessable | Teachable, scaffoldable |
| **Alignment** | State standards | Curriculum publishers |
| **Example** | "Blend phonemes to form words" | "Day 1: Blend 2-phoneme words (/c/+/at/)" |

**Example: Phoneme Blending**

**ROCK Skill** (Assessment-Optimized):
- "Blend spoken phonemes to form one-syllable words"
- Broad enough to assess periodically
- Covers entire concept in one skill
- Grade K, measured every few weeks

**P&I Instructional Needs** (Curriculum-Aligned):
- Day 1: Blend 2 phonemes (CVC words: cat, dog, sit)
- Day 2: Blend 3 phonemes (CVCC words: list, fast)
- Day 3: Blend initial consonant blends (CCVC: stop, plan)
- Day 4: Blend with digraphs (ship, chat)
- Day 5: Blend complex patterns (split, shrimp)

**The Gap**: One ROCK skill must decompose into 5-10 daily lesson objectives for P&I.

**The Business Lock-In:**

ROCK cannot be made finer-grained because:
- **Star Assessment Dependency**: Star products (primary revenue) depend on current ROCK structure
- **Historical Data**: Millions of student records tied to existing broad skills
- **Assessment Validity**: Fine-grained skills would compromise psychometric properties
- **Data Integrity**: Any changes risk breaking historical trend analysis

**The Result:**

P&I teams cannot use ROCK skills for daily instruction:
- ROCK skills too broad to support 1-3 day lesson cycles
- ROCK not aligned to specific curriculum publishers (McGraw-Hill, Houghton Mifflin, etc.)
- ROCK optimized for measurement, not teaching

**P&I teams bypass ROCK entirely:**
- Build custom skill frameworks from scratch
- Duplicate development of skill infrastructure
- No reuse of ROCK metadata, relationships, or data
- Ecosystem fragmentation: Assessment (ROCK) and Instruction (P&I) operate in parallel with no integration

**The Expert-Driven Problem:**

P&I teams create skills through subject matter expertise:
- Curriculum specialists review educational materials
- Domain experts identify learning objectives
- Team consensus determines skill granularity

**Systematic Issues:**
- **Inconsistent Granularity**: No objective methodology (Math: 47 objectives for fractions; Reading: 23 for comparable unit)
- **Coverage Gaps**: Advanced topics omitted, review skills inconsistent, cross-curricular connections missing
- **Curriculum Misalignment**: Skills reflect expert interpretation, not classroom reality
- **No External Validation**: Missing field testing, professional curriculum design, market validation
- **Cannot Scale**: Expert-driven approach cannot cover 50+ curriculum publishers, thousands of pacing guides

---

## 2. Quantifying the Compound Problem

### 2.1 Estimated Redundancy

Based on sample analysis of ROCK schemas (literacy skills only):

**Master Concept Examples and ROCK Skill Counts**:

| Science of Reading Concept | Estimated ROCK Skills | States Represented | Grade Spread |
|---------------------------|----------------------|-------------------|--------------|
| Phoneme Blending | 8-12 | TX, CA, CCSS, VA, OH, FL, etc. | K-2 |
| Phoneme Segmentation | 8-12 | Multiple states | K-2 |
| Context Clues for Word Meaning | 10-15 | Most states | 2-6 |
| Main Idea Identification | 12-18 | Most states | 2-8 |
| Text Structure Analysis | 10-14 | Most states | 3-7 |
| Inferencing | 15-20 | Most states | 2-10 |
| Author's Purpose | 10-15 | Most states | 3-9 |
| Decoding Multisyllabic Words | 12-16 | Most states | 2-5 |

**Redundancy Ratio Estimate**:
- If ROCK has ~1,200 distinct literacy skills (hypothetical)
- And ~150 master Science of Reading competencies cover K-12 literacy
- Average fragmentation: **8 ROCK skills per master concept**
- **Conceptual redundancy: 60-75%**

### 2.2 Example: Detailed Fragmentation Analysis

**Master Concept**: Using Context to Determine Word Meaning (Vocabulary/Contextual Word Learning)

**Fragmentation Pattern**:

| Education Authority | Grade | ROCK Skill Description (Abbreviated) | Differences |
|---------------------|-------|--------------------------------------|-------------|
| Texas TEKS | 3 | Use context to determine relevant meaning | "relevant meaning" emphasis |
| California CCSS | 4 | Use context as clue to meaning of word or phrase | "clue" framing, adds "phrase" |
| Common Core | 4-5 | Use context (definitions, examples) as clue | Specifies context types |
| Ohio | 5 | Determine meaning using context clues | "context clues" terminology |
| Virginia | 3 | Use context to clarify meaning | "clarify" framing |
| Florida | 4 | Determine or clarify meaning using context | Combines "determine" and "clarify" |
| New York | 5 | Use context to determine meaning of unknown words | Specifies "unknown words" |
| Pennsylvania | 4 | Identify and correctly use context clues | "identify and use" action pair |

**Total ROCK Skills for This One Concept**: ~12-15 across all states and grade levels

**What's Missing**: 
- No field tagging these skills as "Vocabulary: Contextual Word Learning"
- No reference to Science of Reading taxonomy node
- No metadata indicating conceptual equivalence

### 2.3 Data Volume Impact

**Hypothetical ROCK Skill Inventory** (based on typical state standard sets):

| Content Area | Total ROCK Skills | Unique Master Concepts (Est.) | Redundancy Ratio |
|--------------|------------------|-------------------------------|------------------|
| ELA Literacy | 1,200 | 150-200 | 6-8x |
| Mathematics | 900 | 120-150 | 6-7.5x |
| **Total** | **2,100** | **270-350** | **~6-8x** |

**Interpretation**: For every 6-8 ROCK skills, there is likely one underlying master concept, with the rest being state/grade variants.

### 2.3 The Compound Effect: How Both Problems Multiply

**Scenario: Building a Context Clues Unit for P&I**

**Step 1: Search for ROCK Skills (Horizontal Problem)**
- Curriculum developer searches "context clues"
- Finds 12-15 fragmented ROCK skills across TX, CA, OH, VA, CCSS, etc.
- Must manually determine which are conceptually equivalent
- **Time lost**: 2-3 hours analyzing redundant skills

**Step 2: Realize ROCK Too Broad (Vertical Problem)**
- Each ROCK skill covers entire "context clues" concept
- P&I needs 5-7 daily lesson objectives:
  - Day 1: Definition clues
  - Day 2: Synonym clues
  - Day 3: Antonym clues
  - Day 4: Example clues
  - Day 5: Combining multiple clue types
- ROCK cannot support this decomposition
- **Result**: Must build from scratch, bypassing ROCK entirely

**Step 3: No Reuse (Business Constraint)**
- Cannot modify ROCK to fix either problem (Star dependency)
- Cannot add finer granularity (assessment validity)
- Cannot add taxonomy metadata (schema changes too risky)
- **Result**: Complete bypass, duplicate infrastructure

**Total Impact:**
- Searched 12-15 redundant ROCK skills (horizontal waste)
- None usable for daily instruction anyway (vertical gap)
- Built custom P&I framework from scratch (ecosystem fragmentation)
- **Efficiency loss**: ~80-90% compared to ideal integrated system

---

## 3. Architectural Analysis

### 3.1 Current ROCK Schema Structure

**What Exists**:
```
skills.csv:
  - SKILL_ID (PK)
  - SKILL_NAME
  - SKILL_SHORT_NAME
  - SKILL_AREA_NAME (loose grouping, not hierarchical)
  - CONTENT_AREA_NAME
  - GRADE_LEVEL_NAME
  - DOK_LEVEL
  - SKILL_STATUS
  
standard-skills.csv:
  - SKILL_ID (FK to skills)
  - STANDARD_ID (FK to standards)
  - STANDARD_SET_NAME
  - EDUCATION_AUTHORITY
  - RELATIONSHIP_TYPE
  
standards.csv:
  - STANDARD_ID (PK)
  - STANDARD_CODE
  - STANDARD_DESCRIPTION
  - EDUCATION_AUTHORITY
  - DOMAIN_NAME
  - DOMAIN_GROUP_NAME
```

**What's Missing**:
```
(NO TABLE OR FIELD FOR:)
  - Master Skill Taxonomy Reference
  - Science of Reading / Learning Progression IDs
  - Cognitive Construct Tags
  - Conceptual Equivalence Mappings
  - Prerequisite/Progression Relationships (learning-science-based)
```

### 3.2 Comparison to Science of Reading Taxonomy

**Science of Reading Structure** (from provided taxonomy):
```csv
Strand, Pillar, Domain, Skill Area, Skill Set, Skill Subset, Annotation
Active Self-Regulation, Executive Function Skills, Core Executive Processes, Cognitive Flexibility, Strategy Shifting, Switching Strategies Based on Task Demands, "The ability to shift between strategies..."
```

**Key Features**:
- ✅ **Hierarchical**: Clear parent-child relationships (6 levels deep)
- ✅ **Evidence-Based**: Grounded in reading research
- ✅ **Grade-Independent**: Focuses on competencies, not standards
- ✅ **Comprehensive**: 1,140 rows covering cognitive, metacognitive, linguistic domains
- ✅ **Consistent**: No state-specific variations
- ✅ **Annotated**: Examples and behavioral descriptions for each skill

**ROCK Skills Structure**:
- ❌ **Flat**: SKILL_AREA_NAME is a flat grouping, not a hierarchy
- ❌ **Standards-Derived**: Tied to state political documents, not learning science
- ❌ **Grade-Specific**: Each skill locked to a default grade level
- ❌ **Fragmented**: State-specific variations with no equivalence metadata
- ❌ **No Annotations**: Limited guidance on what competencies mean cognitively

### 3.3 The Missing Taxonomic Layer

**What a Solution Would Provide** (conceptually):

```
ROCK Skill:
  - SKILL_ID: 4e12f61e-e69f-e311-9503-005056801da1
  - SKILL_NAME: "Use knowledge of frequently occurring affixes..."
  - SKILL_AREA_NAME: "Word Meaning and Reference Materials"
  
  [MISSING METADATA:]
  - MASTER_SKILL_ID: SoR-Vocabulary-MorphologicalAnalysis-002
  - SOR_TAXONOMY_PATH: "Decoding and Word Recognition > Morphological Awareness > Affix Knowledge"
  - COGNITIVE_CONSTRUCTS: ["morphological-awareness", "vocabulary-development"]
  - EQUIVALENT_SKILLS: [list of conceptually identical skill IDs from other states]
  - PREREQUISITE_SKILLS: [skills that should be mastered first, based on learning science]
  - PROGRESSION_LEVEL: 2 (indicating where in developmental sequence)
```

**With This Metadata**:
- ✅ Could query: "Show me all skills teaching morphological awareness"
- ✅ Could group data across state variants
- ✅ Could build learning progressions programmatically
- ✅ Could align content to Science of Reading framework
- ✅ Could identify coverage gaps in master competencies

---

## 4. Impact Analysis: The Compound Effect

### 4.1 Impact on Curriculum Development (Both Problems)

**Horizontal Problem Impact**:
- Cannot discover all skills teaching a concept (60-75% redundancy)
- Must manually identify conceptual equivalents across states
- Duplicate content development for similar skills

**Vertical Problem Impact**:
- ROCK skills too broad for daily instruction
- Must decompose each ROCK skill into 5-10 P&I objectives
- No systematic decomposition methodology

**Combined Impact - Current Workflow Challenge**:
1. Curriculum developer wants to create content for "phoneme blending"
2. Searches ROCK skills for "blend phoneme"
3. Finds 5 skills
4. Misses 7 additional skills using "blend sound" or "oral blend" terminology
5. Doesn't realize some skills are conceptually identical across states
6. Either duplicates work or creates incomplete coverage

**With Taxonomic Metadata**:
1. Search Science of Reading taxonomy node: "Phoneme Blending"
2. Get all 12 ROCK skills linked to that node automatically
3. See which are state variants (equivalent) vs. developmental progressions
4. Make informed decisions about content reuse and adaptation

**Estimated Efficiency Gain**: 30-50% reduction in search and analysis time

### 4.2 Impact on Product Development

**Current Challenge**:
- Product team building adaptive system to recommend "next skills"
- System can only traverse standard-to-skill alignments
- Cannot identify conceptually related skills across states
- Cannot build learning progressions grounded in cognitive science
- Adaptive recommendations limited by lack of skill relationships

**With Taxonomic Metadata**:
- System can recommend conceptually related skills
- Can follow evidence-based learning progressions
- Can adapt across state configurations seamlessly
- Can fill knowledge gaps using Science of Reading framework

**Estimated Value**: Enables next-generation personalization features

### 4.3 Impact on Analytics and Research

**Current Challenge**:
- Researcher wants to analyze student mastery of "inferencing" across Renaissance products
- Must manually identify all "inferencing" skills by reading descriptions
- No way to distinguish state variants from developmental levels
- Cannot aggregate data at master-concept level
- Cross-state comparisons require extensive manual coding

**With Taxonomic Metadata**:
- Query all skills tagged with "inferencing" construct
- Automatically group by conceptual equivalence
- Aggregate data at Science of Reading taxonomy level
- Run analyses aligned with learning science frameworks

**Estimated Value**: Enables research-grade data aggregation and validation

### 4.4 Impact on Educators

**Current Challenge**:
- Teacher searching for intervention content for struggling reader
- Knows student needs work on "phonemic awareness" (from diagnostic)
- Searches ROCK, finds scattered skills with unclear relationships
- Uncertain which skills are redundant vs. progressive
- Difficult to build coherent intervention plan

**With Taxonomic Metadata**:
- Search by Science of Reading taxonomy: "Phonological Awareness > Phoneme Blending"
- See all relevant skills grouped by equivalence and progression
- Understand developmental sequence (beginner → advanced)
- Select appropriate skills for student's level

**Estimated Value**: Improved educator experience and student outcomes

---

## 5. Root Cause Analysis

### 5.1 Historical Context

**Why ROCK Skills Are Standards-Driven**:
- Renaissance products must demonstrate standards alignment for state adoptions
- Schools and districts procure based on standards compliance
- Standards are the contractual/regulatory requirement
- ROCK was designed to prove alignment to accountability frameworks

**This Made Sense When**:
- Standards-based reform was the primary driver (1990s-2010s)
- Cross-state comparison was less important
- Adaptive/personalized systems were less sophisticated
- Learning science taxonomies were less mature/available

### 5.2 Why the Problem Persists

**Technical Challenges**:
- Large existing skill inventory (~2,000+ skills)
- Complex migration to add taxonomic metadata
- No off-the-shelf taxonomy for all content areas
- Standards alignment still required (can't remove)

**Organizational Challenges**:
- Skills owned by multiple product teams
- No single authority for taxonomic tagging
- Competing priorities (new features vs. technical debt)
- Requires cross-functional coordination (curriculum, research, engineering)

**Knowledge Challenges**:
- Requires deep expertise in learning science frameworks
- Mapping skills to Science of Reading requires curriculum specialists
- Conceptual equivalence is sometimes subjective
- Developmental progressions require research validation

### 5.3 Strategic Implications

**The Trade-Off**:
- **Current State**: Optimized for standards compliance, poor for learning science alignment
- **Desired State**: Support both standards compliance AND science-based taxonomy

**The Risk**:
- Competitors adopting taxonomy-driven architectures gain advantages in:
  - Adaptive personalization
  - Research-grounded product claims
  - Educator-friendly content discovery
  - Cross-state/international scalability

---

## 6. Stakeholder Perspectives

### 6.1 Curriculum Designers
**Pain Points**:
- Cannot easily find all skills for a concept
- Must manually map equivalences
- Learning progressions are implicit, not formalized
- Content reuse across similar skills is manual

**Needs**:
- Query skills by evidence-based construct
- See skill relationships (equivalent, prerequisite, progression)
- Understand coverage gaps in master frameworks

### 6.2 Product Managers
**Pain Points**:
- Feature requests requiring skill relationships blocked
- Adaptive systems cannot leverage learning progressions
- Cross-state product parity difficult to achieve
- Cannot market "Science of Reading aligned" with data to back it

**Needs**:
- Programmatic access to skill relationships
- Science-based taxonomy integration for product claims
- Cross-state skill equivalence for feature parity

### 6.3 Data Scientists & Researchers
**Pain Points**:
- Cannot aggregate data by master constructs
- Cross-state analyses require manual skill coding
- Validation against learning science frameworks not possible
- Research publications require extensive manual work

**Needs**:
- Taxonomic metadata for grouping and aggregation
- Evidence-based framework references for validation
- Conceptual equivalence metadata for cross-state studies

### 6.4 Educators
**Pain Points**:
- Searching by concept (e.g., "phonemic awareness") yields incomplete results
- Unclear which skills are redundant vs. progressive
- Difficult to match diagnostics to interventions
- Learning progressions not visible

**Needs**:
- Search by familiar educational concepts
- Clear skill progressions aligned with learning stages
- Transparency on what skills teach conceptually

---

## 7. The Science of Reading Taxonomy as an Example

The provided **Science of Reading - Literacy Skills Taxonomy.csv** exemplifies what a master taxonomy provides:

**Structure**:
- 1,140 rows covering comprehensive literacy competencies
- 6-level hierarchy: Strand → Pillar → Domain → Skill Area → Skill Set → Skill Subset
- Annotations with concrete examples for each skill

**Example Entry**:
```
Strand: "Decoding and Word Recognition"
Pillar: "Morphological Awareness"
Domain: "Morphological Analysis"
Skill Area: "Affix Knowledge"
Skill Set: "Prefix/Suffix Identification"
Skill Subset: "Identify and define common prefixes (un-, re-, pre-)"
Annotation: "The ability to recognize and understand meaning of common prefixes..."
```

**Value for ROCK**:
- Could link ROCK skills to specific taxonomy nodes
- Would reveal conceptual redundancy instantly
- Would formalize learning progressions
- Would enable Science of Reading alignment claims backed by data

**Challenge**:
- Requires mapping ~1,200 literacy skills to ~200 relevant taxonomy nodes
- Subjective decisions on best-fit mapping
- Maintenance as taxonomy evolves

---

## 8. Problem Statement Summary

### The Core Problem
**ROCK skills are derived from state standards rather than science-based master competencies, resulting in massive redundancy with no taxonomic metadata to connect conceptually equivalent skills or ground them in evidence-based frameworks.**

### Quantified Impact
- **60-75% conceptual redundancy** across ROCK skill inventory
- **8-15 state-specific skills per master concept** (average)
- **Manual effort** required for all cross-state skill discovery and equivalence mapping
- **Blocked features** requiring skill relationships or learning progressions

### Root Cause
**Architectural Decision**: ROCK prioritizes standards compliance (WHERE skills came from) over learning science (WHAT students are learning). No taxonomic metadata layer exists to connect skills to evidence-based frameworks.

### Why It Matters Now
- **Learning Science Renaissance**: Science of Reading and evidence-based frameworks now mainstream
- **Product Differentiation**: Competitors adopting taxonomy-driven architectures
- **Adaptive Systems**: Next-gen features require skill relationships
- **Research Validation**: Increasingly important to ground products in learning science

### Success Criteria for a Solution (Conceptual)
A solution would enable:
1. ✅ Query all ROCK skills teaching a master competency (e.g., "phoneme blending")
2. ✅ Identify conceptually equivalent skills across states
3. ✅ Discover formalized learning progressions grounded in evidence
4. ✅ Aggregate data at master-concept level for research
5. ✅ Link ROCK skills to Science of Reading taxonomy nodes
6. ✅ Maintain standards alignment while adding science-based layer

---

## 9. Next Steps for the ROCK Skills List Advancement Team

### Immediate Actions
1. **Validate Problem Quantification**: Sample-analyze ROCK skills to confirm redundancy estimates
2. **Identify Priority Domains**: Start with high-impact areas (e.g., K-2 foundational reading)
3. **Engage Stakeholders**: Share problem statement with curriculum, product, and research leaders
4. **Assess Taxonomies**: Evaluate Science of Reading and other evidence-based frameworks for suitability

### Future Exploration
1. **Pilot Mapping**: Map 50-100 skills to Science of Reading taxonomy as proof of concept
2. **Schema Design**: Design taxonomic metadata fields/tables for ROCK database
3. **Tooling**: Explore AI/NLP approaches for semi-automated skill-to-taxonomy mapping
4. **Governance**: Establish process for maintaining taxonomic metadata as skills evolve

**This document focuses on problem definition and analysis. Solution design is a separate effort.**

---

## Appendix: References

- **ROCK Schemas**: `/rock_schemas/` directory (skills.csv, standards.csv, standard-skills.csv, domains.csv, domain-groups.csv, standard-sets.csv)
- **Science of Reading Taxonomy**: `Science of Reading - Literacy Skills Taxonomy.csv` (1,140 rows, 6-level hierarchy)
- **Related Documentation**: 
  - `schema-overview.md`: Technical schema reference
  - `master-skill-fragmentation.md`: Visual diagram of the problem
- **ROCK Skills Agent**: `agents/work-agents/rock-skills-agent.txt`: Expert consultation resource

