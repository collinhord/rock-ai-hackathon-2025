# Problem-Solution Integration: Three-Level Approach

**ROCK AI Hackathon 2025**

This diagram shows how MICRO, MID, and MACRO levels work together to solve the horizontal fragmentation problem.

---

## Complete Problem-Solution Diagram

```mermaid
graph TB
    %% ===== THE PROBLEM: Horizontal Fragmentation =====
    subgraph Problem["🚨 THE PROBLEM: Horizontal Fragmentation"]
        direction TB
        
        Master["<b>BASE SKILL</b><br/>(Science of Reading)<br/><br/>Use Context Clues<br/><br/>Core competency: Using semantic<br/>and syntactic context to infer<br/>meanings of unfamiliar words"]
        
        %% State Standards Layer
        TX_STD["TX Standard<br/>TEKS 3.4B<br/>'Use context to determine<br/>relevant meaning'"]
        CA_STD["CA Standard<br/>CCSS.ELA-Literacy.L.4.4a<br/>'Use context as clue<br/>to meaning'"]
        OH_STD["OH Standard<br/>RI.5.4<br/>'Determine meaning using<br/>context clues'"]
        VA_STD["VA Standard<br/>3.4.d<br/>'Use context to clarify<br/>meaning'"]
        
        %% ROCK Skills (Fragmented) = BASE + Specs
        TX_SKILL["<b>ROCK Skill (TX)</b><br/>BASE: Use Context Clues<br/>━━━━━━━━━━━━━━━<br/>• Grade: 3<br/>• State: TX<br/>• Text type: informational<br/>• Domain: reading"]
        CA_SKILL["<b>ROCK Skill (CA)</b><br/>BASE: Use Context Clues<br/>━━━━━━━━━━━━━━━<br/>• Grade: 4<br/>• State: CA<br/>• Text type: informational<br/>• Domain: reading"]
        OH_SKILL["<b>ROCK Skill (OH)</b><br/>BASE: Use Context Clues<br/>━━━━━━━━━━━━━━━<br/>• Grade: 5<br/>• State: OH<br/>• Text type: academic<br/>• Domain: reading"]
        VA_SKILL["<b>ROCK Skill (VA)</b><br/>BASE: Use Context Clues<br/>━━━━━━━━━━━━━━━<br/>• Grade: 3<br/>• State: VA<br/>• Text type: informational<br/>• Domain: reading"]
        
        Master --> TX_STD
        Master --> CA_STD
        Master --> OH_STD
        Master --> VA_STD
        
        TX_STD --> TX_SKILL
        CA_STD --> CA_SKILL
        OH_STD --> OH_SKILL
        VA_STD --> VA_SKILL
        
        %% Missing backward links (the problem!)
        TX_SKILL -.->|"❌ NO LINK"| Master
        CA_SKILL -.->|"❌ NO LINK"| Master
        OH_SKILL -.->|"❌ NO LINK"| Master
        VA_SKILL -.->|"❌ NO LINK"| Master
    end
    
    %% ===== MICRO LEVEL: Extract Metadata =====
    subgraph Micro["🔬 MICRO LEVEL: Metadata Extraction (Jess)"]
        direction TB
        
        MicroDesc["<b>Extract Structured Metadata</b><br/>from each ROCK skill using spaCy NLP"]
        
        TX_META["TX Metadata:<br/>• Action: use, determine<br/>• Target: context, clues, meaning<br/>• Domain: reading<br/>• Text type: informational"]
        CA_META["CA Metadata:<br/>• Action: determine<br/>• Target: meaning, context<br/>• Domain: reading<br/>• Text type: informational"]
        OH_META["OH Metadata:<br/>• Action: analyze, infer<br/>• Target: context, meaning<br/>• Domain: reading<br/>• Text type: academic"]
        VA_META["VA Metadata:<br/>• Action: clarify<br/>• Target: meaning, context<br/>• Domain: reading<br/>• Text type: informational"]
        
        MicroDesc --> TX_META
        MicroDesc --> CA_META
        MicroDesc --> OH_META
        MicroDesc --> VA_META
    end
    
    %% ===== MID LEVEL: Detect Redundancy =====
    subgraph Mid["🔍 MID LEVEL: Redundancy Detection (Savannah)"]
        direction TB
        
        MidDesc["<b>Concept-Aware Similarity Detection</b><br/>Compare skills using text + concept overlap"]
        
        Comparison["Similarity Analysis:<br/>• TX vs CA: 0.88 (same actions/targets)<br/>• TX vs OH: 0.85 (same core concept)<br/>• TX vs VA: 0.87 (same domain)<br/>• All 4 skills: Grade 3-5, reading, context"]
        
        RedundancyGroup["<b>REDUNDANCY GROUP</b><br/>RED-001: Context Clues<br/><br/>4 state variants identified:<br/>TX, CA, OH, VA<br/><br/>Avg similarity: 0.87<br/>Type: Cross-state variants"]
        
        MidDesc --> Comparison
        Comparison --> RedundancyGroup
    end
    
    %% ===== MACRO LEVEL: Extract BASE Skill + Specifications =====
    subgraph Macro["🎯 MACRO LEVEL: BASE Skill + Specification Extraction (Collin)"]
        direction TB
        
        MacroDesc["<b>Extract Base Skill + Map to Framework</b><br/>Decompose variants into BASE + specs"]
        
        BaseSkill["BASE Skill Extracted:<br/>'Use Context Clues'<br/><br/>Core competency:<br/>Using context to determine<br/>word meaning"]
        
        Framework["Map to Framework:<br/>Science of Reading Path:<br/>Language Comprehension ><br/>Vocabulary > Context Clues ><br/>Using Semantic Context"]
        
        BaseSpecs["<b>✅ BASE SKILL + SPECIFICATION TAXONOMY</b><br/>━━━━━━━━━━━━━━━━━━━━━━<br/>BASE: Use Context Clues<br/>━━━━━━━━━━━━━━━━━━━━━━<br/>SPECIFICATIONS:<br/>• Primary: text_type, complexity, domain<br/>• Secondary: text_mode, support<br/>• Tertiary: scope, quantity<br/>━━━━━━━━━━━━━━━━━━━━━━<br/>ROCK Mappings: 4 skills<br/>States: TX, CA, OH, VA<br/>Grades: 3-5"]
        
        MacroDesc --> BaseSkill
        BaseSkill --> Framework
        Framework --> BaseSpecs
    end
    
    %% ===== SOLUTION: Bridge Created =====
    subgraph Solution["✅ THE SOLUTION: Bridge Created"]
        direction LR
        
        Bridge["<b>Cross-State Bridge</b><br/><br/>1 BASE Skill + Spec Taxonomy ←→ 4 ROCK Skills<br/><br/>Content tagged once to BASE →<br/>Discoverable across all 4 states<br/><br/>Scientific grounding →<br/>Links back to SoR taxonomy"]
        
        PIValue["<b>P&I Value Delivered</b><br/><br/>• Tag content to BASE skill<br/>• Filter by specifications<br/>• Discover in TX, CA, OH, VA<br/>• Track learning progressions<br/>• Scale efficiently"]
        
        Bridge --> PIValue
    end
    
    %% ===== DATA FLOW: Problem → Solution =====
    TX_SKILL --> MicroDesc
    CA_SKILL --> MicroDesc
    OH_SKILL --> MicroDesc
    VA_SKILL --> MicroDesc
    
    TX_META --> MidDesc
    CA_META --> MidDesc
    OH_META --> MidDesc
    VA_META --> MidDesc
    
    RedundancyGroup --> MacroDesc
    
    BaseSpecs --> Bridge
    
    %% ===== BACKWARD LINK CREATED =====
    BaseSpecs ==>|"✅ BRIDGE CREATED"| Master
    
    %% Styling
    classDef problemStyle fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef masterStyle fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    classDef stateStyle fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef skillStyle fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    classDef microStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef midStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef macroStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef solutionStyle fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,font-weight:bold
    
    class Master masterStyle
    class TX_STD,CA_STD,OH_STD,VA_STD stateStyle
    class TX_SKILL,CA_SKILL,OH_SKILL,VA_SKILL skillStyle
    class MicroDesc,TX_META,CA_META,OH_META,VA_META microStyle
    class MidDesc,Comparison,RedundancyGroup midStyle
    class MacroDesc,BaseSkill,Framework,BaseSpecs macroStyle
    class Bridge,PIValue solutionStyle
```

---

## How the Three Levels Solve the Problem

### The Problem (Top Section)
**Horizontal Fragmentation**: One Science of Reading BASE skill → 50+ state standards → 4-15 ROCK skills **with no backward link**

In this example:
- **1 BASE Skill**: "Use Context Clues" (Science of Reading)
- **4 State Standards**: TX, CA, OH, VA (different wording, different grades)
- **4 ROCK Skills**: Each = BASE + different specifications (grade, state, text_type)
- **❌ Problem**: Can't discover cross-state equivalents, can't scale content, no scientific grounding

---

### MICRO Level (Jess): Extract Metadata
**What it does**: Uses spaCy NLP to extract structured concepts from each ROCK skill

**For each skill, extract**:
- **Actions**: use, determine, analyze, clarify, infer
- **Targets**: context, clues, meaning, words
- **Qualifiers**: informational, academic, textual
- **Metadata**: text_type, complexity, domain, support_level

**Value**: Transforms unstructured text → structured data that MID level can analyze

**Result**: 4 enriched skill records with comparable metadata

---

### MID Level (Savannah): Detect Redundancy
**What it does**: Uses concept-aware similarity to detect that these 4 skills are variants

**Similarity Analysis**:
```
TX vs CA: 0.88 (both: determine meaning using context)
TX vs OH: 0.85 (both: analyze context for word meaning)
TX vs VA: 0.87 (both: clarify meaning from context)
All share: reading domain, informational text, grades 3-5
```

**Detection Logic**:
- Text similarity: ~0.70 (good but not perfect)
- **+ Concept overlap**: ~0.95 (same actions/targets)
- **+ Context match**: same domain, grade band, text type
- **= Enhanced similarity**: ~0.87 → **Flagged as redundant variants**

**Value**: Groups cross-state equivalents that text-only similarity would miss

**Result**: Redundancy Group RED-001 with 4 variant skills

---

### MACRO Level (Collin): Extract BASE Skill + Specification Taxonomy
**What it does**: Decomposes variant group into BASE skill + hierarchical specification taxonomy, maps to Science of Reading

**BASE Skill Extraction**:
- Remove state-specific wording
- Remove grade qualifiers
- Extract core competency: **"Use Context Clues"**
- Formula: ROCK Skill = BASE + Specifications

**Specification Taxonomy Extraction**:
- **Primary specs**: text_type=informational, complexity=3-5, domain=reading
- **Secondary specs**: text_mode=prose, support=independent
- **Tertiary specs**: scope=word_level, quantity=single

**Framework Mapping**:
- Science of Reading Path: Language Comprehension > Vocabulary > Context Clues > Using Semantic Context
- Pedagogical metadata: Bloom's=Application, Webb's DOK=2

**Value**: Separates WHAT (base skill) from WHERE/WHEN/HOW (specifications), enabling flexible content tagging

**Result**: BASE skill + specification taxonomy linking 4 ROCK skills to SoR taxonomy

---

### The Solution (Bottom Section)
**✅ Bridge Created**: BASE skill + specification taxonomy serves as bridge linking ROCK skills to scientific framework

**Cross-State Bridge Enabled**:
- 1 BASE Skill + Spec Taxonomy ←→ 4 ROCK Skills (TX, CA, OH, VA)
- Content tagged once to BASE skill → discoverable across all specification variants
- Scientific grounding via Science of Reading mapping
- Learning progressions tracked via complexity specifications

**P&I Value Delivered**:
- **Tag content once**: "Context Clues Lesson Plan" → BASE skill
- **Filter by specs**: Choose text_type, complexity, domain as needed
- **Discover everywhere**: TX, CA, OH, VA users can all find it
- **Track progressions**: Complexity 3-5, can scale to 6-8, 9-12
- **Scale efficiently**: 60-80% reduction in tagging effort
- **Scientific validation**: Grounded in evidence-based framework

---

## Key Insight: Sequential Problem-Solving

Each level solves a problem that enables the next:

**Without MICRO**:
- MID can only use text similarity → misses "determine meaning" ≈ "clarify meaning" ≈ "infer meaning"
- Result: 15-20% false negatives, variants not grouped

**Without MID**:
- MACRO processes 8,000 skills individually → 300+ potential base skills with duplicates
- Result: Manual deduplication needed, cross-state variants missed

**Without MACRO**:
- No BASE skill to serve as bridge → content must be tagged to individual state skills
- Result: 4x duplication, no cross-state discovery, no scientific grounding

**With All Three**:
- ✅ MICRO extracts comparable metadata
- ✅ MID groups cross-state variants
- ✅ MACRO decomposes into BASE skill + specification taxonomy
- ✅ P&I can tag to BASE, filter by specs, scale content efficiently

---

## From Problem to Solution: The Complete Flow

```
🚨 PROBLEM
   Fragmented ROCK Skills (no backward link to BASE skill)
      ↓
🔬 MICRO extracts metadata
   4 skills → 4 enriched records with structured concepts
      ↓
🔍 MID detects redundancy
   4 enriched records → 1 variant group (similarity: 0.87)
      ↓
🎯 MACRO decomposes into BASE + specs
   1 variant group → 1 BASE skill + specification taxonomy + SoR mapping
      ↓
✅ SOLUTION
   BASE skill + specs bridges ROCK skills ←→ Science of Reading
   Content scales across 4 states, scientific grounding achieved
```

---

## Example: Concrete Before/After

### Before Integration
```
Curriculum Developer wants to create "Context Clues" lesson

Step 1: Search ROCK for "context clues"
Result: Find 12-15 skills, unclear which are equivalent

Step 2: Manually analyze each skill
Time: 2-3 hours per concept

Step 3: Pick one state's skill to tag content
Result: Content only discoverable in that state (49 states miss it)

Step 4: No scientific grounding
Problem: Can't validate against learning science
```

### After Integration
```
Curriculum Developer wants to create "Context Clues" lesson

Step 1: Search BASE skills for "context clues"
Result: Find BASE skill with 4 state mappings + specification taxonomy

Step 2: Tag content to BASE skill
Time: < 5 minutes

Step 3: Content automatically discoverable with flexible filtering
Result: TX, CA, OH, VA users all find it
Bonus: Can filter by grade (3-5), text_type (informational), etc.

Step 4: Scientific grounding included
Value: Science of Reading path shows learning progression
```

**Impact**: 95% time reduction, 4x reach, flexible filtering, scientific validation

---

## This Diagram Shows

✅ **The Problem**: Horizontal fragmentation with no backward links  
✅ **MICRO Solution**: Structured metadata enables comparison  
✅ **MID Solution**: Concept-aware detection groups variants  
✅ **MACRO Solution**: BASE skill + specification taxonomy bridges to frameworks  
✅ **The Result**: Cross-state scaling + flexible filtering + scientific grounding  

**Foundation**: Your original fragmentation diagram  
**Enhancement**: Shows how three levels solve it sequentially  
**Key Insight**: ROCK Skill = BASE + Specifications (separates WHAT from WHERE/WHEN/HOW)  
**Value**: Complete problem → solution narrative

---

**Document**: `docs/problem-solution-integrated.md`  
**Status**: ✅ Ready for hackathon presentation

