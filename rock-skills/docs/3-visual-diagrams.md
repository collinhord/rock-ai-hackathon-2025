# The Compound ROCK Skills Problem

**Visual Diagrams**: How ROCK faces two interrelated architectural challenges—horizontal fragmentation and vertical granularity mismatch

---

## Overview: Two Dimensions of the Problem

ROCK Skills face a **compound architectural problem** with two distinct but related dimensions:

1. **Horizontal Fragmentation**: Same science-based concept → 8-15 redundant ROCK skills across states
2. **Vertical Granularity Mismatch**: ROCK skills too broad for daily instruction; P&I needs finer-grained objectives

**The Combined Effect**: ROCK is both redundant (too many similar skills) AND too coarse (each skill too broad for instruction), making it difficult to use for either discovery or daily teaching.

---

## Problem 1: Horizontal Fragmentation (Master Skill Redundancy)

The following diagram shows how a single evidence-based literacy competency (from the Science of Reading) branches into multiple state-specific standards, which then generate redundant ROCK skills **with no backward linkage to the master concept**.

```mermaid
graph LR
    %% Master Skill (Science of Reading)
    Master["<b>MASTER SKILL</b><br/>Contextual Word Learning<br/><i>(Science of Reading)</i><br/><br/>Using semantic and syntactic<br/>context to infer meanings<br/>of unfamiliar words"]
    
    %% State Legislative Filter
    Master -->|TX Legislature| TX_STD["TX Standard<br/>TEKS 3.4B<br/>'Use context to determine<br/>the relevant meaning of<br/>unfamiliar words'"]
    Master -->|CA Legislature| CA_STD["CA Standard<br/>CCSS.ELA-Literacy.L.4.4a<br/>'Use context as a clue<br/>to the meaning of a<br/>word or phrase'"]
    Master -->|OH Legislature| OH_STD["OH Standard<br/>RI.5.4<br/>'Determine the meaning of<br/>general academic and<br/>domain-specific words<br/>using context clues'"]
    Master -->|CCSS Adoption| CC_STD["Common Core<br/>CCSS.ELA-Literacy.L.4.4a<br/>'Use context (e.g., definitions,<br/>examples) as a clue to the<br/>meaning of a word'"]
    Master -->|VA Legislature| VA_STD["VA Standard<br/>3.4.d<br/>'Use context to clarify<br/>meaning of unfamiliar<br/>words and phrases'"]
    
    %% ROCK Skills Derived from Standards
    TX_STD -->|ROCK derives| TX_SKILL["<b>ROCK Skill (TX)</b><br/>Use context clues to<br/>determine word meaning<br/><i>Grade 3</i>"]
    CA_STD -->|ROCK derives| CA_SKILL["<b>ROCK Skill (CA)</b><br/>Determine meaning using<br/>context<br/><i>Grade 4</i>"]
    OH_STD -->|ROCK derives| OH_SKILL["<b>ROCK Skill (OH)</b><br/>Analyze context to infer<br/>word meaning<br/><i>Grade 5</i>"]
    CC_STD -->|ROCK derives| CC_SKILL["<b>ROCK Skill (CCSS)</b><br/>Use context as clue to<br/>meaning of word or phrase<br/><i>Grade 4</i>"]
    VA_STD -->|ROCK derives| VA_SKILL["<b>ROCK Skill (VA)</b><br/>Clarify meaning using<br/>textual context<br/><i>Grade 3</i>"]
    
    %% Missing Backward Link
    TX_SKILL -.->|❌ NO METADATA<br/>LINKING BACK| Master
    CA_SKILL -.->|❌ NO METADATA<br/>LINKING BACK| Master
    OH_SKILL -.->|❌ NO METADATA<br/>LINKING BACK| Master
    CC_SKILL -.->|❌ NO METADATA<br/>LINKING BACK| Master
    VA_SKILL -.->|❌ NO METADATA<br/>LINKING BACK| Master
    
    %% Styling
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef stateStyle fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef skillStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    
    class Master masterStyle
    class TX_STD,CA_STD,OH_STD,CC_STD,VA_STD stateStyle
    class TX_SKILL,CA_SKILL,OH_SKILL,CC_SKILL,VA_SKILL skillStyle
```

---

## What the Diagram Shows

### Left: Science-Based Master Skill
**The Source of Truth**
- Evidence-based competency from learning science (Science of Reading, Mathematics Learning Progressions, etc.)
- Grade-independent conceptual definition
- Grounded in research on how students learn
- Example: "Contextual Word Learning" – using context to infer word meanings

### Middle: State Legislative Filter
**The Fragmentation Layer**
- Each state legislature creates its own standards document
- Standards express the master concept with:
  - Different terminology ("context clues" vs. "textual context" vs. "surrounding words")
  - Different scope (some narrow, some broad)
  - Different grade-level assignments (Grade 3 vs. Grade 4 vs. Grade 5)
  - Different performance indicators
- Common Core State Standards (CCSS) attempted uniformity, but:
  - Not all states adopted CCSS
  - States that adopted CCSS still created supplemental standards
  - Even CCSS-aligned skills show variation in implementation

### Right: ROCK Skills (Fragmented Endpoints)
**The Redundancy Problem**
- ROCK creates skills by mapping to state standards
- **Result**: 5-15+ ROCK skills teaching the same underlying competency
- Each skill is independently defined with:
  - Unique SKILL_ID
  - State-specific description
  - Different grade-level defaults
  - Separate content libraries
  - Independent assessment items
- **Critical Gap**: No field or metadata linking skills back to master concept

### Bottom: Missing Backward Linkage (Dotted Lines)
**The Core Problem**
- ❌ No taxonomic metadata connecting ROCK skills to master competencies
- ❌ No Science of Reading taxonomy references
- ❌ No cognitive construct tags
- ❌ No equivalence or similarity metadata
- ❌ No learning progression hierarchies

**Impact**: You cannot programmatically ask ROCK:
- "Show me all skills that teach contextual word learning"
- "What are the conceptually equivalent skills across states?"
- "Which skills form a developmental progression for this competency?"
- "Are we missing coverage of any Science of Reading components?"

---

## Real-World Example: Phonemic Blending

```mermaid
graph LR
    %% Master Skill
    Master["<b>MASTER SKILL</b><br/>Phoneme Blending<br/><i>(Science of Reading:<br/>Phonological Awareness)</i><br/><br/>Blending individual phonemes<br/>into spoken words"]
    
    %% Standards
    Master -->|CCSS| CCSS["CCSS.ELA-Literacy.RF.K.2c<br/>'Blend two to three phonemes<br/>into recognizable words'"]
    Master -->|TX TEKS| TX["TX TEKS K.2.A.iv<br/>'Blend spoken phonemes<br/>to form one-syllable words'"]
    Master -->|CA Standards| CA["CA RF.K.2.c<br/>'Orally blend two to three<br/>phonemes into words'"]
    Master -->|VA SOL| VA["VA K.4<br/>'Blend sounds to make<br/>one-syllable words'"]
    
    %% ROCK Skills
    CCSS --> CCSS_SKILL["<b>ROCK Skill</b><br/>Blend phonemes to<br/>form words<br/><i>Grade K</i>"]
    TX --> TX_SKILL["<b>ROCK Skill</b><br/>Blend spoken phonemes<br/>into one-syllable words<br/><i>Grade K</i>"]
    CA --> CA_SKILL["<b>ROCK Skill</b><br/>Orally blend 2-3 phonemes<br/>into recognizable words<br/><i>Grade K</i>"]
    VA --> VA_SKILL["<b>ROCK Skill</b><br/>Blend sounds to make<br/>one-syllable words<br/><i>Grade K</i>"]
    
    %% Missing Links
    CCSS_SKILL -.->|❌ NO LINK TO<br/>SoR TAXONOMY| Master
    TX_SKILL -.->|❌ NO LINK TO<br/>SoR TAXONOMY| Master
    CA_SKILL -.->|❌ NO LINK TO<br/>SoR TAXONOMY| Master
    VA_SKILL -.->|❌ NO LINK TO<br/>SoR TAXONOMY| Master
    
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef stateStyle fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef skillStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    
    class Master masterStyle
    class CCSS,TX,CA,VA stateStyle
    class CCSS_SKILL,TX_SKILL,CA_SKILL,VA_SKILL skillStyle
```

**Observation**: All four skills teach the same foundational competency (phoneme blending) at the same grade level (K), but ROCK treats them as distinct, unrelated skills.

---

## Real-World Example: Text Structure Analysis

```mermaid
graph LR
    %% Master Skill
    Master["<b>MASTER SKILL</b><br/>Text Structure Knowledge<br/><i>(Comprehension Research)</i><br/><br/>Identifying and using<br/>organizational patterns<br/>(cause-effect, compare-contrast,<br/>sequence, description)<br/>to comprehend text"]
    
    %% Standards (showing progression and variation)
    Master -->|TX Grade 3| TX3["TX TEKS 3.9.D.i<br/>'Recognize organizational<br/>patterns such as sequence<br/>and description'"]
    Master -->|CCSS Grade 4| CC4["CCSS.ELA-Literacy.RI.4.5<br/>'Describe overall structure<br/>of events, ideas, concepts'"]
    Master -->|OH Grade 5| OH5["OH RI.5.5<br/>'Compare and contrast the<br/>structure of two or more texts'"]
    Master -->|CA Grade 6| CA6["CA RH.6-8.5<br/>'Analyze how text structure<br/>contributes to author's<br/>development of ideas'"]
    
    %% ROCK Skills (showing developmental spread)
    TX3 --> TX3_SKILL["<b>ROCK Skill</b><br/>Identify text structure<br/>(sequence, description)<br/><i>Grade 3</i>"]
    CC4 --> CC4_SKILL["<b>ROCK Skill</b><br/>Describe overall structure<br/>of events/ideas in text<br/><i>Grade 4</i>"]
    OH5 --> OH5_SKILL["<b>ROCK Skill</b><br/>Compare and contrast<br/>structure of two texts<br/><i>Grade 5</i>"]
    CA6 --> CA6_SKILL["<b>ROCK Skill</b><br/>Analyze how structure<br/>contributes to development<br/><i>Grade 6</i>"]
    
    %% Missing Progression Links
    TX3_SKILL -.->|❌ NO PROGRESSION<br/>METADATA| Master
    CC4_SKILL -.->|❌ NO PROGRESSION<br/>METADATA| Master
    OH5_SKILL -.->|❌ NO PROGRESSION<br/>METADATA| Master
    CA6_SKILL -.->|❌ NO PROGRESSION<br/>METADATA| Master
    
    TX3_SKILL -.->|Should be linked<br/>as developmental<br/>progression| CC4_SKILL
    CC4_SKILL -.->|Should be linked<br/>as developmental<br/>progression| OH5_SKILL
    OH5_SKILL -.->|Should be linked<br/>as developmental<br/>progression| CA6_SKILL
    
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef stateStyle fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef skillStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    
    class Master masterStyle
    class TX3,CC4,OH5,CA6 stateStyle
    class TX3_SKILL,CC4_SKILL,OH5_SKILL,CA6_SKILL skillStyle
```

**Observation**: These skills form a clear developmental progression (identify → describe → compare → analyze), but ROCK has no formal progression metadata. They can only be discovered by manual inspection.

---

## Problem 2: Vertical Granularity Mismatch (Assessment vs. Instruction)

The following diagram shows how ROCK skills, optimized for periodic assessment, are **too broad and coarse** for daily instructional use, forcing P&I teams to bypass ROCK entirely.

```mermaid
graph TB
    subgraph "Science-Based Master Skills"
        Master["<b>MASTER SKILL</b><br/>Phoneme Blending<br/><i>(Science of Reading)</i>"]
    end
    
    subgraph "ROCK Layer (Assessment-Optimized)"
        ROCK1["<b>ROCK Skill</b><br/>Blend phonemes to form words<br/><i>BROAD - Measured periodically</i><br/><i>Star Assessment dependency</i>"]
        ROCK2["<b>ROCK Skill</b><br/>Blend spoken phonemes<br/>into one-syllable words<br/><i>BROAD - Measured periodically</i>"]
    end
    
    subgraph "P&I Needs (Instruction-Level)"
        PI1["<b>Daily Lesson 1</b><br/>Blend 2 phonemes<br/><i>(/c/ + /at/ = cat)</i><br/><i>Day 1 objective</i>"]
        PI2["<b>Daily Lesson 2</b><br/>Blend 3 phonemes<br/><i>(/s/ + /i/ + /t/ = sit)</i><br/><i>Day 2 objective</i>"]
        PI3["<b>Daily Lesson 3</b><br/>Blend initial consonant blends<br/><i>(/st/ + /op/ = stop)</i><br/><i>Day 3 objective</i>"]
        PI4["<b>Daily Lesson 4</b><br/>Blend with digraphs<br/><i>(/sh/ + /ip/ = ship)</i><br/><i>Day 4 objective</i>"]
        PI5["<b>Curriculum-Specific</b><br/>McGraw-Hill Wonders<br/>Unit 1, Lesson 3<br/><i>Publisher alignment</i>"]
    end
    
    Master --> ROCK1
    Master --> ROCK2
    
    ROCK1 -.->|"❌ TOO BROAD<br/>Cannot support<br/>daily lessons"| PI1
    ROCK1 -.->|"❌ TOO BROAD<br/>Cannot support<br/>daily lessons"| PI2
    ROCK2 -.->|"❌ TOO BROAD<br/>Cannot support<br/>daily lessons"| PI3
    ROCK2 -.->|"❌ TOO BROAD<br/>Cannot support<br/>daily lessons"| PI4
    ROCK1 -.->|"❌ NOT CURRICULUM<br/>ALIGNED"| PI5
    
    PI1 -->|"P&I teams<br/>bypass ROCK"| Custom["<b>CUSTOM P&I SKILLS</b><br/>Built from scratch<br/><i>No reuse of ROCK</i><br/><i>Duplicate infrastructure</i>"]
    PI2 -->|"P&I teams<br/>bypass ROCK"| Custom
    PI3 -->|"P&I teams<br/>bypass ROCK"| Custom
    PI4 -->|"P&I teams<br/>bypass ROCK"| Custom
    PI5 -->|"P&I teams<br/>bypass ROCK"| Custom
    
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef rockStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    classDef piStyle fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff
    classDef customStyle fill:#F44336,stroke:#B71C1C,stroke-width:3px,color:#fff
    
    class Master masterStyle
    class ROCK1,ROCK2 rockStyle
    class PI1,PI2,PI3,PI4,PI5 piStyle
    class Custom customStyle
```

### What This Diagram Shows

**Top: Master Skill (Science of Reading)**
- Evidence-based competency: Phoneme Blending

**Middle: ROCK Skills (Assessment Context)**
- Broad, assessable competencies
- Measured weekly/monthly/semester
- Optimized for Star Assessment (business lock-in)
- **Problem**: Too coarse for daily instruction

**Bottom: P&I Instructional Needs**
- Fine-grained, daily lesson objectives
- Curriculum-specific alignments (McGraw-Hill, Houghton Mifflin, etc.)
- 1-3 day lesson cycles
- **Gap**: ROCK cannot support this granularity

**Right: The Bypass**
- P&I teams build custom skills from scratch
- Complete duplication of infrastructure
- No reuse of ROCK relationships or metadata
- Ecosystem fragmentation

### The Business Constraint

**ROCK is Immutable Because:**
- Star Assessments (primary revenue) depend on current structure
- Years of historical student data tied to existing skills
- Any modification risks data integrity and business continuity
- Revenue protection makes ROCK untouchable

**Result**: Cannot modify ROCK to serve P&I needs. Must build around it.

---

## Problem 3: The Compound Effect

The following diagram shows how **both problems together** create an impossible situation:

```mermaid
graph TB
    subgraph "Science-Based Master Skills"
        Master["<b>MASTER SKILL</b><br/>Using Context Clues<br/>for Word Meaning<br/><i>(Science of Reading)</i>"]
    end
    
    subgraph "Horizontal Fragmentation"
        direction LR
        ROCK_TX["TX ROCK Skill<br/><i>Grade 3</i><br/>TOO BROAD"]
        ROCK_CA["CA ROCK Skill<br/><i>Grade 4</i><br/>TOO BROAD"]
        ROCK_OH["OH ROCK Skill<br/><i>Grade 5</i><br/>TOO BROAD"]
        ROCK_VA["VA ROCK Skill<br/><i>Grade 3</i><br/>TOO BROAD"]
        ROCK_CC["CCSS ROCK Skill<br/><i>Grade 4</i><br/>TOO BROAD"]
    end
    
    subgraph "P&I Instructional Needs (Vertical)"
        PI_Day1["Day 1: Identify<br/>definition context clues"]
        PI_Day2["Day 2: Identify<br/>synonym context clues"]
        PI_Day3["Day 3: Identify<br/>antonym context clues"]
        PI_Day4["Day 4: Identify<br/>example context clues"]
        PI_Day5["Day 5: Combine<br/>multiple clue types"]
    end
    
    Master -->|"State filter"| ROCK_TX
    Master -->|"State filter"| ROCK_CA
    Master -->|"State filter"| ROCK_OH
    Master -->|"State filter"| ROCK_VA
    Master -->|"State filter"| ROCK_CC
    
    ROCK_TX -.->|"❌ TOO BROAD"| PI_Day1
    ROCK_CA -.->|"❌ TOO BROAD"| PI_Day2
    ROCK_OH -.->|"❌ TOO BROAD"| PI_Day3
    ROCK_VA -.->|"❌ TOO BROAD"| PI_Day4
    ROCK_CC -.->|"❌ TOO BROAD"| PI_Day5
    
    ROCK_TX -.->|"❌ NO LINK"| Master
    ROCK_CA -.->|"❌ NO LINK"| Master
    ROCK_OH -.->|"❌ NO LINK"| Master
    ROCK_VA -.->|"❌ NO LINK"| Master
    ROCK_CC -.->|"❌ NO LINK"| Master
    
    PI_Day1 --> Bypass["<b>COMPLETE BYPASS</b><br/><br/>P&I teams build<br/>custom skills<br/><br/>Cannot use<br/>fragmented,<br/>too-broad ROCK"]
    PI_Day2 --> Bypass
    PI_Day3 --> Bypass
    PI_Day4 --> Bypass
    PI_Day5 --> Bypass
    
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef rockStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    classDef piStyle fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff
    classDef bypassStyle fill:#F44336,stroke:#B71C1C,stroke-width:4px,color:#fff
    
    class Master masterStyle
    class ROCK_TX,ROCK_CA,ROCK_OH,ROCK_VA,ROCK_CC rockStyle
    class PI_Day1,PI_Day2,PI_Day3,PI_Day4,PI_Day5 piStyle
    class Bypass bypassStyle
```

### The Compound Problem Analysis

**Challenge 1: Too Many Similar Skills (Horizontal)**
- 5 ROCK skills teaching the same concept
- No metadata linking them
- Cannot discover conceptually equivalent skills
- **Impact**: 60-75% redundancy, difficult to navigate

**Challenge 2: Each Skill Too Broad (Vertical)**
- ROCK skills optimized for periodic assessment
- P&I needs daily, granular objectives
- One ROCK skill must decompose into 5-10 P&I lessons
- **Impact**: Cannot support daily instruction

**Challenge 3: Business Lock-In**
- Star Assessment depends on ROCK
- Historical data tied to existing skills
- Cannot modify ROCK without business risk
- **Impact**: Problems cannot be fixed at source

**Combined Effect:**
1. Curriculum developers search for "context clues" skills
2. Find 5-12 fragmented ROCK skills (redundancy problem)
3. Each ROCK skill still too broad for daily lessons (granularity problem)
4. Cannot modify ROCK to fix either issue (business constraint)
5. **Result**: P&I teams bypass ROCK entirely, build custom infrastructure from scratch

---

## The Structural Problem Summary

### Current State: Standards-Driven Architecture
```
State Standards (PRIMARY) 
    ↓ (derivation)
ROCK Skills (SECONDARY)
    ↓ (no link)
Master Science-Based Skills (ORPHANED)
```

### Desired State: Science-Driven Architecture
```
Master Science-Based Skills (PRIMARY)
    ↓ (taxonomy link)
ROCK Skills (SECONDARY)
    ↓ (alignment link)
State Standards (TERTIARY)
```

### Key Architectural Issues

1. **No Taxonomy Root**
   - Skills have no parent/child relationships
   - Cannot traverse a hierarchy from general to specific
   - Flat structure with only loose groupings (SKILL_AREA_NAME)

2. **No Equivalence Metadata**
   - Cannot identify skills that teach the same concept
   - Must rely on text similarity (brittle, language-dependent)
   - No cross-state skill mapping tables

3. **No Learning Progression Encoding**
   - Developmental sequences exist but are implicit
   - Prerequisite relationships not formalized
   - Cannot programmatically build learning pathways

4. **No Evidence-Based Framework References**
   - No links to Science of Reading taxonomy
   - No references to mathematics learning progressions
   - No connections to cognitive science constructs

---

## Consequences of Fragmentation

### Data Volume Impact
- **1 Master Concept** → **~8-15 ROCK Skills** (average across literacy/math concepts)
- **Estimated Redundancy Ratio**: 60-75% of ROCK skills are conceptual duplicates
- **Hidden Equivalent Skills**: Educators searching for "phonemic awareness" skills might find 5 but miss 8 others using different terminology

### Operational Impact
- **Content Development**: Teams create items/lessons for 12 "different" skills that teach the same thing
- **Product Integration**: Systems cannot automatically recommend equivalent skills across state configurations
- **Analytics**: Cannot aggregate learning data at the master-concept level
- **Curriculum Design**: Manual mapping required to identify learning progressions

### Strategic Impact
- **Competitive Disadvantage**: Competitors with taxonomy-driven architectures can offer superior content discovery and personalization
- **Research Limitations**: Cannot validate products against learning science frameworks at scale
- **Scalability Issues**: Adding new states/standards increases fragmentation linearly

---

## What a Solution Would Need (Conceptual Framework)

To address **both** the horizontal and vertical problems without modifying ROCK (business constraint), a solution would need:

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│  Science of Reading Taxonomy (NEW LAYER)        │
│  - Evidence-based master skills                 │
│  - Hierarchical structure                       │
│  - Grade-independent competencies               │
└─────────────────────────────────────────────────┘
         ↕ (mapping metadata)
┌─────────────────────────────────────────────────┐
│  ROCK Skills (PRESERVED AS-IS)                  │
│  - Assessment-level, broad competencies         │
│  - Fragmented across states (unchanged)         │
│  - Star dependency protected                    │
└─────────────────────────────────────────────────┘
         ↕ (decomposition metadata)
┌─────────────────────────────────────────────────┐
│  P&I Instructional Objectives (NEW LAYER)       │
│  - Daily lesson-level granularity               │
│  - Curriculum-specific alignments               │
│  - 1-3 day instructional cycles                 │
└─────────────────────────────────────────────────┘
```

### How This Addresses Both Problems

**For Horizontal Fragmentation:**
- Taxonomy layer groups 8-15 fragmented ROCK skills under single master concept
- Enables discovery: "Show all ROCK skills teaching phoneme blending"
- Provides conceptual equivalence metadata across states
- Does NOT modify ROCK—adds metadata layer above it

**For Vertical Granularity:**
- Taxonomy provides decomposition structure for P&I
- Master concept → ROCK skills (assessment) + P&I objectives (instruction)
- Enables: "Given this master skill, generate daily lesson objectives"
- Does NOT modify ROCK—adds P&I layer below it via taxonomy

**Preserving Business Constraints:**
- ✅ ROCK remains unchanged (Star protected)
- ✅ Historical data integrity maintained
- ✅ All existing ROCK relationships preserved
- ✅ New layers added via external metadata, not schema changes

### Implementation Reality

**Phase 1: Taxonomy Bridge**
- Map ROCK skills to Science of Reading taxonomy nodes
- Create equivalence groups for fragmented skills
- Enable conceptual search and grouping

**Phase 2: P&I Decomposition**
- Use taxonomy to generate curriculum-aligned objectives
- Create P&I skill layer linked through taxonomy
- Enable daily instructional support

**Phase 3: Dual-Track Integration**
- Assessment track: Taxonomy → ROCK → Star (unchanged)
- Instruction track: Taxonomy → P&I Objectives → Curriculum (new)
- Bridge: Both tracks connect through shared taxonomy

**Success Criteria:**
1. ✅ ROCK never modified (Star protected)
2. ✅ Can discover conceptually equivalent ROCK skills
3. ✅ Can generate appropriate-granularity P&I objectives
4. ✅ Both use same science-based taxonomy foundation
5. ✅ Ecosystem integration via taxonomy, not ROCK modification

---

## Key Insight: Why Science of Reading Taxonomy Solves Both

The Science of Reading taxonomy can serve as the **bridge layer** in a dual-track architecture:

**For Assessment (ROCK):**
- Map upward from fragmented ROCK skills to master concepts
- Group conceptually equivalent skills
- Enable research-grounded analysis

**For Instruction (P&I):**
- Decompose downward from master concepts to daily objectives
- Generate curriculum-aligned fine-grained skills
- Enable daily lesson support

**The Critical Point:**
This is not optimal system design from first principles—it's architectural creativity under business constraints. Renaissance must build around ROCK, not through it.

**Note**: This document focuses on **problem visualization**. See `problem-statement.md` for quantitative analysis and detailed impact assessment.

