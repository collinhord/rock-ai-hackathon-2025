# ROCK Skills Taxonomy - Documentation Index

**Welcome!** This index helps you find the right documentation for your needs.

---

## 🚀 I Want To Get Started Quickly

→ **[QUICK_START.md](QUICK_START.md)** - Getting started guide (5 minutes)

→ **[docs/guides/QUICK_REFERENCE.md](docs/guides/QUICK_REFERENCE.md)** - One-page quick reference card

Includes:
- Quick start commands for all workflows
- Key file locations
- Troubleshooting basics
- Cost estimates

---

## 🎯 I Need To Run A Specific Workflow

→ **[docs/guides/WORKFLOW_GUIDE.md](docs/guides/WORKFLOW_GUIDE.md)** - Complete workflow documentation

Covers:
- First time setup
- Full taxonomy refresh
- Incremental updates
- Conflict resolution
- Quality validation
- When to use which workflow
- Decision trees and best practices

---

## 📜 I Need Script Details

→ **[docs/guides/SCRIPT_REFERENCE.md](docs/guides/SCRIPT_REFERENCE.md)** - Complete script reference

Includes:
- What each script does
- Usage examples
- Time and cost estimates
- When to use each script
- Script hierarchy and relationships
- Troubleshooting common errors

---

## 🏗️ I Want To Understand The Architecture

→ **[docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md)** - System overview

Covers:
- Conceptual model (base skills + specifications)
- System architecture
- Database schema
- Query patterns
- Extension points
- Implementation details

---

## 🎓 I Want To Understand The Concept

→ **[docs/architecture/base-skill-specification-model.md](docs/architecture/base-skill-specification-model.md)** - Conceptual framework

Explains:
- Why base skill + specification model?
- Hierarchical specification taxonomy
- Mapping examples (Capitalize, Determine Main Idea)
- Benefits and tradeoffs
- How it solves the fragmentation problem

---

## 📊 I Want To See Visual Diagrams

→ **[docs/diagrams/problem-solution-diagrams-simple.md](docs/diagrams/problem-solution-diagrams-simple.md)** - ⭐ Simplified problem-solution view

→ **[docs/diagrams/problem-solution-integrated.md](docs/diagrams/problem-solution-integrated.md)** - Complete problem-solution flow

→ **[docs/diagrams/master-skill-spine-diagram-simple.md](docs/diagrams/master-skill-spine-diagram-simple.md)** - Strategy visualization

→ **[docs/diagrams/3-visual-diagrams.md](docs/diagrams/3-visual-diagrams.md)** - Comprehensive visual diagrams

→ **[docs/architecture/implementation-architecture.md](docs/architecture/implementation-architecture.md)** - Technical architecture diagrams

Includes:
- Problem-solution diagrams (horizontal fragmentation)
- Three-vector strategy (top-down, bottom-up, lateral)
- System component diagrams
- Data flow diagrams
- Pipeline architecture

---

## 🔧 I'm Working With The Pipelines

→ **[analysis/pipelines/README.md](analysis/pipelines/README.md)** - Pipeline documentation

Covers:
- How extraction pipelines work
- spaCy + LLM approach
- MECE validation algorithm
- Cost optimization strategies
- Example usage
- Development guide

---

## 🎨 I'm Working With The UI

→ **[poc/README.md](poc/README.md)** - Frontend documentation

Includes:
- Streamlit app setup
- Page structure
- Data loading
- Redundancy Grooming UI
- Customization guide

---

## ⚙️ I Need To Configure The System

→ **[config.yaml](config.yaml)** - Configuration file

Controls:
- LLM usage (cost vs. quality tradeoff)
- Validation thresholds
- Checkpoint intervals
- Output directories
- Database settings

Edit this file to adjust system behavior.

---

## 🧪 I Want To Test The System

→ **[test_base_skill_system.sh](test_base_skill_system.sh)** - End-to-end test script

→ **[analysis/pipelines/test_extraction_poc.py](analysis/pipelines/test_extraction_poc.py)** - Quick extraction test

→ **[docs/reference/TESTING.md](docs/reference/TESTING.md)** - Complete testing guide

---

## 📊 I Want To See The Project Status

→ **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Current implementation status

→ **[IMPLEMENTATION_PHASE_0_COMPLETE.md](IMPLEMENTATION_PHASE_0_COMPLETE.md)** - Phase 0 completion status

→ **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What's been delivered

---

## 🎪 I'm Preparing For The Hackathon Demo

### Three-Level Integration (NEW - 2025 Hackathon)

→ **[docs/architecture/three-level-integration.md](docs/architecture/three-level-integration.md)** - ⭐ Complete three-level architecture

→ **[docs/guides/hackathon-integration-overview.md](docs/guides/hackathon-integration-overview.md)** - Team integration guide

→ **[docs/guides/three-level-quick-reference.md](docs/guides/three-level-quick-reference.md)** - One-page quick reference

→ **[docs/diagrams/2-problem-statement.md](docs/diagrams/2-problem-statement.md)** - Updated with integrated approach

→ **[docs/guides/filtered-dataset-validation.md](docs/guides/filtered-dataset-validation.md)** - Validation results

Explains:
- How MICRO (Jess), MID (Savannah), and MACRO (Collin) levels integrate
- Data flow through the three-level pipeline
- Tool connections and shared schemas
- Value proposition of integration
- Complete architecture diagrams

### Demo Materials

→ **[docs/hackathon/three-level-approach.md](docs/hackathon/three-level-approach.md)** - ⭐ Executive summary

→ **[docs/hackathon/demo-script.md](docs/hackathon/demo-script.md)** - 5-minute demo walkthrough

→ **[docs/hackathon/executive-summary.md](docs/hackathon/executive-summary.md)** - One-page overview for leadership

→ **[docs/hackathon/launch-guide.md](docs/hackathon/launch-guide.md)** - Hackathon launch guide

→ **[docs/hackathon/DEMO_CHECKLIST.md](docs/hackathon/DEMO_CHECKLIST.md)** - Pre-demo validation checklist

→ **[docs/hackathon/INCREMENTAL_FEATURES_DEMO.md](docs/hackathon/INCREMENTAL_FEATURES_DEMO.md)** - Incremental features demo

→ **[docs/hackathon/UPDATE_DEMO_DATA.md](docs/hackathon/UPDATE_DEMO_DATA.md)** - Demo data update guide

---

## 🔍 I Need Problem Context

→ **[docs/diagrams/2-problem-statement.md](docs/diagrams/2-problem-statement.md)** - Comprehensive problem analysis

→ **[docs/reference/1-schema-overview.md](docs/reference/1-schema-overview.md)** - ROCK schema reference

→ **[docs/diagrams/3-visual-diagrams.md](docs/diagrams/3-visual-diagrams.md)** - Problem/solution flowcharts

---

## 📚 I Want To Know What Files Exist

→ **[README.md](README.md)** - Project overview and structure

Includes:
- Project structure
- Technology stack
- Quick start
- Key findings
- Timeline

---

## Documentation Map

```
📄 Root Level (Start Here)
├── README.md                            # Project overview
├── QUICK_START.md                       # Getting started guide
├── DOCUMENTATION_INDEX.md               # This file (you are here)
├── docs/architecture/base-skill-architecture.md    # System architecture
├── WORKSPACE_AUDIT.md                   # Workspace audit report
├── PHASE_A_CLEANUP_SUMMARY.md           # Cleanup summary
└── config.yaml                          # Configuration

📁 docs/ (All Documentation - Organized)
├── README.md                            # Documentation overview
│
├── architecture/                        # System Design
│   ├── three-level-integration.md       # ⭐ NEW: Complete three-level architecture
│   ├── base-skill-specification-model.md # Conceptual framework
│   ├── master-skill-spine-strategy.md   # Three-vector strategy
│   └── implementation-architecture.md   # Technical diagrams
│
├── diagrams/                            # Visual Diagrams
│   ├── problem-solution-diagrams-simple.md # ⭐ Simplified view
│   ├── problem-solution-integrated.md   # Complete flow
│   ├── 2-problem-statement.md           # Problem analysis
│   ├── 3-visual-diagrams.md             # Comprehensive diagrams
│   └── master-skill-spine-diagram-simple.md # Strategy visualization
│
├── guides/                              # How-To Guides
│   ├── QUICK_REFERENCE.md               # ⭐ Quick start (5 min)
│   ├── WORKFLOW_GUIDE.md                # ⭐ Complete workflows
│   ├── SCRIPT_REFERENCE.md              # ⭐ Script details
│   ├── three-level-quick-reference.md   # Three-level quick ref
│   ├── hackathon-integration-overview.md # Team integration
│   └── filtered-dataset-validation.md   # Validation results
│
├── hackathon/                           # Demo Materials
│   ├── three-level-approach.md          # ⭐ Executive summary
│   ├── demo-script.md                   # 5-minute walkthrough
│   ├── executive-summary.md             # Leadership overview
│   ├── launch-guide.md                  # Hackathon launch
│   ├── DEMO_CHECKLIST.md                # Pre-demo checks
│   ├── INCREMENTAL_FEATURES_DEMO.md     # Features demo
│   └── UPDATE_DEMO_DATA.md              # Demo data update
│
└── reference/                           # Reference Materials
    ├── 1-schema-overview.md             # ROCK schema reference
    ├── TESTING.md                       # Testing guide
    └── rock-skills-bridge-explorer.md   # Bridge explorer docs

📁 analysis/ (Pipelines & Data)
├── pipelines/
│   ├── README.md                        # ⭐ Pipeline documentation
│   ├── extract_base_skills.py
│   ├── extract_specifications.py
│   ├── validate_mece.py
│   ├── test_extraction_poc.py
│   └── quick_start.sh                   # ⭐ First-time setup
└── outputs/                             # Generated data

📁 scripts/ (Workflows & Utilities)
├── status.sh                            # ⭐ Check system state
├── refresh_taxonomy.sh                  # ⭐ Full rebuild
├── update_taxonomy.sh                   # ⭐ Incremental update
├── apply_decisions.sh                   # ⭐ Apply UI decisions
├── validate_taxonomy.sh                 # ⭐ Quality checks
└── utils/
    ├── generate_reports.py
    ├── export_to_csv.py
    └── apply_decisions.py

📁 poc/ (Frontend)
├── README.md                            # Frontend setup
├── skill_bridge_app.py                  # ⭐ Streamlit UI
└── pages/
    └── redundancy_grooming.py           # ⭐ Conflict resolution UI

📁 schemas/ (Data Models)
├── base_skill.json                      # Base skill schema
├── specification.json                   # Specification schema
├── rock_skill_mapping.json              # Mapping schema
└── scientific_framework.json            # Framework schema

📁 Testing & Status
├── test_base_skill_system.sh            # End-to-end test
├── IMPLEMENTATION_STATUS.md             # Current status
├── IMPLEMENTATION_COMPLETE.md           # Delivered features
├── READY_TO_TEST.md                     # Testing guide
├── DEMO_CHECKLIST.md                    # Pre-demo checks
└── TESTING.md                           # Full testing guide
```

---

## By Role: What Should I Read?

### New Developer / First-Time User
1. [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
2. [docs/guides/QUICK_REFERENCE.md](docs/guides/QUICK_REFERENCE.md) - One-page reference
3. [docs/guides/WORKFLOW_GUIDE.md](docs/guides/WORKFLOW_GUIDE.md) - Learn the workflows
4. [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md) - Understand the system

### Data Scientist / Analyst
1. [analysis/pipelines/README.md](analysis/pipelines/README.md) - Pipeline details
2. [docs/architecture/base-skill-specification-model.md](docs/architecture/base-skill-specification-model.md) - Conceptual model
3. [docs/guides/SCRIPT_REFERENCE.md](docs/guides/SCRIPT_REFERENCE.md) - Script usage
4. [docs/architecture/three-level-integration.md](docs/architecture/three-level-integration.md) - Three-level architecture

### Frontend Developer
1. [poc/README.md](poc/README.md) - UI setup
2. [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md) - Data models
3. [schemas/](schemas/) - JSON schemas

### Curriculum Expert / Domain Specialist
1. [docs/architecture/base-skill-specification-model.md](docs/architecture/base-skill-specification-model.md) - Conceptual framework
2. [poc/skill_bridge_app.py](poc/skill_bridge_app.py) - Launch UI
3. [docs/guides/WORKFLOW_GUIDE.md](docs/guides/WORKFLOW_GUIDE.md) - Conflict resolution workflow

### Project Manager / Leadership / Hackathon Prep
1. [docs/hackathon/three-level-approach.md](docs/hackathon/three-level-approach.md) - ⭐ Executive summary
2. [docs/hackathon/executive-summary.md](docs/hackathon/executive-summary.md) - Business case
3. [docs/hackathon/demo-script.md](docs/hackathon/demo-script.md) - Demo walkthrough
4. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current progress

### DevOps / System Admin
1. [config.yaml](config.yaml) - Configuration
2. [docs/guides/SCRIPT_REFERENCE.md](docs/guides/SCRIPT_REFERENCE.md) - All scripts
3. [docs/guides/WORKFLOW_GUIDE.md](docs/guides/WORKFLOW_GUIDE.md) - Operations guide

---

## By Task: What Should I Read?

### I Need To...

**Run the system for the first time**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) + `analysis/pipelines/quick_start.sh`

**Update the taxonomy with new skills**
→ [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) → Incremental Update section

**Fix conflicts or redundancies**
→ [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) → Conflict Resolution section  
→ Launch UI: `cd poc && streamlit run skill_bridge_app.py`

**Understand how extraction works**
→ [analysis/pipelines/README.md](analysis/pipelines/README.md)

**Validate data quality**
→ [SCRIPT_REFERENCE.md](SCRIPT_REFERENCE.md) → `validate_taxonomy.sh`

**Generate reports or export data**
→ [SCRIPT_REFERENCE.md](SCRIPT_REFERENCE.md) → Utilities section

**Configure LLM usage or thresholds**
→ [config.yaml](config.yaml)

**Present to stakeholders**
→ [hackathon/demo-script.md](hackathon/demo-script.md)  
→ [hackathon/executive-summary.md](hackathon/executive-summary.md)

**Understand the problem being solved**
→ [docs/2-problem-statement.md](docs/2-problem-statement.md)

**Extend or modify the system**
→ [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md)  
→ [docs/implementation-architecture.md](docs/implementation-architecture.md)

---

## Quick Links By Format

### Single-Page References
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - ⭐ Start here
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - This file
- [DEMO_CHECKLIST.md](DEMO_CHECKLIST.md) - Pre-demo checks

### Complete Guides
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - All workflows
- [SCRIPT_REFERENCE.md](SCRIPT_REFERENCE.md) - All scripts
- [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md) - System architecture
- [analysis/pipelines/README.md](analysis/pipelines/README.md) - Pipeline details

### Conceptual Docs
- [docs/base-skill-specification-model.md](docs/base-skill-specification-model.md)
- [docs/2-problem-statement.md](docs/2-problem-statement.md)

### Visual Docs
- [docs/master-skill-spine-diagram-simple.md](docs/master-skill-spine-diagram-simple.md)
- [docs/implementation-architecture.md](docs/implementation-architecture.md)
- [docs/3-visual-diagrams.md](docs/3-visual-diagrams.md)

### Executable
- [test_base_skill_system.sh](test_base_skill_system.sh)
- [scripts/status.sh](scripts/status.sh)
- [scripts/refresh_taxonomy.sh](scripts/refresh_taxonomy.sh)
- [scripts/validate_taxonomy.sh](scripts/validate_taxonomy.sh)
- [analysis/pipelines/quick_start.sh](analysis/pipelines/quick_start.sh)

---

## Still Can't Find What You Need?

1. **Check system status**: `./scripts/status.sh`
2. **Look at the root README**: [README.md](README.md)
3. **Browse the file structure**: `tree -L 2 rock-skills/`
4. **Search all docs**: `grep -r "your search term" *.md docs/ analysis/pipelines/README.md`

---

## Documentation Standards

All documentation follows these principles:

- **Quick Reference**: One-page cards for fast lookup
- **Complete Guides**: Comprehensive workflows and details
- **Conceptual Docs**: Why and how it works
- **Executable Scripts**: Actually runs the system
- **Visual Diagrams**: Mermaid charts for clarity

**⭐ = Recommended starting point**

---

**Most Common Starting Points:**

| I Want To... | Start Here |
|--------------|-----------|
| Get started quickly | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Run a workflow | [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.MD) |
| Understand a script | [SCRIPT_REFERENCE.md](SCRIPT_REFERENCE.md) |
| Learn the system | [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md) |
| Demo the project | [hackathon/demo-script.md](hackathon/demo-script.md) |


