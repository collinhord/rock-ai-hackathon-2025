# ROCK Skills Taxonomy - Script Reference

## Quick Script Lookup

| What Do You Want To Do? | Run This Script | Details |
|-------------------------|-----------------|---------|
| Check current status | `./scripts/status.sh` | [Details](#scriptsstatussh) |
| First time setup | `analysis/pipelines/quick_start.sh` | [Details](#analysispipelinesquick_startsh) |
| Rebuild everything | `./scripts/refresh_taxonomy.sh` | [Details](#scriptsrefresh_taxonomysh) |
| Add new skills only | `./scripts/update_taxonomy.sh` | [Details](#scriptsupdate_taxonomysh) |
| Apply UI decisions | `./scripts/apply_decisions.sh` | [Details](#scriptsapply_decisionssh) |
| Validate quality | `./scripts/validate_taxonomy.sh` | [Details](#scriptsvalidate_taxonomysh) |
| Generate reports | `python3 scripts/utils/generate_reports.py` | [Details](#scriptsutilsgenerate_reportspy) |
| Export to CSV | `python3 scripts/utils/export_to_csv.py` | [Details](#scriptsutilsexport_to_csvpy) |
| Launch UI | `cd poc && streamlit run skill_bridge_app.py` | [Details](#pocskill_bridge_apppy) |

---

## Script Hierarchy

```
TIER 1: Master Orchestration (Complete Workflows)
scripts/
├── status.sh                    # Check system state
├── refresh_taxonomy.sh          # Full rebuild workflow
├── update_taxonomy.sh           # Incremental update workflow
├── apply_decisions.sh           # Conflict resolution workflow
└── validate_taxonomy.sh         # Quality validation workflow

TIER 2: Single-Purpose Pipelines (Specific Tasks)
analysis/pipelines/
├── extract_base_skills.py       # ROCK skills → Base skills
├── extract_specifications.py    # Mappings → Specifications
├── validate_mece.py             # Conflict & redundancy detection
└── test_extraction_poc.py       # Quick test (20 samples)

TIER 3: Utilities (Helper Functions)
scripts/utils/
├── generate_reports.py          # Analytics & summaries
├── export_to_csv.py             # SQLite → CSV exports
└── apply_decisions.py           # Decision application logic

FRONTEND: Interactive UI
poc/
├── skill_bridge_app.py          # Main Streamlit app
└── pages/
    └── redundancy_grooming.py   # Conflict resolution UI
```

---

## Detailed Script Reference

### `scripts/status.sh`

**Purpose**: Display current taxonomy state and suggest next actions

**Usage**:
```bash
cd rock-skills
./scripts/status.sh
```

**Output**:
- Database existence and stats (base skills, ROCK skills mapped)
- Pending conflicts count
- MECE validation score
- Running background processes
- Suggested next actions

**Time**: < 1 minute  
**Cost**: Free

**When to Use**:
- Anytime you want to check system state
- Before starting work (what needs attention?)
- After making changes (did it work?)

---

### `analysis/pipelines/quick_start.sh`

**Purpose**: First-time setup and validation

**Usage**:
```bash
cd rock-skills/analysis/pipelines
./quick_start.sh
```

**What It Does**:
1. Installs Python dependencies (pandas, spaCy, etc.)
2. Downloads spaCy language model (en_core_web_lg, ~800MB)
3. Runs POC test on 20 sample skills
4. Validates all imports work
5. Creates sample outputs

**Time**: 5-10 minutes  
**Cost**: Free

**When to Use**:
- First time using the system
- After fresh git clone
- Testing new development environment

---

### `scripts/refresh_taxonomy.sh`

**Purpose**: Complete regeneration of entire taxonomy database

**Usage**:
```bash
cd rock-skills

# Full refresh with LLM (best quality, costly)
./scripts/refresh_taxonomy.sh

# Without LLM (faster, free, lower quality)
./scripts/refresh_taxonomy.sh --no-llm

# Test mode (100 skills only)
./scripts/refresh_taxonomy.sh --test
```

**What It Does**:
1. Creates backup of existing taxonomy.db
2. Runs `extract_base_skills.py` (all ROCK skills)
3. Runs `extract_specifications.py` (all mappings)
4. Runs `validate_mece.py` (detect conflicts)
5. Generates summary reports

**Time**: 3-5 hours (with LLM), 1-2 hours (without)  
**Cost**: $40-60 (with LLM), Free (without)

**When to Use**:
- Major ROCK schema updates
- Scientific framework changes
- After experimental changes (clean rebuild)
- Starting from scratch

**Calls These Scripts**:
- `analysis/pipelines/extract_base_skills.py`
- `analysis/pipelines/extract_specifications.py`
- `analysis/pipelines/validate_mece.py`
- `scripts/utils/generate_reports.py`

---

### `scripts/update_taxonomy.sh`

**Purpose**: Add new ROCK skills without regenerating everything

**Usage**:
```bash
cd rock-skills

# Auto-detect new skills
./scripts/update_taxonomy.sh

# Specify date
./scripts/update_taxonomy.sh --since 2025-10-15

# Provide file
./scripts/update_taxonomy.sh --new-skills data/new_skills.csv
```

**What It Does**:
1. Identifies skills not in current taxonomy
2. Extracts base skills (only new skills)
3. Attempts to map to existing base skills first
4. Validates for conflicts with existing taxonomy
5. Incrementally updates taxonomy.db

**Time**: 30-60 minutes  
**Cost**: $5-10 (proportional to new skills)

**When to Use**:
- ROCK adds small batches (10-100 new skills)
- Monthly updates
- Don't want to wait for full refresh

**Calls These Scripts**:
- `analysis/pipelines/extract_base_skills.py --incremental`
- `analysis/pipelines/extract_specifications.py --new-only`
- `analysis/pipelines/validate_mece.py --check-new-conflicts`

---

### `scripts/apply_decisions.sh`

**Purpose**: Apply conflict resolution decisions from UI

**Usage**:
```bash
cd rock-skills

# Apply all pending decisions
./scripts/apply_decisions.sh

# Preview changes without applying
./scripts/apply_decisions.sh --dry-run

# Custom decisions file
./scripts/apply_decisions.sh --file taxonomy/custom_decisions.json
```

**What It Does**:
1. Reads `taxonomy/decisions.json` (exported from UI)
2. Merges redundant base skills
3. Adds new specifications
4. Updates clarifications
5. Regenerates validation report

**Time**: 5-10 minutes  
**Cost**: Free

**When to Use**:
- After making decisions in Redundancy Grooming UI
- After human review of conflicts

**Prerequisites**:
1. Review conflicts in Streamlit UI (Redundancy Grooming page)
2. Make decisions (merge/specify/clarify/keep)
3. Export decisions to `taxonomy/decisions.json`

**Calls These Scripts**:
- `scripts/utils/apply_decisions.py`
- `analysis/pipelines/validate_mece.py` (regenerate)

---

### `scripts/validate_taxonomy.sh`

**Purpose**: Comprehensive quality checks before deploy

**Usage**:
```bash
cd rock-skills

# Full validation
./scripts/validate_taxonomy.sh

# Quick mode (skip LLM analysis)
./scripts/validate_taxonomy.sh --quick
```

**What It Checks**:
1. MECE score (must be ≥ 0.90)
2. Coverage (% of ROCK skills mapped)
3. Data integrity (orphaned records, missing fields)
4. Specification completeness
5. Remaining conflicts

**Time**: 10-15 minutes  
**Cost**: Free (or minimal if LLM analysis enabled)

**When to Use**:
- Before git commits
- Before production deploy
- After resolving conflicts
- Regular quality audits

**Output Files**:
- `analysis/reports/quality_report_TIMESTAMP.txt`

---

### `scripts/utils/generate_reports.py`

**Purpose**: Generate summary analytics and metrics

**Usage**:
```bash
python3 scripts/utils/generate_reports.py
python3 scripts/utils/generate_reports.py --output custom/dir
```

**Outputs**:
- `analysis/reports/summary_TIMESTAMP.txt` (human-readable)
- `analysis/reports/metrics_TIMESTAMP.json` (machine-readable)

**Time**: 1-2 minutes  
**Cost**: Free

**Metrics Included**:
- Base skills count
- ROCK skills mapped
- Specifications count
- Coverage percentages
- Top 10 most frequent base skills

---

### `scripts/utils/export_to_csv.py`

**Purpose**: Export taxonomy data from SQLite to CSV

**Usage**:
```bash
# Export all tables
python3 scripts/utils/export_to_csv.py

# Export specific tables
python3 scripts/utils/export_to_csv.py --tables base_skills,specifications

# Custom output directory
python3 scripts/utils/export_to_csv.py --output exports/
```

**Outputs**:
- `taxonomy/exports/base_skills_TIMESTAMP.csv`
- `taxonomy/exports/specifications_TIMESTAMP.csv`
- `taxonomy/exports/rock_skill_mappings_TIMESTAMP.csv`

**Time**: < 1 minute  
**Cost**: Free

**When to Use**:
- Sharing data with external tools
- Excel analysis
- Backup in human-readable format

---

### `analysis/pipelines/extract_base_skills.py`

**Purpose**: Extract base skills from ROCK skills (Tier 2 pipeline)

**Usage**:
```bash
cd analysis/pipelines

# Full extraction with LLM
python3 extract_base_skills.py

# Test mode (100 skills, no LLM)
python3 extract_base_skills.py --limit 100 --no-llm

# Incremental (new skills only)
python3 extract_base_skills.py --incremental --since 2025-10-15
```

**Process**:
1. **spaCy Preprocessing**: Dependency parsing, NER, lemmatization
2. **Clustering**: Group similar skills
3. **LLM Extraction** (optional): Generate base skill from group
4. **Mapping Creation**: ROCK skill → Base skill relationships

**Time**: 2-3 hours (full, with LLM)  
**Cost**: $30-40 (with LLM), Free (without)

**Called By**: `scripts/refresh_taxonomy.sh`, `scripts/update_taxonomy.sh`

---

### `analysis/pipelines/extract_specifications.py`

**Purpose**: Extract hierarchical specifications from mappings (Tier 2 pipeline)

**Usage**:
```bash
cd analysis/pipelines

# Full extraction
python3 extract_specifications.py

# New specifications only
python3 extract_specifications.py --new-only
```

**Process**:
1. **Rule-Based Extraction**: Pattern matching for common specs (text_type, grade, etc.)
2. **LLM Enhancement** (optional): Extract nuanced specifications
3. **Hierarchy Construction**: Build specification taxonomy

**Time**: 30-60 minutes  
**Cost**: $10-15 (with LLM), Free (rule-based only)

**Called By**: `scripts/refresh_taxonomy.sh`, `scripts/update_taxonomy.sh`

---

### `analysis/pipelines/validate_mece.py`

**Purpose**: Detect conflicts and redundancies (Tier 2 pipeline)

**Usage**:
```bash
cd analysis/pipelines

# Full validation with LLM
python3 validate_mece.py

# Fast mode (no LLM semantic analysis)
python3 validate_mece.py --no-llm

# Check only new conflicts
python3 validate_mece.py --check-new-conflicts
```

**Detection Levels**:
1. **String Similarity**: Exact/near-exact matches
2. **Semantic Similarity**: Vector embeddings (sentence-transformers)
3. **LLM Analysis**: Deep semantic ambiguity detection

**Outputs**:
- `taxonomy/validation_report.json` (MECE score, metrics)
- `taxonomy/conflicts.json` (flagged conflicts)
- `taxonomy/redundancies.json` (duplicate groups)

**Time**: 10-15 minutes  
**Cost**: $2-5 (with LLM), Free (without)

**Called By**: `scripts/refresh_taxonomy.sh`, `scripts/validate_taxonomy.sh`

---

### `analysis/pipelines/test_extraction_poc.py`

**Purpose**: Quick validation on 20 sample skills (Tier 2 pipeline)

**Usage**:
```bash
cd analysis/pipelines
python3 test_extraction_poc.py
```

**What It Does**:
1. Selects 20 diverse ROCK skills
2. Runs extraction pipeline
3. Validates outputs
4. Prints sample results

**Time**: 2-3 minutes  
**Cost**: Free

**When to Use**:
- Testing pipeline changes
- Validating environment setup
- Quick smoke test

**Called By**: `analysis/pipelines/quick_start.sh`

---

### `poc/skill_bridge_app.py`

**Purpose**: Interactive Streamlit web application

**Usage**:
```bash
cd rock-skills/poc
streamlit run skill_bridge_app.py
```

**Opens**: `http://localhost:8501`

**Features**:
- **Overview Dashboard**: System metrics
- **Base Skills Explorer**: Browse extracted base skills
- **Specification Browser**: View hierarchical specs
- **ROCK Skill Mapper**: See mappings
- **Framework Alignment**: Scientific framework connections
- **Redundancy Grooming**: Conflict resolution UI ⭐

**Key Page: Redundancy Grooming**
- View flagged conflicts
- See LLM analysis and reasoning
- Make decisions (merge/specify/clarify/keep)
- Export decisions to JSON

**Time**: Always running (web app)  
**Cost**: Free

---

## Configuration File

### `config.yaml`

**Purpose**: Central configuration for all scripts

**Key Settings**:

```yaml
extraction:
  use_llm: true              # false = free but lower quality

validation:
  mece_threshold: 0.90       # Minimum acceptable score

database:
  auto_backup: true          # Backup before major operations
```

**Edit This File To**:
- Toggle LLM usage (cost vs. quality)
- Adjust validation thresholds
- Change checkpoint intervals
- Configure backup retention

---

## Decision Tree

```
What do you need to do?
│
├─ Check status
│  └─ ./scripts/status.sh
│
├─ First time setup
│  └─ analysis/pipelines/quick_start.sh
│
├─ Complete rebuild
│  └─ ./scripts/refresh_taxonomy.sh
│
├─ Add new skills only
│  └─ ./scripts/update_taxonomy.sh
│
├─ Resolve conflicts
│  ├─ 1. UI: Redundancy Grooming (make decisions)
│  └─ 2. ./scripts/apply_decisions.sh
│
├─ Validate quality
│  └─ ./scripts/validate_taxonomy.sh
│
├─ Generate reports
│  └─ python3 scripts/utils/generate_reports.py
│
├─ Export data
│  └─ python3 scripts/utils/export_to_csv.py
│
└─ View UI
   └─ cd poc && streamlit run skill_bridge_app.py
```

---

## Common Workflows

### Scenario 1: "I just cloned the repo"
```bash
cd rock-skills/analysis/pipelines
./quick_start.sh
cd ../../poc
streamlit run skill_bridge_app.py
```

### Scenario 2: "ROCK added 50 new skills"
```bash
cd rock-skills
./scripts/update_taxonomy.sh --new-skills data/new_skills.csv
./scripts/validate_taxonomy.sh
```

### Scenario 3: "I need to rebuild everything"
```bash
cd rock-skills
./scripts/refresh_taxonomy.sh --no-llm    # Start without LLM (free)
# Review results
./scripts/refresh_taxonomy.sh             # Re-run with LLM if needed
```

### Scenario 4: "I see conflicts in the UI"
```bash
# Step 1: UI
cd rock-skills/poc
streamlit run skill_bridge_app.py
# Navigate to Redundancy Grooming, make decisions, export

# Step 2: Apply
cd ../scripts
./scripts/apply_decisions.sh
./scripts/validate_taxonomy.sh
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database not found" | Run `./scripts/refresh_taxonomy.sh` |
| "AWS credentials not configured" | Run `aws configure` or set `use_llm: false` in config.yaml |
| Low MECE score | Run UI conflict resolution, then `./scripts/apply_decisions.sh` |
| Script permission denied | Run `chmod +x scripts/*.sh` |
| spaCy model not found | Run `python3 -m spacy download en_core_web_lg` |

---

## Additional Resources

- **Workflow Guide**: [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow documentation
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - One-page quick start
- **Architecture**: [base-skill-architecture.md](../architecture/base-skill-architecture.md) - System overview
- **Pipeline Details**: [analysis/pipelines/README.md](analysis/pipelines/README.md) - Technical details
- **Configuration**: [config.yaml](config.yaml) - Edit settings here

---

**Questions? Run `./scripts/status.sh` to see what needs attention.**

