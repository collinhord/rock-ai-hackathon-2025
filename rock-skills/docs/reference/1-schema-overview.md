# ROCK Schema Overview

**Document Purpose**: Technical reference for understanding ROCK schema structure, relationships, and current metadata capabilities.

**Audience**: ROCK Skills List Advancement team, data analysts, curriculum developers

---

## Schema Files and Structure

### 1. SKILLS.csv

**Purpose**: Core ROCK skills that students demonstrate proficiency in across Renaissance products.

**Key Fields**:
- `SKILL_ID`: Unique identifier (GUID)
- `SKILL_NAME`: Full description of the skill
- `SKILL_SHORT_NAME`: Abbreviated name
- `SKILL_AREA_NAME`: Grouping category (references SKILL_AREAS.csv)
- `SKILL_AREA_ID`: Foreign key to SKILL_AREAS table
- `CONTENT_AREA_NAME`: Subject area (e.g., "English Language Arts", "Mathematics")
- `CONTENT_AREA_ID`: Foreign key for content area
- `CONTENT_AREA_SHORT_NAME`: Abbreviated content area
- `GRADE_LEVEL_NAME`: Default grade level (K, 1-12)
- `GRADE_LEVEL_DEFAULT_ID`: Grade level identifier
- `GRADE_LEVEL_DEFAULT_ORDER`: Sorting order
- `DOK_LEVEL`: Depth of Knowledge level (1-4)
- `PEDAGOGICAL_LIMITS`: Instructional constraints or guidance
- `USP_SECTION_CODE`, `USP_SECTION_NAME`, `USP_SECTION_ID`: Universal Skills Platform section classification
- `SKILL_STATUS`: Lifecycle status (Released, Development, Deprecated)
- `USP_SKILL_STATUS`: Universal Skills Platform status

**Special Skill Flags**:
- `IS_EN_US_FOCUS_SKILL`: Flagged as a focus skill for English/US
- `IS_G3_READING_PROFICIENCY_SKILL`: Grade 3 reading proficiency indicator
- `IS_G4_PROFICIENCY_SKILL`: Grade 4 proficiency indicator
- `IS_KINDERGARTEN_READINESS_SKILL`: Kindergarten readiness indicator
- `IS_ALGEBRA_READINESS_SKILL`: Algebra readiness indicator
- `HAS_CBM_MEASURE`: Has Curriculum-Based Measurement

**Metadata Fields**:
- `REPLACES_SKILL_ID`: If this skill replaces a deprecated skill
- `SKILL_CREATION_RATIONALE`: Why the skill was created
- `SKILL_NOTES`: Additional notes
- `DEV_NOTE`: Development notes
- `LAST_CHANGE_TYPE`, `LAST_CHANGE_BATCH`: Change tracking

**Current Limitations**:
- No field linking to science-based master skills or learning progressions
- No taxonomic hierarchy beyond flat SKILL_AREA_NAME groupings
- No semantic similarity or conceptual relationship metadata
- Skills can only be related through shared standards, not learning science

---

### 2. SKILL_AREAS.csv

**Purpose**: Defines the skill area categories used to group skills.

**Key Fields**:
- `SKILL_AREA_ID`: Unique identifier
- `SKILL_AREA_NAME`: Name of the skill area (e.g., "Word Meaning and Reference Materials", "Blending and Segmenting")
- `SKILL_AREA_STATUS`: Lifecycle status
- `CONTENT_AREA_ID`: Foreign key to content area
- `CONTENT_AREA_SHORT_NAME`: Abbreviated content area
- `CONTENT_AREA_NAME`: Full content area name
- `REPLACES_SKILL_AREA_ID`: If this replaces a deprecated skill area
- `SKILL_AREA_CREATION_RATIONALE`: Why this grouping was created
- `SKILL_AREA_NOTES`: Additional documentation
- `LAST_CHANGE_TYPE`, `LAST_BATCH_NAME`: Change tracking

**Observation**: Skill areas are flat groupings, not hierarchical. They provide organizational structure but lack taxonomic depth.

---

### 3. STANDARDS.csv

**Purpose**: Educational standards from state, national, and international authorities that ROCK skills align to.

**Key Fields**:

**Identification**:
- `STANDARD_ID_VERSION`: Versioned identifier
- `STANDARD_ID`: Base identifier (GUID)
- `STANDARD_CODE_FQ`: Fully qualified code
- `STANDARD_CODE`: Human-readable code (e.g., "CCSS.ELA-Literacy.RF.K.3.c")
- `STANDARD_DESCRIPTION`: Full text of the standard
- `STANDARD_TYPE`: Type classification
- `STANDARD_HIERARCHY_LEVEL`: Level in standards hierarchy
- `STANDARD_STATUS`: Status (Released, Deprecated, Obsolete, Historical Use)
- `STANDARD_DISPLAY_ORDER`: Sorting order
- `GRADE_RANGE`: Applicable grades

**Standard Set Information**:
- `STANDARD_SET_ID_VERSION`: Versioned standard set identifier
- `STANDARD_SET_NAME`: Collection name (e.g., "CPR for TX", "CPM for CA")
- `STANDARD_SET_SHORT_NAME`: Abbreviated name
- `STANDARD_SET_DESCRIPTION`: Full description
- `STANDARD_SET_AUTHORITY_NAME`: Publishing authority
- `STANDARD_SET_INTERNAL_NAME`: Internal reference name
- `STANDARD_SET_IS_LATEST`: Version flags (latest, latest GA, latest dev, latest internal)
- `STANDARD_SET_STATUS`, `STANDARD_SET_STATUS_CODE`: Status information

**Geographic & Authority Information**:
- `EDUCATION_AUTHORITY`: State or region (TX, CA, OH, CCSS, etc.)
- `REGION`: Geographic region
- `COUNTRY`: Country code
- `IS_CCSS_RELATED`: Boolean indicating if derived from Common Core

**Content Classification**:
- `CONTENT_AREA_SHORT_NAME`: Subject abbreviation
- `CONTENT_AREA_NAME`: Subject (ELA, Mathematics)
- `SECTION_ID`, `SECTION_NAME`, `SECTION_SHORT_NAME`: Section classification
- `SECTION_DISPLAY_ORDER`: Section sorting

**Domain Information** (within standard set):
- `DOMAIN_GROUP_ID_VERSION`, `DOMAIN_GROUP_ID`: Domain group identifiers
- `DOMAIN_GROUP_NAME`: Higher-level grouping (e.g., "Foundational Skills", "Reading: Literature")
- `DOMAIN_GROUP_DISPLAY_ORDER`: Domain group sorting
- `DOMAIN_ID_VERSION`, `DOMAIN_ID`: Domain identifiers
- `DOMAIN_NAME`: Domain classification (e.g., "Phonics and Word Recognition")
- `DOMAIN_DISPLAY_ORDER`: Domain sorting

**Academic Benchmarks Integration**:
- `AB_STANDARD_GUID`: Academic Benchmarks standard identifier
- `AB_DOCUMENT_GUID`: Academic Benchmarks document identifier
- `ORIGIN_AB_STANDARD_GUID`: Original AB standard
- `ORIGIN_ROCK_STANDARD_ID_VERSION`: Original ROCK standard version

**Additional Metadata**:
- `DEFAULT_STAR_DIFFICULTY_LEVEL_SET`: STAR difficulty calibration set
- `LP_STANDARD_NAME`: Learning Platform standard name
- `INCLUDED_BY_SECTION`: Section inclusion rules
- `RULE_STANDARD_STATUS_DEFAULT`, `RULE_STANDARD_STATUS_RECOMMENDATION`: Status rules
- `ROCK_SOURCE`: Source system
- `DEV_NOTES`: Development notes
- `IS_MOCK`: Mock data flag
- `CDW_SOURCE`: Common Data Warehouse source

**Key Insight**: Standards are the source documents from which ROCK skills are derived. Each education authority's standards represent a state-specific interpretation of underlying educational concepts.

---

### 4. STANDARD_SKILLS.csv

**Purpose**: Many-to-many relationship table connecting standards to skills.

**Key Fields**:

**Relationship Identifiers**:
- `STANDARD_SET_ID_VERSION`: Versioned standard set ID
- `STANDARD_SET_ID`: Base standard set ID
- `STANDARD_ID_VERSION`: Versioned standard ID
- `STANDARD_ID`: Base standard ID
- `SKILL_ID`: Skill identifier
- `SKILL_NAME`: Denormalized skill name
- `RELATIONSHIP_TYPE`: Type of alignment (typically "is_aligned_to")

**Display & Organization**:
- `STANDARD_SKILL_DISPLAY_ORDER`: Order within standard
- `STANDARD_SET_SKILL_DISPLAY_ORDER`: Order within standard set
- `PROGRESSION_ORDER`: Sequence within curriculum

**Content Classification**:
- `CONTENT_AREA_SHORT_NAME`: Subject abbreviation
- `CONTENT_AREA_NAME`: Subject area
- `SECTION_ID`, `SECTION_NAME`, `SECTION_SHORT_NAME`: Section classification
- `SECTION_DISPLAY_ORDER`: Section sorting

**Skill Flags** (denormalized):
- `IS_EN_US_FOCUS_SKILL`: Focus skill flag
- `IS_BRIDGE_SKILL`: Bridge skill indicator
- `IS_G3_READING_PROFICIENCY_SKILL`: Grade 3 reading proficiency
- `IS_G4_PROFICIENCY_SKILL`: Grade 4 proficiency
- `IS_KINDERGARTEN_READINESS_SKILL`: Kindergarten readiness
- `IS_ALGEBRA_READINESS_SKILL`: Algebra readiness
- `HAS_CBM_MEASURE`: Curriculum-Based Measurement flag
- `PREDICTOR_INDICATOR`: Predictor relationship indicator

**STAR Assessment Difficulty Calibration**:
- `STAR_SKILL_DIFFICULTY`: STAR difficulty level
- `STAR_UNIFIED_SKILL_DIFFICULTY`: Unified difficulty measure
- `STAR_RASCH_SKILL_DIFFICULTY`: Rasch-calibrated difficulty
- `STAR_DIFFICULTY_CALIBRATION_VERSION`: Calibration version
- `STAR_SCALED_DIFFICULTY_50`, `_70`, `_75`, `_80`: Scaled difficulties at different performance levels

**Skill Collections**:
- `SKILL_INTENDED_COLLECTION_ID`: Intended collection identifier
- `SKILL_INTENDED_COLLECTION_SHORT_NAME`: Collection abbreviation
- `SKILL_INTENDED_COLLECTION_NAME`: Collection name
- `SKILL_INTENDED_COLLECTION_DISPLAY_ORDER`: Collection ordering
- `SKILL_INTENDED_GRADE_LEVEL_ID`: Intended grade level
- `COLLECTION_ID`, `COLLECTION_SHORT_NAME`, `COLLECTION_NAME`: Actual collection assignment
- `COLLECTION_DISPLAY_ORDER`: Collection sorting

**Metadata**:
- `PEDAGOGICAL_LIMITS`: Instructional constraints
- `DOK_LEVEL`: Depth of Knowledge
- `RELATIONSHIP_NOTES`: Additional notes on the relationship
- `LAST_CHANGE_TYPE`, `LAST_BATCH_NAME`: Change tracking

**Relationship Cardinality**:
- **One Standard → Many Skills**: A single standard can align to multiple ROCK skills
- **One Skill → Many Standards**: A single ROCK skill can align to standards from multiple states

**Critical Observation**: This table shows that skills are **state-standard-derived**, not **master-skill-derived**. The same conceptual skill appears multiple times, once for each state's expression, with NO field indicating conceptual equivalence across state variants.

---

### 5. STANDARD_SET_DOMAINS.csv

**Purpose**: Defines domains within standard sets - subject-area categories used to organize standards.

**Key Fields**:
- `STANDARD_SET_ID_VERSION`: Versioned standard set identifier
- `DOMAIN_ID_VERSION`: Versioned domain identifier
- `DOMAIN_ID`: Base domain identifier
- `DOMAIN_NAME`: Name of the domain (e.g., "Vocabulary Acquisition and Use", "Expressions and Equations")
- `DOMAIN_DISPLAY_ORDER`: Sorting order within standard set
- `DOMAIN_GROUP_ID_VERSION`: Versioned parent domain group ID
- `DOMAIN_GROUP_ID`: Base parent domain group ID
- `DOMAIN_GROUP_NAME`: Parent grouping (e.g., "Language", "Algebra")
- `DOMAIN_GROUP_DISPLAY_ORDER`: Domain group sorting order
- `DOMAIN_NOTES`: Additional documentation
- `DOMAIN_CREATION_RATIONALE`: Why this domain was created
- `LP_DOMAINGROUPID`, `LP_DOMAIN_TAGID`: Learning Platform identifiers
- `LAST_CHANGE_TYPE`, `LAST_CHANGE_BATCH_NAME`: Change tracking

**Source**: Domains originate from standards documents themselves (e.g., Common Core domains). They are **organizational**, not **conceptual taxonomies**.

**Limitation**: Domains group standards by how they were published in source documents, not by underlying learning science or cognitive progressions.

---

### 6. STANDARD_SET_DOMAIN_GROUPS.csv

**Purpose**: High-level groupings of domains within standard sets.

**Key Fields**:
- `STANDARD_SET_ID_VERSION`: Versioned standard set identifier
- `DOMAIN_GROUP_ID_VERSION`: Versioned domain group identifier
- `DOMAIN_GROUP_ID`: Base domain group identifier
- `DOMAIN_GROUP_NAME`: Name (e.g., "Foundational Skills", "Algebra", "Reading: Informational")
- `DOMAIN_GROUP_DISPLAY_ORDER`: Sorting order
- `DOMAIN_GROUP_STATUS`: Lifecycle status
- `DOMAIN_GROUP_NOTES`: Additional documentation
- `DOMAIN_GROUP_CREATION_RATIONALE`: Why this grouping was created
- `LAST_CHANGE_TYPE`, `LAST_CHANGE_BATCH`: Change tracking

**Examples**:
- **ELA**: Literature, Informational Text, Foundational Skills, Writing, Language
- **Math**: Number & Operations, Algebra, Functions, Geometry, Statistics & Probability

---

### 7. STANDARD_SETS.csv

**Purpose**: Collections of standards for specific education authorities and products.

**Key Fields**:

**Identification**:
- `STANDARD_SET_ID_VERSION`: Versioned identifier
- `STANDARD_SET_ID`: Base identifier
- `STANDARD_SET_NAME`: Name (e.g., "CPR for TX", "CPM for CA", "CPR for CCSS")
- `STANDARD_SET_SHORT_NAME`: Abbreviated name
- `STANDARD_SET_DESCRIPTION`: Full description
- `STANDARD_SET_AUTHORITY_NAME`: Publishing authority (e.g., "Texas Education Agency")
- `STANDARD_SET_INTERNAL_NAME`: Internal reference name

**Versioning**:
- `STANDARD_SET_VERSION_MAJOR`: Major version number
- `STANDARD_SET_VERSION_MINOR`: Minor version number
- `IS_LATEST`: Latest version flag
- `IS_LATEST_GENERAL_AVAILABILITY`: Latest GA release flag
- `IS_LATEST_INTERNAL`: Latest internal version flag
- `IS_LATEST_DEVELOPMENT`: Latest development version flag

**Content & Geographic Information**:
- `CONTENT_AREA_NAME`: Subject area
- `CONTENT_AREA_SHORT_NAME`: Subject abbreviation
- `EDUCATION_AUTHORITY`: State or entity (TX, CA, CCSS, REN, etc.)
- `REGION`: Geographic region
- `COUNTRY`: Country code
- `ZONE`: Geographic zone

**Common Core Information**:
- `IS_CCSS_RELATED`: Whether derived from Common Core State Standards
- `CCSS_STANDARD_SET_ID_VERSION`: Reference to related CCSS standard set
- `CCSS_ADOPTER_STATUS`: If state adopted CCSS (Adopter, Non-Adopter, Unknown)

**Status**:
- `STANDARD_SET_STATUS`: Status description
- `STANDARD_SET_STATUS_CODE`: Status code
- `STANDARD_SET_STATUS_ID`: Status identifier

**Metadata**:
- `IS_MOCK`: Mock data flag for testing
- `CDW_SOURCE`: Common Data Warehouse source

**Key Insight**: Each state has its own standard set (e.g., "CPR for TX" = Core Progress Reading for Texas). This is the **branching point** where master concepts split into state-specific variants.

---

## Schema Relationships

### Entity-Relationship Overview

```
Standard Sets (1) ──── (M) Standards (M) ──── (M) Skills
       │                      │                    │
       │                      │                    │
       └──(1)─(M) Domain Groups (1) ──── (M) Domains
                                                   │
                                              Skill Areas (organizational)
```

### Data Flow

1. **Education Authority** (e.g., Texas Education Agency) publishes **Standards**
2. Standards are grouped into **Standard Sets** (e.g., "CPR for TX")
3. Standards reference **Domains** and **Domain Groups** (from standards document structure)
4. ROCK team creates **Skills** that align to **Standards**
5. **Standard-Skills** table records many-to-many alignments
6. Skills are categorized into **Skill Areas** (flat organizational groups)

### Current Metadata Available

**What We Have**:
- ✅ Skills with comprehensive metadata (descriptions, grade levels, content areas, USP classification)
- ✅ Rich skill flags (focus skills, proficiency indicators, readiness markers, CBM)
- ✅ Skill areas (flat organizational groupings)
- ✅ Standards with full hierarchy, versioning, and Academic Benchmarks integration
- ✅ Domains and domain groups (organizational, within standard sets)
- ✅ Many-to-many skill-standard relationships with rich metadata
- ✅ STAR difficulty calibration at multiple performance levels
- ✅ DOK levels (cognitive complexity)
- ✅ Skill collections and intended collections
- ✅ Comprehensive versioning and change tracking

**What We DON'T Have**:
- ❌ Links to science-based master skills or learning progressions
- ❌ Taxonomic parent-child relationships between skills
- ❌ Conceptual similarity or equivalence metadata
- ❌ Prerequisite/progression relationships grounded in learning science
- ❌ Cognitive construct tags (e.g., "phonemic awareness", "place value", "inferencing")
- ❌ Evidence-based framework references (Science of Reading, CCSSM learning trajectories)
- ❌ Cross-state skill equivalence mappings

---

## Examples of Skill Redundancy Across States

### Example 1: Using Context Clues for Word Meaning

**Master Concept** (Science of Reading): *Contextual Word Learning* – using semantic and syntactic context to infer meanings of unfamiliar words.

**ROCK Skills** (conceptually identical, derived from different standards):

| Skill Name (abbreviated) | Grade | Education Authority | Skill Area |
|--------------------------|-------|---------------------|------------|
| Use context clues to determine word meaning | 3 | TX | Word Meaning |
| Determine meaning using context | 4 | CA | Vocabulary |
| Use context as clue to meaning of word or phrase | 5 | CCSS | Vocabulary Acquisition |
| Analyze context to infer meaning | 6 | OH | Word Analysis |

**Problem**: No metadata connects these four skills to the same underlying competency.

### Example 2: Phonemic Blending

**Master Concept** (Science of Reading): *Phoneme Blending* – blending individual phonemes into spoken words.

**ROCK Skills**:

| Skill Name (abbreviated) | Grade | Education Authority | Skill Area |
|--------------------------|-------|---------------------|------------|
| Blend phonemes to form words | K | CCSS | Blending and Segmenting |
| Blend 2-3 phonemes into recognizable words | K | TX | Phonological Awareness |
| Orally blend phonemes into one-syllable words | 1 | CA | Foundational Skills |
| Blend grade-appropriate words with greater phonemes | 2 | VA | Blending and Segmenting |

**Problem**: These are developmentally sequenced (increasing complexity), but ROCK has no formal progression metadata linking them as a learning trajectory.

### Example 3: Analyzing Text Structure

**Master Concept** (Literacy Framework): *Text Structure Analysis* – identifying and using organizational patterns (cause-effect, compare-contrast, etc.) to comprehend informational text.

**ROCK Skills**:

| Skill Name (abbreviated) | Grade | Education Authority | Skill Area |
|--------------------------|-------|---------------------|------------|
| Identify text structure (sequence, description) | 3 | TX | Text Features |
| Describe overall structure of events/ideas in text | 4 | CCSS | Craft and Structure |
| Analyze text structure and its effect on meaning | 5 | OH | Analysis and Comparison |
| Evaluate how text structure contributes to purpose | 6 | CA | Informational Analysis |

**Problem**: No connection to the evidence-based construct of "text structure knowledge" or to research on comprehension strategies.

---

## Impact of Missing Taxonomic Structure

### For Curriculum Developers
- **Cannot easily find all conceptually related skills** across states and grades
- **Must manually compare skill descriptions** to identify redundancy
- **Cannot leverage content across similar skills** without extensive mapping work
- **Difficulty designing coherent learning progressions** spanning grade levels

### For Product Teams
- **Duplicate content creation** for essentially identical skills
- **Inconsistent measurement** of the same underlying competency
- **Difficulty aggregating student performance data** across equivalent skills
- **Cannot build adaptive systems** that understand skill relationships

### For Research & Analytics
- **Cannot group data by master constructs** for research studies
- **Cross-state comparisons require manual coding** of skill equivalence
- **Learning progressions must be inferred** rather than formalized
- **Limited ability to validate assessment items** against learning science

### For Educators
- **Difficult to understand what students are actually learning** beyond state-specific language
- **Cannot easily see connections** between skills across grade levels
- **Hard to find appropriate interventions** when searching by concept rather than standard code
- **Limits understanding of coherent learning pathways**

---

## Comparison to Science-Based Taxonomies

### Science of Reading Taxonomy (Example)

The Science of Reading taxonomy provided has a hierarchical structure:

```
Strand (e.g., "Active Self-Regulation")
  └─ Pillar (e.g., "Executive Function Skills")
      └─ Domain (e.g., "Core Executive Processes")
          └─ Skill Area (e.g., "Cognitive Flexibility")
              └─ Skill Set (e.g., "Strategy Shifting")
                  └─ Skill Subset (e.g., "Switching Strategies Based on Task Demands")
```

**Key Differences from ROCK**:
- ✅ **Evidence-based**: Grounded in reading research and cognitive science
- ✅ **Hierarchical**: Clear parent-child relationships (6 levels)
- ✅ **Grade-independent**: Focuses on competencies, not grade-level standards
- ✅ **Comprehensive**: Covers cognitive, metacognitive, and motivational components
- ✅ **Consistent terminology**: No state-specific variations
- ✅ **Explicit examples**: Each skill includes concrete behavioral examples

**What ROCK Could Gain**:
- Skills linked to taxonomy nodes (e.g., SKILL_ID → SoR_Skill_Subset_ID)
- Automatic identification of conceptually equivalent skills
- Learning progressions defined by science, not state document order
- Cross-state curriculum alignment without manual mapping
- Research-grounded content development priorities

---

## Summary

The ROCK schema effectively captures:
- Skills and their state-standard derivations
- Standards from multiple education authorities with rich hierarchy
- Organizational domains and groupings (within standard sets)
- Many-to-many alignment relationships with comprehensive metadata
- STAR difficulty calibration and skill collections
- Extensive versioning and change tracking

The ROCK schema **lacks**:
- Taxonomic connections to evidence-based master skills
- Metadata for identifying conceptually equivalent skills across states
- Formalized learning progressions grounded in science
- Hierarchical skill relationships beyond flat organizational groupings

**Result**: Massive skill fragmentation where one science-based concept becomes 5-15 state-specific ROCK skills with no metadata linking them together.

**Next Steps**: See `master-skill-fragmentation.md` for a visual diagram of the problem and `problem-statement.md` for detailed analysis and quantification.
