# ROCK Skills Metadata Gap Analysis

**Purpose**: Document what metadata currently exists in ROCK schemas vs. what would be needed for science-based taxonomy bridging.

**Date**: October 2025

---

## Current ROCK Metadata Structure

### Fields That Exist

#### SKILLS.csv
- `SKILL_ID` - Unique identifier (GUID)
- `SKILL_NAME` - Full text description
- `SKILL_SHORT_NAME` - Abbreviated name
- `SKILL_AREA_NAME` - Flat grouping category
- `CONTENT_AREA_NAME` - Subject (ELA, Math, etc.)
- `GRADE_LEVEL_NAME` - Default grade level
- `DOK_LEVEL` - Depth of Knowledge (1-4)
- `SKILL_STATUS` - Lifecycle status

**Current Capabilities:**
- ✅ Can group skills by SKILL_AREA_NAME (flat grouping)
- ✅ Can filter by content area and grade level
- ✅ Can track DOK cognitive complexity
- ✅ Can link to state standards via STANDARD_SKILLS

**Limitations:**
- ❌ No hierarchical taxonomy structure
- ❌ No reference to evidence-based master competencies
- ❌ No semantic/conceptual relationships between skills
- ❌ No learning progression metadata
- ❌ No cognitive construct tags

#### STANDARD_SKILLS.csv
- `SKILL_ID` - Foreign key to SKILLS
- `STANDARD_ID` - Foreign key to STANDARDS
- `EDUCATION_AUTHORITY` - State/region (TX, CA, CCSS, etc.)
- `STANDARD_SET_NAME` - Standards collection name
- `RELATIONSHIP_TYPE` - Always "is_aligned_to"

**Current Capabilities:**
- ✅ Can trace skill back to originating standard(s)
- ✅ Can identify which states use which skills
- ✅ Can count standards per skill (many-to-many)

**Limitations:**
- ❌ No distinction between "same concept, different state" vs. "related but distinct concepts"
- ❌ No confidence score for alignment strength
- ❌ No indication of why skills are related

#### STANDARDS.csv
- `STANDARD_ID` - Unique identifier
- `STANDARD_CODE` - Human-readable code (e.g., "CCSS.ELA-Literacy.RF.K.3.c")
- `STANDARD_DESCRIPTION` - Full standard text
- `EDUCATION_AUTHORITY` - State/authority
- `DOMAIN_NAME` - Subject-area grouping
- `DOMAIN_GROUP_NAME` - High-level category
- `GRADE_RANGE` - Applicable grades

**Current Capabilities:**
- ✅ Provides standards context for skills
- ✅ Shows domain structure from standards documents

**Limitations:**
- ❌ Domain structure is organizational, not learning-science-based
- ❌ No cross-state concept alignment

---

## What's Missing: Taxonomic Bridge Metadata

To connect fragmented ROCK skills to science-based master competencies (e.g., Science of Reading), the following metadata would be needed:

### 1. Master Taxonomy Reference Fields

**Proposed Fields for SKILLS table or new linking table:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `MASTER_TAXONOMY_ID` | String | ID from external taxonomy (e.g., SoR) | `SOR-PhonAware-Blend-002` |
| `TAXONOMY_SOURCE` | String | Which taxonomy framework | `Science of Reading`, `Math Learning Progressions` |
| `TAXONOMY_PATH` | String | Full hierarchical path | `Decoding and Word Recognition > Phonological Awareness > Phoneme Blending` |
| `TAXONOMY_LEVEL` | Integer | Depth in hierarchy (1=Strand, 6=Skill Subset) | `4` (Skill Area level) |
| `MAPPING_CONFIDENCE` | String | Confidence of mapping | `High`, `Medium`, `Low` |
| `MAPPING_RATIONALE` | Text | Why this mapping was made | "Skill explicitly teaches phoneme blending..." |
| `MAPPED_BY` | String | Who/what created mapping | `curriculum_specialist_jdoe`, `AI_assisted` |
| `MAPPED_DATE` | Date | When mapping was created | `2025-10-14` |

### 2. Conceptual Equivalence Fields

**To identify state-specific variants of the same master skill:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `MASTER_SKILL_GROUP_ID` | String | Groups conceptually equivalent skills | `MSG-ContextClues-001` |
| `EQUIVALENCE_TYPE` | String | How skills are related | `Identical Concept`, `Narrower Scope`, `Broader Scope` |
| `PRIMARY_SKILL_ID` | String | Reference to "canonical" version | GUID of CCSS skill |
| `VARIANT_REASON` | String | Why variant exists | `State-specific terminology`, `Grade-level adaptation` |

### 3. Learning Progression Metadata

**To capture prerequisite relationships and developmental sequences:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `PREREQUISITE_SKILL_IDS` | Array | Skills that should come before | `[guid1, guid2, guid3]` |
| `PROGRESSION_LEVEL` | Integer | Step in learning sequence | `3` (e.g., level 3 of 5) |
| `PROGRESSION_GROUP_ID` | String | IDs of skills in same progression | `PROG-Decoding-Basic-to-Advanced` |
| `DEVELOPMENTAL_STAGE` | String | Educational phase | `Early Emergent`, `Developing`, `Proficient` |

### 4. Cognitive Construct Tags

**To enable searching by learning science concepts:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `COGNITIVE_CONSTRUCTS` | Array | Research-based competencies taught | `['phonological-awareness', 'working-memory']` |
| `SOR_PILLAR` | String | Science of Reading pillar | `Phonological Awareness`, `Phonics`, `Fluency`, `Vocabulary`, `Comprehension` |
| `LITERACY_COMPONENT` | String | Literacy framework component | `Decoding`, `Language Comprehension`, `Strategic Knowledge` |

### 5. Cross-Reference Metadata

**To link to external frameworks and assessments:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `EXTERNAL_FRAMEWORK_IDs` | JSON | References to other taxonomies | `{"NRP": "PA-Blend-1", "IDA": "Phon-2.1"}` |
| `ASSESSMENT_TAGS` | Array | Related assessment types | `['CBM-ORF', 'Phoneme-Segmentation-Fluency']` |

---

## Schema Design Options

### Option 1: Add Fields to SKILLS Table
**Pros:** Simple, direct access  
**Cons:** Schema changes risky (Star dependency), bloats existing table

### Option 2: Create New SKILL_TAXONOMY_MAPPINGS Table
**Pros:** Non-invasive, can evolve independently, supports multiple taxonomies  
**Cons:** Requires joins for queries

**Recommended Structure:**
```sql
CREATE TABLE SKILL_TAXONOMY_MAPPINGS (
    MAPPING_ID (PK),
    SKILL_ID (FK to SKILLS),
    TAXONOMY_SOURCE,
    MASTER_TAXONOMY_ID,
    TAXONOMY_PATH,
    TAXONOMY_LEVEL,
    MAPPING_CONFIDENCE,
    MAPPING_RATIONALE,
    MAPPED_BY,
    MAPPED_DATE,
    IS_ACTIVE
);

CREATE TABLE SKILL_EQUIVALENCE_GROUPS (
    GROUP_ID (PK),
    MASTER_SKILL_GROUP_ID,
    GROUP_NAME,
    GROUP_DESCRIPTION,
    TAXONOMY_REFERENCE
);

CREATE TABLE SKILL_EQUIVALENCE_MEMBERS (
    MEMBER_ID (PK),
    GROUP_ID (FK to SKILL_EQUIVALENCE_GROUPS),
    SKILL_ID (FK to SKILLS),
    EQUIVALENCE_TYPE,
    VARIANT_REASON,
    IS_PRIMARY
);

CREATE TABLE SKILL_PROGRESSIONS (
    PROGRESSION_ID (PK),
    SKILL_ID (FK to SKILLS),
    PREREQUISITE_SKILL_ID (FK to SKILLS),
    PROGRESSION_GROUP_ID,
    PROGRESSION_LEVEL,
    RELATIONSHIP_TYPE
);
```

### Option 3: External Mapping Store (JSON/Document DB)
**Pros:** Maximum flexibility, no schema changes  
**Cons:** Separate system to maintain, may not integrate well with existing tools

---

## Standard-to-Skill Cardinality Patterns

Based on the STANDARD_SKILLS relationships:

### Common Patterns:
1. **One-to-Many**: Single standard → multiple ROCK skills (standard broken into assessable pieces)
2. **Many-to-One**: Multiple standards → single ROCK skill (skill synthesizes standards)
3. **Many-to-Many**: Complex web of relationships

### Observed Issues:
- **Inconsistent Granularity**: Some standards map to 1 skill, others to 10+
- **No Rationale**: Why standards were split/merged not documented
- **State Variations**: Same concept has different cardinality across states

**Example:**
- CCSS RF.K.2.c (phoneme blending) → 1 ROCK skill
- TX TEKS K.2.A (phonological awareness) → 5 ROCK skills (blend, segment, delete, substitute, combine)
- Both teach related concepts but inconsistent decomposition

---

## Skill Area Name Inconsistencies

### Problem: Same concept, different SKILL_AREA_NAME across authorities

**Example: Phoneme Blending Skills**

| SKILL_NAME | SKILL_AREA_NAME | EDUCATION_AUTHORITY |
|------------|-----------------|---------------------|
| Blend phonemes to form words | Blending and Segmenting | CCSS |
| Blend spoken phonemes into one-syllable words | Phonological Awareness | TX |
| Orally blend 2-3 phonemes into recognizable words | Foundational Skills | CA |

**Analysis:**
- Same master concept ("Phoneme Blending" from Science of Reading)
- 3 different SKILL_AREA_NAME values
- No field indicating they're conceptually related

**Impact:**
- Cannot query "show me all blending skills" without knowing all possible SKILL_AREA_NAME variants
- Curriculum developers miss relevant skills from other states
- Analytics cannot aggregate by concept

---

## Comparison to Science of Reading Taxonomy

### What Science of Reading Provides (That ROCK Lacks)

#### Hierarchical Structure (6 Levels)
- **Strand** → **Pillar** → **Domain** → **Skill Area** → **Skill Set** → **Skill Subset**
- Example: `Active Self-Regulation > Executive Function Skills > Core Executive Processes > Working Memory Updating > Goal and Information Updating`

**ROCK equivalent:** Only 1-2 levels (CONTENT_AREA_NAME > SKILL_AREA_NAME)

#### Evidence-Based Grounding
- Every node tied to cognitive/linguistic research
- Annotations with examples and behavioral descriptions
- Grade-independent (focuses on competency, not age)

**ROCK equivalent:** Standards-based (political/legislative, not purely research)

#### Comprehensive Coverage
- 1,140 skill subsets covering literacy + executive function + metacognition
- Includes underlying competencies (attention, memory, motivation) not just reading mechanics

**ROCK equivalent:** Focused on assessable standards, missing foundation skills

#### Consistent Terminology
- Same terms used across all applications
- No state-specific variations

**ROCK equivalent:** Terminology varies by education authority

---

## Recommended Next Steps

### Immediate (Proof of Concept)
1. ✅ Create SKILL_TAXONOMY_MAPPINGS CSV with 50-100 pilot mappings
2. ✅ Map high-impact ELA skills to Science of Reading taxonomy
3. ✅ Document mapping methodology and confidence criteria
4. ✅ Build prototype query tool demonstrating value

### Short-Term (Production Pilot)
1. Design SKILL_TAXONOMY_MAPPINGS table schema
2. Implement in test environment
3. Map 500 skills (K-2 foundational literacy)
4. Build API endpoints for taxonomy queries
5. Integrate with one product (e.g., Star Early Literacy)

### Long-Term (Full Implementation)
1. Map all ELA skills (~2,000+) to Science of Reading
2. Identify/create math learning progressions taxonomy
3. Map all Math skills (~2,000+)
4. Build governance process for maintaining mappings
5. Integrate taxonomy layer across all Renaissance products
6. Enable curriculum developers and educators to search by master concepts

---

## Key Insights

1. **The Gap is Metadata, Not Data**: ROCK has the skills, just missing the taxonomic links
2. **Non-Invasive Solution Possible**: Can add bridge layer without modifying ROCK core
3. **High Value, Defined Scope**: 50-skill pilot can demonstrate full concept
4. **Precedent Exists**: Science of Reading taxonomy is ready-to-use framework
5. **Solves Both Problems**: Addresses horizontal fragmentation AND provides structure for P&I vertical decomposition

---

## Related Documentation
- `redundancy-analysis.ipynb` - Quantitative analysis of fragmentation
- `fragmentation-examples.csv` - Concrete skill cluster examples
- `/rock-skills/docs/2-problem-statement.md` - Comprehensive problem analysis
- `/rock-skills/POC_science_of_reading_literacy_skills_taxonomy.csv` - Master taxonomy reference

