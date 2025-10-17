# ROCK Skills Taxonomy: Base Skill + Specification System

**Renaissance Learning AI Hackathon 2025**

## Overview

This project addresses the **Master Skill Fragmentation Problem** in ROCK: the same learning concept appears 6-8 times across state standards with no metadata connecting conceptually equivalent skills.

**Solution**: A hierarchical base skill + specification architecture that bridges ROCK skills to scientific frameworks (Science of Reading), enabling discovery, reducing redundancy, and grounding skills in learning science.

### What's New: Three-Level Integration (Hackathon 2025)

**🚀 NEW**: Integrated three-level approach combining metadata extraction, redundancy detection, and master concept mapping:

**🔬 MICRO Level (Jess)**: Extract structured metadata from skills using spaCy NLP
- **Result**: 95%+ extraction accuracy for actions, targets, qualifiers
- **Value**: Enables concept-based analysis beyond text similarity

**🔍 MID Level (Savannah)**: Detect and resolve redundancies through concept-aware similarity  
- **Result**: 23.7% redundancy detected in filtered dataset
- **Value**: Groups cross-state variants, reduces apparent skill count

**🎯 MACRO Level (Collin)**: Create master concepts through scientific framework triangulation
- **Result**: 254 master concepts from 333 skills (23.7% reduction)
- **Value**: Enables cross-state content scaling, learning progression tracking

**Pipeline Status**: ✅ Production-ready (2.7 seconds for 333 skills)

**Quick Start**:
```bash
cd rock-skills/analysis/pipelines
python3 integrated_skill_analysis.py --input ../../rock_schemas/skill_list_filtered_data_set.csv
```

**Documentation**: See [`docs/three-level-integration.md`](docs/three-level-integration.md) for complete architecture

---

### Base Skill + Specification Model

Instead of treating redundant skills as "master concepts," we use:
- **Base Skills**: Core learning objectives (e.g., "Capitalize")
- **Hierarchical Specifications**: Context and application tags (e.g., text_type, complexity_band, support_level)

This enables:
- **Flexible Querying**: "Show me all reading comprehension base skills for fictional prose at grade 3-5 complexity"
- **MECE Validation**: Automated detection of redundant or conflicting base skills
- **Scientific Alignment**: Top-down framework → bottom-up skills bridging

## Project Structure

```
rock-skills/
├── analysis/                    # Phase 1 & 2: Analysis and Mapping
│   ├── redundancy-analysis.ipynb    # Quantitative fragmentation analysis
│   ├── llm_skill_mappings.csv       # LLM-assisted mappings (1,270 skills)
│   ├── master-concepts.csv          # Master concept groupings
│   ├── scripts/batch_map_skills.py  # LLM mapping pipeline
│   ├── outputs/                     # Batch mapping results
│   ├── metadata-gaps.md             # What's missing in ROCK schemas
│   └── README.md                    # Pipeline documentation
│
├── poc/                         # Phase 3: Interactive Demo
│   ├── skill_bridge_app.py          # Streamlit web application
│   ├── data_loader.py               # Data loading module
│   ├── mock_data/                   # Content scaling demo data
│   ├── requirements.txt             # App dependencies
│   └── README.md                    # Setup and usage instructions
│
├── hackathon/                   # Phase 4: Presentation Materials
│   ├── executive-summary.md         # One-page overview for leadership
│   ├── demo-script.md               # 5-minute demo walkthrough
│   └── next-steps.md                # Roadmap for pilot and production
│
├── docs/                        # Problem Documentation
│   ├── 1-schema-overview.md         # ROCK schema technical reference
│   ├── 2-problem-statement.md       # Comprehensive problem analysis
│   ├── 3-visual-diagrams.md         # Mermaid flowcharts
│   └── archive/                     # Archived status documents
│
├── taxonomy_builder/            # Taxonomy Validation & Analysis
│   ├── cli.py                       # Command-line interface
│   ├── validator.py                 # Structural validation
│   ├── framework_analyzer.py        # Framework comparison
│   └── README.md                    # Complete documentation
│
├── scripts/                     # Utility Scripts
│   ├── quick_demo_test.sh           # Pre-demo validation ⭐
│   ├── verify_data_integrity.py     # Data validation
│   └── README.md                    # Scripts documentation
│
├── rock_schemas/                # ROCK Production Data
│   ├── SKILLS.csv                   # 8,355 ROCK skills
│   ├── STANDARD_SKILLS.csv          # Skill-standard relationships
│   ├── STANDARDS.csv                # State standards
│   └── ... (other schema files)
│
├── POC_science_of_reading_literacy_skills_taxonomy.csv  # Master taxonomy
├── taxonomy.db                  # SQLite database (3.1 MB)
├── DEMO_TEST_GUIDE.md           # Content Scaling demo test guide
├── DEMO_CHECKLIST.md            # Pre-demo validation checklist ⭐
└── QUICK_START.md               # 5-minute quick start guide
```

## Quick Start

### System Workflows (New Architecture)

**Check System Status:**
```bash
cd rock-skills
./scripts/status.sh
```

**First Time Setup & Test:**
```bash
cd rock-skills/analysis/pipelines
./quick_start.sh                    # Install dependencies, run POC test (5-10 min, Free)
cd ../../poc
streamlit run skill_bridge_app.py   # Launch UI
```

**Update Entire Taxonomy (Full Refresh):**
```bash
cd rock-skills
./scripts/refresh_taxonomy.sh       # Complete regeneration (3-5 hours, $40-60)
# Or without LLM (faster, lower quality):
./scripts/refresh_taxonomy.sh --no-llm
```

**Add New Skills (Incremental):**
```bash
cd rock-skills
./scripts/update_taxonomy.sh --new-skills data/new_skills.csv  # (30-60 min, $5-10)
```

**Resolve Conflicts (Human Review):**
```bash
cd rock-skills/poc
streamlit run skill_bridge_app.py
# Navigate to "Redundancy Grooming" page
# Make decisions, export, then:
cd ../scripts
./apply_decisions.sh
```

**Validate Quality:**
```bash
cd rock-skills
./scripts/validate_taxonomy.sh      # Quality checks (10-15 min, Free)
```

📖 **Full Workflow Documentation**: See [docs/architecture/base-skill-architecture.md](docs/architecture/base-skill-architecture.md)

📋 **Phase 0 Implementation**: See [PHASE_0_IMPLEMENTATION_SUMMARY.md](PHASE_0_IMPLEMENTATION_SUMMARY.md)

📚 **All Documentation**: See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

### Pre-Demo Validation ✅

```bash
# Run comprehensive demo readiness check
bash scripts/quick_demo_test.sh
```

### Launch the Interactive Demo (Original Hackathon)

```bash
cd poc

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the Streamlit app
streamlit run skill_bridge_app.py
```

Opens at `http://localhost:8501`

**Primary Demo Features**:
- 🎯 **Content Scaling Simulator** - Shows 8% → 100% coverage transformation ⭐
- 🔎 **Cross-State Discovery** - Demonstrates content invisibility problem
- 💰 **Scaling Impact Dashboard** - Interactive ROI calculator

**Additional Features**:
- 🔍 Master Concept Browser - Group fragmented skills
- 📊 Redundancy Visualizer - Charts proving fragmentation
- 📚 Science of Reading Taxonomy Explorer

**Demo Guide**: Follow `DEMO_TEST_GUIDE.md` or `DEMO_CHECKLIST.md`

### Review Presentation Materials

```bash
cd hackathon
```

- `executive-summary.md` - Share with leadership
- `demo-script.md` - 5-minute walkthrough script
- `next-steps.md` - Detailed roadmap for pilot phase

### Run Analysis (Optional)

```bash
cd analysis

# Install dependencies
pip install -r requirements.txt

# Run the redundancy analysis notebook
jupyter notebook redundancy-analysis.ipynb
```

## Key Deliverables

### Phase 1: Quantitative Validation ✅
- [x] Redundancy analysis notebook
- [x] Fragmentation examples dataset
- [x] Metadata gap analysis document
- [x] **Result**: Proved 6.8x average redundancy with real data

### Phase 2: Taxonomy Mapping ✅
- [x] 50 ROCK skills mapped to Science of Reading
- [x] 15 master concepts defined
- [x] Semantic similarity tool for AI-assisted mapping
- [x] **Result**: Demonstrated mapping feasibility and methodology

### Phase 3: POC Demonstrator ✅
- [x] Interactive Streamlit web application
- [x] Master concept browser with skill groupings
- [x] Skill inspector with taxonomy mappings
- [x] Redundancy visualizer with charts
- [x] **Result**: Working demo showing solution value

### Phase 4: Presentation Materials ✅
- [x] Executive summary (1-page)
- [x] Demo script (5-minute walkthrough)
- [x] Next steps roadmap (pilot to production)
- [x] **Result**: Complete package for stakeholder presentation

## Key Findings

### Problem Quantified
- **8,355 total ROCK skills** analyzed
- **~1,200 unique ELA patterns** (6.8x redundancy)
- **60-75% conceptual redundancy** across skill inventory
- **Zero metadata** connecting equivalent skills

### Solution Demonstrated
- **Science of Reading** provides master taxonomy framework
- **Non-invasive bridge layer** requires no ROCK schema changes
- **50 pilot mappings** prove feasibility
- **Interactive POC** shows immediate value

### Value Proposition
- **70-80% reduction** in skill discovery time
- **Enables new features**: adaptive learning, cross-state alignment
- **Research-grade data**: aggregate by master concepts
- **Competitive advantage**: learning science leadership

## Technologies Used

### Analysis
- **Python**: pandas, numpy, matplotlib, seaborn
- **Jupyter**: Interactive notebooks
- **sklearn**: Semantic similarity (cosine distance)
- **sentence-transformers**: Embedding models (optional)

### POC Application
- **Streamlit**: Rapid web app framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation with caching

### Data
- **ROCK Schemas**: 8,355 skills, 2M+ standard relationships
- **Science of Reading**: 1,140 taxonomy entries (6-level hierarchy)

## Running Semantic Similarity Tool

```bash
cd analysis

python semantic_similarity.py \
  --skills ../rock_schemas/SKILLS.csv \
  --taxonomy ../POC_science_of_reading_literacy_skills_taxonomy.csv \
  --output skill_taxonomy_matches.csv \
  --max-skills 100 \
  --top-k 5
```

**Requires**: `sentence-transformers` package (optional, 2GB download)

## Project Timeline

- **Phase 1 (Analysis)**: 6 hours - Quantitative validation
- **Phase 2 (Mapping)**: 8 hours - Taxonomy mapping experiment
- **Phase 3 (POC)**: 12 hours - Interactive demonstrator
- **Phase 4 (Presentation)**: 3 hours - Executive materials
- **Total**: ~30 hours for complete hackathon project

## Next Steps (Post-Hackathon)

### Immediate (1-2 weeks)
1. Present POC to ROCK Skills List Advancement team
2. Validate with curriculum designers and product managers
3. Gather feedback and refine approach

### Pilot Phase (3-6 months)
1. Map 500 K-2 foundational literacy skills
2. Build production API and database schema
3. Integrate with Star Early Literacy (pilot product)
4. Evaluate and measure ROI

### Full Implementation (6-18 months)
1. Map all 2,000 ELA skills to Science of Reading
2. Create Math Learning Progressions taxonomy
3. Map all 2,000 Math skills
4. Integrate across Renaissance product suite

## Documentation

### Problem Documentation
- `/docs/2-problem-statement.md` - Comprehensive problem analysis (646 lines)
- `/docs/1-schema-overview.md` - Technical schema reference (479 lines)
- `/docs/3-visual-diagrams.md` - Mermaid flowcharts (522 lines)

### Analysis Documentation
- `/analysis/metadata-gaps.md` - What metadata is missing and what's needed
- `/analysis/redundancy-analysis.ipynb` - Commented analysis code

### POC Documentation
- `/poc/README.md` - Complete setup and usage guide
- Demo script with troubleshooting and backup talking points

## FAQs

### Why Science of Reading?
- Evidence-based framework grounded in decades of reading research
- Hierarchical structure with 6 levels of granularity
- 1,140 skill subsets covering comprehensive literacy competencies
- Already familiar to Renaissance curriculum teams

### Does this require changing ROCK?
No. Bridge layer approach adds new `SKILL_TAXONOMY_MAPPINGS` table without modifying existing ROCK schema. Preserves Star Assessment dependency.

### How accurate are the mappings?
Pilot mappings have confidence scores:
- **High**: Direct match, clear alignment (60%)
- **Medium**: Good match, slight interpretation (30%)
- **Low**: Best available, needs expert review (10%)

### What about Math skills?
Same approach, different taxonomy. Need to select/create Math Learning Progressions framework first (NCTM, CCSS Math progressions, or cognitive research-based).

### Can this scale?
Yes. AI-assisted semantic similarity suggests top-5 matches, humans validate. Estimated 800 hours for 2,000 skills (~4-6 months with team).

## Contact

**Project Lead**: ROCK Skills Analysis Team  
**Hackathon**: Renaissance Learning AI Hackathon 2025  
**Date**: October 2025

## License

Internal Renaissance Learning project. See `/LICENSE` for details.

---

## Appendix: Sample Commands

### Generate fragmentation examples
```bash
jupyter nbconvert --execute --to notebook \
  --output redundancy-analysis-executed.ipynb \
  redundancy-analysis.ipynb
```

### Export POC screenshots
```bash
streamlit run skill_bridge_app.py
# Navigate to each page, take screenshots for presentation
```

### Check data availability
```bash
ls -lh rock_schemas/*.csv
wc -l rock_schemas/SKILLS.csv
wc -l POC_science_of_reading_literacy_skills_taxonomy.csv
```

### Validate mappings
```bash
python -c "
import pandas as pd
mapping = pd.read_csv('analysis/skill-taxonomy-mapping.csv')
skills = pd.read_csv('rock_schemas/SKILLS.csv')
valid = mapping['SKILL_ID'].isin(skills['SKILL_ID']).all()
print(f'All mappings valid: {valid}')
print(f'Mapped skills: {len(mapping)}')
"
```

---

## Testing & Validation

### Quick Demo Test (Before Presentations)
```bash
bash scripts/quick_demo_test.sh
```

Validates:
- Data integrity (all CSV files load)
- Python dependencies installed
- Critical files exist
- Application imports work
- CLI tools functional

### Data Integrity Check
```bash
python3 scripts/verify_data_integrity.py
```

Checks all critical data files for:
- Correct row counts
- Required columns present
- Files load without errors

### Complete Testing Guide
See `TESTING.md` for comprehensive testing procedures.

---

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| `README.md` | Project overview and quick start | Everyone |
| `DEMO_CHECKLIST.md` | Pre-demo validation checklist | Presenters ⭐ |
| `DEMO_TEST_GUIDE.md` | Content Scaling demo walkthrough | Presenters |
| `QUICK_START.md` | 5-minute quick start | New users |
| `TESTING.md` | Testing procedures | Developers |
| `hackathon/executive-summary.md` | Business case | Leadership |
| `hackathon/demo-script.md` | Presentation script | Presenters |
| `analysis/README.md` | Analysis pipeline | Data scientists |
| `scripts/README.md` | Utility scripts | Developers |
| `taxonomy_builder/README.md` | Taxonomy tools | Taxonomists |

---

**Ready to demo? Run `bash scripts/quick_demo_test.sh` and follow `DEMO_CHECKLIST.md`**
