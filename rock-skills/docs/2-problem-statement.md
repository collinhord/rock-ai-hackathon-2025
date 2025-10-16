# ROCK Skills Compound Architectural Problem: Problem Statement

**Document Status**: Analysis and Problem Definition (Solution-Neutral)

**Prepared For**: ROCK Skills List Advancement Team

**Date**: October 2025

---

## Executive Summary

The ROCK Skills List faces a **compound architectural problem** with three interrelated failure modes preventing ecosystem-wide integration.

### Problem 1: Horizontal Fragmentation (Cross-State Redundancy)
Skills derive from state-specific standards rather than science-based master competencies, creating 6-8x redundancy (8-15 conceptually identical skills per learning objective) with no metadata connecting them.

### Problem 2: Vertical Granularity Mismatch + Absent Bridging Mechanisms
ROCK skills create an impossible scaling situation with two interrelated problems:
- **Too Broad**: One ROCK skill covers entire competency; P&I needs 5-10 micro-objectives for daily lessons
- **No Cross-State Bridging**: Even when appropriately-granular ROCK skills exist, absent master skill relationships prevent content from being discoverable/reusable across 50+ state systems—no proxying mechanism exists

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
2. **Master skills as bridging/proxy mechanisms** to enable cross-state content scaling (vertical bridging)
3. State variant mappings to enable P&I content discoverability (vertical-specific)
4. Hierarchical decomposition for micro-objectives (vertical-broad)
5. Bridge layer preserving ROCK immutability (business constraint)

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

#### Problem B: No Cross-State Bridging Mechanism (The Scaling Blocker)
- **Reality**: Appropriately-granular ROCK skills often DO exist for specific states
- **Critical Gap**: No **master skill** to serve as bridging/proxy mechanism connecting equivalent skills across states
- **P&I develops**: Lesson content "Blend 2-phoneme CVC words" (perfect granularity)
- **Impossible Dilemma**: Which ROCK skill(s) to tag content with?
  - **Option 1**: Tag with TX skill only → CA/OH/VA/FL users cannot discover content (invisible to 49 states)
  - **Option 2**: Tag with all 50 state-specific skills → Maintenance nightmare, metadata explosion, unsustainable
  - **Option 3**: Create master skill as content anchor → **BLOCKED** (ROCK immutable, Star dependency)
  - **Option 4**: Don't use ROCK skills → **Current reality**

**Key Insight**: Even when lesson-granularity skills exist in ROCK, content cannot scale because:
- **No Proxy Mechanism**: Master skill would serve as single content anchor that automatically inherits all state variants
- **No Discoverability**: Content tagged to one state's skill is invisible to equivalent skills in other states
- **No Reusability**: Must duplicate content 50x or bypass ROCK entirely

**Result**: P&I cannot leverage ROCK. Builds parallel taxonomy, losing all ROCK standards alignment, metadata, and relationships.

#### The Business Lock-In
ROCK cannot be changed:
- **Star Assessment Dependency**: Primary revenue product depends on current structure
- **Historical Data**: Millions of student records tied to existing skills
- **Assessment Validity**: Fine-grained skills compromise psychometric properties
- **Data Integrity**: Schema changes risk breaking historical trend analysis

→ **P&I teams bypass ROCK entirely**

### 1.3 The Compound Effect: Real-World Scenario

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

**Step 3: Vertical - No Bridging Mechanism**
- P&I develops 5 micro-lesson videos (appropriate granularity achieved)
- Even if perfect-match ROCK skills exist for some states, no way to scale content:
  - Cannot tag to single state's ROCK skill (invisible to 49 other states)
  - Cannot tag to all 50+ state-specific skills (metadata explosion, unmaintainable)
  - Cannot create master skill as content anchor (ROCK immutable)
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

### 2.2 The P&I Scaling Problem: Absent Bridging Mechanism

**The Fundamental Blocker**: Even when ROCK has appropriately-granular skills for specific states, content cannot scale because no master skill exists to proxy/bridge across state variants.

**Without Master Skill Bridging**:
- P&I develops content "Blend 2-phoneme CVC words" (perfect lesson granularity)
- ROCK has matching skills for TX, CA, OH, VA, FL, etc. (appropriate granularity exists!)
- **But no way to connect them**: Must choose impossible option:
  - **Tag 50+ state skills** (metadata explosion, unsustainable maintenance)
  - **Pick 1 state skill** (content invisible to 49 other states)
  - **Bypass ROCK entirely** (current reality)
- Cannot scale instructional content across state boundaries
- Must replicate content 50x or build parallel system

**With Master Skill Bridging (Proxy Mechanism)**:
- Tag content once to "Phoneme Blending: 2-phoneme CVC" master skill
- Master skill automatically inherits mappings to all equivalent state-specific ROCK skills (TX, CA, OH, VA, FL, etc.)
- Content discoverable across all 50+ states via single anchor point
- Update master mappings → automatically propagates to all tagged content
- Enables scalable P&I development with state-specific ROCK alignment preserved

**Key Insight**: The problem isn't that granular skills don't exist—it's that **without master skills as proxy/bridge**, content tagged to one state's skill cannot be discovered by users searching through equivalent skills in other states.

**Efficiency Gain**: 60-80% reduction in tagging overhead and content fragmentation; enables content reuse across 50+ state systems

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
- **Bridging/Proxy Mechanisms** (master skills as content anchor points that inherit state variant relationships)
- Hierarchical Decomposition (micro-objectives for P&I)
- Learning-Science-Based Prerequisites/Progressions

**Critical Gap**: Cannot query "all skills teaching phoneme blending" or "conceptual equivalents of this skill" or "micro-objectives under this skill." **Cannot tag content to proxy that automatically connects to equivalent skills across 50+ state systems.**

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
- Content developed for one state cannot be discovered by users in other states
- No bridging mechanism to scale content across 50+ state systems
- Must duplicate content development or maintain 50+ state-specific tags
- Cannot decompose ROCK skills into daily objectives

**With Master Skill Bridging/Proxy**:
- Query master concept → get all equivalent ROCK skills automatically across all states
- See state variants vs. developmental progressions
- **Tag content once to master skill (proxy) → automatically inherits mappings to all equivalent state ROCK skills**
- Content discoverable across all 50+ state systems via single anchor point
- View hierarchical decomposition for P&I planning

**Efficiency Gain**: 60-80% reduction in search/analysis/tagging time; enables content reuse across 50+ state configurations

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
3. ✅ **Tag P&I content once to master skill (proxy/bridge), automatically inherit all equivalent state-specific ROCK skills** [vertical bridging—the critical scaling mechanism]
4. ✅ Content discoverable across 50+ state systems via single master skill anchor [cross-state content scaling]
5. ✅ View hierarchical decomposition into micro-objectives for P&I [vertical-broad]
6. ✅ Discover learning progressions grounded in evidence [vertical-broad]
7. ✅ Aggregate data at master-concept level for research [horizontal]
8. ✅ Link ROCK skills to Science of Reading taxonomy nodes [all dimensions]
9. ✅ Maintain standards alignment while adding science layer [business constraint]

**Key Requirement**: Must be **non-invasive**—preserve existing ROCK structure, Star dependency, and historical data. Master skills serve as external **proxy/bridging layer**, not schema modifications.

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
