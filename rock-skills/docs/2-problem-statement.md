# ROCK Skills Compound Architectural Problem: Problem Statement

**Document Status**: Analysis and Problem Definition (Solution-Neutral)

**Prepared For**: ROCK Skills List Advancement Team

**Date**: October 2025

---

## Executive Summary

The ROCK Skills List faces a **compound architectural problem** with three interrelated failure modes preventing ecosystem-wide integration.

### Problem 1: Horizontal Fragmentation (Cross-State Redundancy)
Skills derive from state-specific standards rather than science-based master competencies, creating 6-8x redundancy (8-15 conceptually identical skills per learning objective) with no metadata connecting them.

### Problem 2: Vertical Granularity Mismatch
ROCK skills are simultaneously **too broad** and **too specific** for P&I instructional use:
- **Too Broad**: One ROCK skill covers entire competency; P&I needs 5-10 micro-objectives for daily lessons
- **Too Specific**: Skills are state-locked; P&I cannot scale content across 8-15 state variants

### The Business Constraint
ROCK cannot be modified—Star Assessments depend on current structure, and years of historical data are tied to existing skills. Schema changes risk data integrity and business continuity.

### Quantified Impact
- **60-75% conceptual redundancy** across skill inventory
- **8-15 state-specific skills per master concept** (horizontal + vertical-specific)
- **5-10 micro-objectives needed per ROCK skill** for daily instruction (vertical-broad)
- **P&I bypass**: Instructional teams build parallel infrastructure, losing ROCK metadata/relationships
- **80-90% efficiency loss** compared to integrated system

### Root Cause
ROCK prioritizes **standards compliance** (WHERE skills came from) over **learning science** (WHAT students learn). No taxonomic metadata layer exists to connect skills to evidence-based frameworks—which would solve all dimensions:
1. Master concepts to group fragmented skills (horizontal)
2. State variant mappings to enable P&I content scaling (vertical-specific)
3. Hierarchical decomposition for micro-objectives (vertical-broad)
4. Bridge layer preserving ROCK immutability (business constraint)

---

## 1. Problem Analysis

### 1.1 The State Legislative Filter

**Science-Based Master Competency** (e.g., Phoneme Blending from Science of Reading)
↓ **State Standards Process**
**8-15 State-Specific Variants** (TX, CA, CCSS, VA, OH, FL, etc.)

Each state interprets master concepts through its own lens:
- Different terminology ("phonemes" vs. "sounds", "blend" vs. "oral blend")
- Different grade assignments (K vs. K-1)
- Different scope qualifiers ("one-syllable", "2-3 phonemes", "CVC words")
- Different action verbs ("blend", "produce", "orally combine")

**Example**: Phoneme Blending appears in ROCK as:

| ROCK Skill Name | State | Key Differences |
|----------------|-------|-----------------|
| Blend phonemes to form words | CCSS | Generic, no qualifiers |
| Blend spoken phonemes into one-syllable words | TX | "spoken", "one-syllable" |
| Orally blend 2-3 phonemes into recognizable words | CA | "orally", "2-3", "recognizable" |
| Blend sounds to make one-syllable words | VA | "sounds" not "phonemes" |
| Orally produce words by blending sounds | OH | "produce", "sounds" |

**Result**: 5-12 ROCK skills teaching the same Science of Reading competency, with **no field indicating conceptual equivalence**.

### 1.2 The Dual Granularity Trap for P&I

**P&I teams face problems from both directions:**

#### Problem A: ROCK Skills Too Broad
- **ROCK Skill**: "Blend phonemes to form words" (covers entire concept)
- **P&I Needs**: 
  - Day 1: Blend 2-phoneme CVC words (cat, dog)
  - Day 2: Blend 3-phoneme words (list, fast)
  - Day 3: Blend consonant blends (stop, plan)
  - Day 4: Blend with digraphs (ship, chat)
  - Day 5: Blend complex patterns (split, shrimp)

**Gap**: 1 ROCK skill → 5-10 instructional micro-objectives

#### Problem B: ROCK Skills Too Specific (State-Locked)
- **P&I develops**: 5 micro-lesson videos for phoneme blending
- **Dilemma**: Which ROCK skill(s) to tag content with?
  - **Option 1**: Tag with all 12 state-specific skills → Maintenance nightmare, massive redundancy
  - **Option 2**: Tag with one "canonical" skill → TX, CA, VA teachers can't find it
  - **Option 3**: Don't use ROCK skills → **Current reality**

**Result**: P&I cannot leverage ROCK. Builds parallel taxonomy, losing all ROCK standards alignment, metadata, and relationships.

#### The Business Lock-In
ROCK cannot be changed:
- **Star Assessment Dependency**: Primary revenue product depends on current structure
- **Historical Data**: Millions of student records tied to existing skills
- **Assessment Validity**: Fine-grained skills compromise psychometric properties
- **Data Integrity**: Schema changes risk breaking historical trend analysis

→ **P&I teams bypass ROCK entirely**

### 1.3 State A vs State B: Two Types of Skill Relationships

Analysis of 8,224 ROCK skills reveals **two distinct patterns of skill relationships**, each requiring different linking strategies:

#### State A: Cross-State Variants (Cross-Sectional Redundancy)

**Definition**: Conceptually identical skills with different terminology across education authorities at the **same grade level**.

**Example - Phoneme Blending (Grade K)**:

| ROCK Skill | Authority | Similarity |
|------------|-----------|------------|
| Blend phonemes to form words | CCSS | 0.92 |
| Blend spoken phonemes into one-syllable words | Texas | 0.89 |
| Orally blend 2-3 phonemes into recognizable words | California | 0.91 |
| Blend sounds to make one-syllable words | Virginia | 0.88 |

**Characteristics**:
- **Normalized name similarity**: > 0.85
- **Grade difference**: ≤ 1 grade level
- **Different education authorities**
- **Same underlying competency**

**Classification Results** (from 8,224 skills):
- **187 State A groups identified**
- **383 skills total** (~5% of inventory)
- **2-3 members per group** on average

**P&I Solution Need**: Enable content tagging to **one master concept** that automatically inherits all state variants. Tag once → applies to TX, CA, CCSS, VA, etc.

#### State B: Grade Progressions (Longitudinal Spiraling)

**Definition**: Related skills showing **increasing complexity** across sequential grade levels, typically within the same education authority or standard set.

**Example - Informational Text Analysis (Grades 1-8)**:

| Grade | ROCK Skill | Complexity |
|-------|------------|------------|
| 1 | Compose informative text (first-grade reading) | Level 1 |
| 2 | Compose informative text (second-grade reading) | Level 2 |
| 3 | Compose informative text (third-grade reading) | Level 3 |
| ... | ... | ... |
| 8 | Compose informative text (eighth-grade reading) | Level 8 |

**Characteristics**:
- **Normalized name similarity**: 0.6-0.8 (related but not identical)
- **Sequential grades**: 2→3→4 spiraling
- **Same authority** or universal (CCSS)
- **Increasing complexity** in same skill family

**Classification Results** (from 8,224 skills):
- **220 State B chains identified**
- **569 skills total** (~7% of inventory)
- **2-8 members per chain** (median: 2-3 grades)

**P&I Solution Need**: Learning progression navigation with **prerequisite relationships**. Show teachers developmental sequence, suggest "next level" content automatically.

#### The Remaining 88%: Unique Skills

**Classification Results**:
- **7,272 unique skills** (88% of inventory)
- Not part of State A or B patterns
- May still need taxonomy mapping for conceptual organization
- Represent specialized or single-state skills

#### Why This Distinction Matters

**For P&I Product Design**:

| Problem Type | Linking Strategy | Use Case |
|--------------|------------------|----------|
| **State A** | Equivalence Groups | Tag content once → applies to all state variants |
| **State B** | Prerequisite Chains | Adaptive sequencing, learning progressions |
| **Unique** | Direct 1:1 Mapping | Standard content tagging |

**Metadata Requirements**:

| Field | State A | State B | Purpose |
|-------|---------|---------|---------|
| `EQUIVALENCE_GROUP_ID` | ✓ | ✓ | Link related skills |
| `EQUIVALENCE_TYPE` | "state-variant" | "grade-progression" | Distinguish pattern type |
| `PREREQUISITE_SKILL_IDS` | ✗ | ✓ | Build prerequisite chains |
| `COMPLEXITY_LEVEL` | ✗ | ✓ (1-5) | Rank difficulty in progression |
| `MASTER_TAXONOMY_NODE` | ✓ | ✓ | Map to evidence-based framework |

**Example Query Patterns**:

```sql
-- State A: Find all equivalent skills for content tagging
SELECT * FROM skills 
WHERE EQUIVALENCE_GROUP_ID = 'uuid-1234'
  AND EQUIVALENCE_TYPE = 'state-variant';

-- State B: Get prerequisite chain for learning progression
WITH RECURSIVE prerequisite_chain AS (
  SELECT * FROM skills WHERE SKILL_ID = 'target-skill-id'
  UNION
  SELECT s.* FROM skills s
  JOIN prerequisite_chain pc ON s.SKILL_ID = pc.PREREQUISITE_SKILL_IDS
)
SELECT * FROM prerequisite_chain ORDER BY COMPLEXITY_LEVEL;
```

**Validation**: Automated classification using TF-IDF similarity + grade analysis achieved 187 State A groups and 220 State B chains from 8,224 skills. Human review of sample groups confirmed >90% accuracy.

### 1.4 The Compound Effect: Real-World Scenario

**Building a Context Clues Unit for P&I**

**Step 1: Horizontal Fragmentation**
- Search "context clues" in ROCK
- Find 12-15 state-specific skills (TX, CA, OH, VA, CCSS, etc.)
- Spend 2-3 hours determining conceptual equivalence
- **Waste**: Cannot easily discover all relevant skills

**Step 2: Vertical - Too Broad**
- Each ROCK skill covers entire "context clues" concept
- P&I needs 5 micro-lessons (definition clues, synonym clues, antonym clues, example clues, multi-clue)
- ROCK cannot support decomposition
- **Result**: Must create micro-objectives from scratch

**Step 3: Vertical - Too Specific**
- P&I develops 5 micro-lesson videos
- Cannot tag to single ROCK skill (loses state coverage)
- Cannot tag to all 12-15 skills (unsustainable redundancy)
- **Result**: Bypass ROCK, use custom P&I taxonomy

**Step 4: Business Constraint**
- Cannot modify ROCK to fix any problem (Star dependency)
- Cannot add master concepts (schema changes too risky)
- **Result**: Complete bypass, duplicate infrastructure

**Total Impact**: 80-90% efficiency loss vs. integrated system

---

## 2. Quantified Analysis

### 2.1 Estimated Redundancy Across ROCK

Based on sample analysis of literacy skills:

| Science of Reading Concept | Est. ROCK Skills | States | Grade Spread |
|----------------------------|------------------|--------|--------------|
| Phoneme Blending | 8-12 | TX, CA, CCSS, VA, OH, FL+ | K-2 |
| Phoneme Segmentation | 8-12 | Multiple | K-2 |
| Context Clues for Word Meaning | 10-15 | Most states | 2-6 |
| Main Idea Identification | 12-18 | Most states | 2-8 |
| Text Structure Analysis | 10-14 | Most states | 3-7 |
| Inferencing | 15-20 | Most states | 2-10 |
| Author's Purpose | 10-15 | Most states | 3-9 |
| Decoding Multisyllabic Words | 12-16 | Most states | 2-5 |

**Projected Inventory**:

| Content Area | Total ROCK Skills | Unique Master Concepts | Redundancy Ratio |
|--------------|------------------|----------------------|------------------|
| ELA Literacy | ~1,200 | 150-200 | **6-8x** |
| Mathematics | ~900 | 120-150 | **6-7.5x** |
| **Total** | **~2,100** | **270-350** | **~6-8x** |

**Interpretation**: For every 6-8 ROCK skills, there is one underlying master concept—the rest are state/grade variants.

### 2.2 The P&I Scaling Problem

**Without Master Taxonomy**:
- P&I develops content for "Phoneme Blending"
- Must choose: Tag 12x (unsustainable) OR Pick 1 skill (lose coverage) OR Bypass ROCK (current)
- Cannot scale instructional content across state boundaries
- Must replicate content or build parallel system

**With Master Taxonomy**:
- Tag content once to "Phoneme Blending" master concept
- Automatically inherits all 12 state-specific ROCK skills
- Content discoverable across all states
- Enables scalable P&I development

**Efficiency Gain**: 60-80% reduction in tagging overhead and content fragmentation

---

## 3. Current ROCK Schema Architecture

### 3.1 What Exists

```
skills.csv:
  - SKILL_ID (PK)
  - SKILL_NAME
  - SKILL_AREA_NAME (flat grouping, not hierarchical)
  - CONTENT_AREA_NAME
  - GRADE_LEVEL_NAME
  - DOK_LEVEL
  
standard-skills.csv:
  - SKILL_ID → STANDARD_ID
  - EDUCATION_AUTHORITY (TX, CA, CCSS, etc.)
  - STANDARD_SET_NAME
```

### 3.2 What's Missing

**(No tables or fields for):**
- Master Skill Taxonomy Reference (Science of Reading, Learning Progressions)
- Conceptual Equivalence Mappings (state variants)
- Hierarchical Decomposition (micro-objectives for P&I)
- Learning-Science-Based Prerequisites/Progressions

**Critical Gap**: Cannot query "all skills teaching phoneme blending" or "conceptual equivalents of this skill" or "micro-objectives under this skill."

### 3.3 Comparison to Science of Reading Taxonomy

**Science of Reading Framework**:
- ✅ **6-level hierarchy**: Strand → Pillar → Domain → Skill Area → Skill Set → Skill Subset
- ✅ **Evidence-based**: Grounded in reading research (1,140 skill subsets)
- ✅ **Grade-independent**: Cognitive constructs, not standards
- ✅ **Consistent**: No state variations
- ✅ **Annotated**: Behavioral descriptions for each skill

**ROCK Skills**:
- ❌ **Flat**: SKILL_AREA_NAME is loose grouping, not hierarchy
- ❌ **Standards-derived**: Tied to state political documents
- ❌ **Grade-specific**: Each skill locked to grade level
- ❌ **Fragmented**: State variations with no equivalence metadata

---

## 4. Stakeholder Impact

### 4.1 Curriculum Developers
**Current Pain**:
- Cannot discover all skills for a concept (60-75% redundancy hidden)
- Must manually identify conceptual equivalents (2-3 hours per concept)
- Duplicate content development for similar skills
- Cannot decompose ROCK skills into daily objectives

**With Taxonomy**:
- Query master concept → get all ROCK skills automatically
- See state variants vs. developmental progressions
- Tag content once → inherits all state ROCK skills
- View hierarchical decomposition for P&I planning

**Efficiency Gain**: 60-80% reduction in search/analysis/tagging time

### 4.2 Product Teams
**Current Pain**:
- Adaptive features requiring skill relationships blocked
- Cannot identify conceptually related skills across states
- Cannot build learning progressions grounded in cognitive science
- P&I products bypass ROCK entirely (no metadata reuse)

**With Taxonomy**:
- Recommend conceptually related skills
- Follow evidence-based learning progressions
- Adapt seamlessly across state configurations
- Enable P&I integration with ROCK

**Value**: Next-generation personalization and cross-product integration

### 4.3 Data Scientists & Educators
**Researchers**:
- Cannot aggregate data by master constructs
- Cross-state analyses require manual skill coding
- Research publications require extensive manual work

**Educators**:
- Searching by concept yields incomplete results
- Unclear which skills are redundant vs. progressive
- Difficult to match diagnostics to interventions

**With Taxonomy**: Research-grade aggregation, transparent progressions, concept-based search

---

## 5. Root Cause & Historical Context

### 5.1 Why ROCK Is Standards-Driven

**Historical Rationale**:
- Renaissance products must demonstrate standards alignment for state adoptions
- Standards compliance is contractual/regulatory requirement
- ROCK designed to prove alignment to accountability frameworks

**This Made Sense When**:
- Standards-based reform was primary driver (1990s-2010s)
- Cross-state comparison less important
- Adaptive systems less sophisticated
- Learning science taxonomies less mature

### 5.2 Why the Problem Persists

**Technical**: Large existing inventory (~2,100 skills), complex migration
**Organizational**: Multiple product owners, no single taxonomic authority
**Knowledge**: Requires learning science expertise, subjective mapping decisions
**Business**: Star dependency, historical data, competing priorities

### 5.3 Why It Matters Now

- **Learning Science Renaissance**: Science of Reading mainstream
- **Product Differentiation**: Competitors adopting taxonomy-driven architectures
- **Adaptive Systems**: Next-gen features require skill relationships
- **P&I Ecosystem**: Instructional products need ROCK integration but cannot use current structure
- **Research Validation**: Must ground products in learning science

---

## 6. Success Criteria for a Solution

A viable solution would enable:

1. ✅ Query all ROCK skills teaching a master competency [horizontal]
2. ✅ Identify conceptually equivalent skills across states [horizontal + vertical-specific]
3. ✅ Tag P&I content once, automatically inherit all state ROCK skills [vertical-specific]
4. ✅ View hierarchical decomposition into micro-objectives for P&I [vertical-broad]
5. ✅ Discover learning progressions grounded in evidence [vertical-broad]
6. ✅ Aggregate data at master-concept level for research [horizontal]
7. ✅ Link ROCK skills to Science of Reading taxonomy nodes [all dimensions]
8. ✅ Maintain standards alignment while adding science layer [business constraint]

**Key Requirement**: Must be **non-invasive**—preserve existing ROCK structure, Star dependency, and historical data.

---

## 7. Next Steps

### Immediate Actions
1. **Validate Problem**: Sample-analyze ROCK skills to confirm 6-8x redundancy
2. **Prioritize Domains**: Start with high-impact areas (K-2 foundational literacy)
3. **Engage Stakeholders**: Share analysis with curriculum, product, research leaders
4. **Assess Taxonomies**: Evaluate Science of Reading and Math Learning Progressions

### Future Exploration
1. **Pilot Mapping**: Map 50-100 skills to Science of Reading as proof of concept
2. **Schema Design**: Design taxonomic metadata fields/tables (bridge layer)
3. **Tooling**: Explore AI/NLP for semi-automated skill-to-taxonomy mapping
4. **Governance**: Establish process for maintaining taxonomic metadata

**This document focuses on problem definition. Solution design is a separate effort.**

---

## Appendix: References

- **ROCK Schemas**: `/rock_schemas/` directory (skills.csv, standards.csv, standard-skills.csv, etc.)
- **Science of Reading Taxonomy**: `POC_science_of_reading_literacy_skills_taxonomy.csv` (1,140 rows, 6-level hierarchy)
- **Related Documentation**: 
  - `1-schema-overview.md`: Technical schema reference
  - `3-visual-diagrams.md`: Mermaid flowcharts
- **ROCK Skills Agent**: `agents/work-agents/rock-skills-agent.txt`: Expert consultation resource
