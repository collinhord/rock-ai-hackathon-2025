# Analysis Directory

LLM-assisted skill mapping pipeline and redundancy analysis tools.

## Overview

This directory contains the analysis pipeline for mapping ROCK skills to Science of Reading taxonomy using AI assistance (AWS Bedrock Claude Sonnet 4.5) and semantic similarity.

---

## Quick Reference

### Run Batch Mapping
```bash
cd analysis
python scripts/batch_map_skills.py \
    --content-area "English Language Arts" \
    --checkpoint-interval 10 \
    --output-dir ./outputs/my_batch
```

### Check Batch Status
```bash
./check_batch_status.sh
```

### View Latest Mappings
```bash
# Latest consolidated mappings
cat llm_skill_mappings.csv
```

---

## Key Files

### Data Files

#### `llm_skill_mappings.csv`
**Purpose**: Consolidated LLM-assisted skill-to-taxonomy mappings  
**Rows**: 1,270 mapped skills  
**Columns**: SKILL_ID, SKILL_NAME, taxonomy path, confidence, rationale  
**Status**: Current (October 15, 2025)  
**Usage**: Primary data source for POC application

#### `master-concepts.csv`
**Purpose**: Defined master learning concepts with fragmentation metrics  
**Rows**: 15 master concepts  
**Usage**: Groups fragmented skills by learning concept

#### `skill-taxonomy-mapping.csv`
**Purpose**: Original pilot mappings (50 skills)  
**Status**: Historical reference  
**Note**: Superseded by `llm_skill_mappings.csv`

#### `metadata-gaps.md`
**Purpose**: Documentation of missing ROCK metadata and proposed schema additions

### Python Scripts

#### `scripts/batch_map_skills.py`
**Purpose**: LLM-assisted batch mapping of ROCK skills to taxonomy  
**Features**:
- Semantic similarity pre-filtering (sentence-transformers)
- AWS Bedrock Claude Sonnet 4.5 for final mapping
- Checkpoint recovery
- Skip existing mappings
- Configurable batch sizes

**Usage**:
```bash
python scripts/batch_map_skills.py \
    --skill-ids-file skill_ids.txt \
    --content-area "English Language Arts" \
    --checkpoint-interval 10 \
    --output-dir ./outputs/batch_name \
    --skip-existing llm_skill_mappings.csv
```

**Cost**: ~$0.01-0.03 per skill with Claude Sonnet 4.5

#### `scripts/prepare_poc_data.py`
**Purpose**: Data preparation utilities for POC application  
**Status**: Support script

#### `semantic_similarity.py`
**Purpose**: Semantic similarity matching between skills and taxonomy  
**Method**: Sentence-transformers embeddings + cosine similarity  
**Usage**: Standalone or as part of batch_map_skills.py

#### `check_remaining.py`
**Purpose**: Identifies unmapped skills remaining in batch  
**Usage**: `python check_remaining.py`

### Shell Scripts

#### `run_all_ela_batches.sh`
**Purpose**: Orchestrates multiple batch mapping runs for ELA skills  
**Status**: Completed (7 batches processed)  
**Usage**: `./run_all_ela_batches.sh`

#### `start_mapping.sh`
**Purpose**: Launches mapping in tmux session for background processing  
**Usage**: `./start_mapping.sh`

#### `check_batch_status.sh`
**Purpose**: Monitors progress of running batch jobs  
**Usage**: `./check_batch_status.sh`  
**Output**: Reads `batch_status.json` and displays progress

#### `monitor_dashboard.sh`
**Purpose**: Real-time monitoring dashboard for batch processing  
**Status**: Utility for long-running batches  
**Usage**: `./monitor_dashboard.sh`

#### `auto_batch_runner.sh`
**Purpose**: Automated batch runner with retry logic  
**Status**: Used for unattended batch processing

### Jupyter Notebooks

#### `redundancy-analysis.ipynb`
**Purpose**: Quantitative analysis of ROCK skill fragmentation  
**Features**:
- Loads 8,355 ROCK skills
- Identifies fragmentation patterns
- Generates visualizations
- Exports example datasets

**Outputs**:
- `fragmentation-examples.csv` - 100+ skill variants
- `fragmented_skill_patterns.csv` - All patterns
- PNG charts (distribution, redundancy)

**Usage**:
```bash
jupyter notebook redundancy-analysis.ipynb
# Run all cells: Kernel → Restart & Run All
```

---

## Batch Outputs

The `outputs/` directory contains results from completed batch mapping runs:

### Structure
```
outputs/
├── ela_batch_001/          # First ELA batch
├── ela_batch_002/          # Second ELA batch
├── ...                     # Batches 003-007
├── priority_ela_78/        # Priority ELA skills
├── poc_mappings_200/       # Initial POC mappings
└── validation_batch_50/    # Validation sample
```

### Files Per Batch
- `checkpoint_TIMESTAMP.csv` - Progress checkpoint
- `llm_assisted_mappings_TIMESTAMP.csv` - Final mappings
- `mapping_summary_TIMESTAMP.txt` - Statistics
- `review_queue_TIMESTAMP.csv` - Low-confidence mappings
- `run.log` - Execution log

### Batch Status

| Batch | Skills | Status | Output |
|-------|--------|--------|--------|
| ela_batch_001 | ~150 | ✅ Complete | mappings in llm_skill_mappings.csv |
| ela_batch_002 | ~150 | ✅ Complete | merged |
| ela_batch_004 | ~150 | ✅ Complete | merged |
| ela_batch_005 | ~150 | ✅ Complete | merged |
| ela_batch_006 | ~150 | ✅ Complete | merged |
| ela_batch_007 | ~150 | ✅ Complete | merged |
| priority_ela_78 | 78 | ✅ Complete | merged |

**Total Mapped**: 1,270 skills

---

## Archived Files

Historical backups are in `backups/` subdirectory:
- `llm_skill_mappings_backup_TIMESTAMP.csv` (5 older versions)
- `batch_runner.log` - Historical batch execution log

---

## Dependencies

### Required
- Python 3.9+
- pandas, numpy
- boto3 (AWS Bedrock)
- sentence-transformers
- scikit-learn

### Optional
- jupyter (for notebooks)
- matplotlib, seaborn, plotly (for visualizations)

**Install**:
```bash
pip install -r requirements.txt
```

---

## Workflow

### 1. Prepare Skill IDs
Create text file with skill IDs (one per line):
```bash
echo "skill-id-1" > my_skills.txt
echo "skill-id-2" >> my_skills.txt
```

### 2. Run Batch Mapping
```bash
python scripts/batch_map_skills.py \
    --skill-ids-file my_skills.txt \
    --content-area "English Language Arts" \
    --output-dir ./outputs/my_batch \
    --checkpoint-interval 10
```

### 3. Monitor Progress
```bash
# Check status
./check_batch_status.sh

# Or view log
tail -f outputs/my_batch/run.log
```

### 4. Review Results
```bash
# View mappings
cat outputs/my_batch/llm_assisted_mappings_*.csv

# Check summary
cat outputs/my_batch/mapping_summary_*.txt

# Review low-confidence mappings
cat outputs/my_batch/review_queue_*.csv
```

### 5. Merge to Master
```bash
# Manually merge or use consolidation script
cat outputs/my_batch/llm_assisted_mappings_*.csv >> llm_skill_mappings.csv
```

---

## Cost Estimates

### Per Skill
- Semantic similarity: Free (local embeddings)
- LLM mapping (Claude Sonnet 4.5): ~$0.01-0.03

### Per Batch (150 skills)
- Total: ~$1.50-4.50
- Time: 20-40 minutes

### Full ELA (2,000 skills)
- Total: ~$20-60
- Time: 4-8 hours

---

## Troubleshooting

### AWS Credentials
```bash
# Configure
aws configure

# Test
aws bedrock list-foundation-models --region us-west-2
```

### Out of Memory
Reduce batch size in checkpoint-interval:
```bash
--checkpoint-interval 5
```

### Checkpoint Recovery
Script automatically resumes from last checkpoint if interrupted.

---

## Quality Metrics

### Confidence Levels
- **High (≥0.70)**: Direct match, use as-is
- **Medium (0.50-0.69)**: Good match, light review
- **Low (<0.50)**: Review required

### Current Results (1,270 skills)
- High confidence: ~60%
- Medium confidence: ~30%
- Low confidence: ~10%

---

## Master Concepts Pipeline

### Overview

The master concepts pipeline generates a bridging layer between fragmented ROCK skills and the Science of Reading taxonomy. It consists of three main components:

1. **Variant Classification**: Identifies State A (cross-state variants) and State B (grade progressions) relationships
2. **Metadata Enrichment** (optional): Extracts pedagogical characteristics using LLM
3. **Master Concepts Generation**: Creates master concepts from variant groups with complexity bands

### Quick Start

Run the complete pipeline:
```bash
cd analysis
./run_full_pipeline.sh
```

This will:
- Classify all ELA skills into variants (State A/B) and unique skills
- Generate progression chains summary
- Create master concepts with complexity bands
- Generate skill-to-concept bridge table

### Pipeline Components

#### 1. Variant Classification

**Script**: `variant_classifier.py`

**What it does**:
- Analyzes ~8,000+ ELA skills for semantic similarity
- Groups cross-state variants (State A): Same skill across different states at same grade
- Identifies grade progressions (State B): Skills that spiral across grades
- Tracks complexity levels (0-14) based on grade
- Maps prerequisite relationships in progression chains

**Output files**:
- `outputs/variant-classification-report.csv`: Full classification with complexity levels
- `outputs/progression-chains-summary.csv`: Summary of spiraled skills

**New columns added**:
- `COMPLEXITY_LEVEL`: Numeric complexity (0=Pre-K, 13=Grade 12)
- `PREREQUISITE_SKILL_ID`: Previous skill in progression chain
- `IS_SPIRAL_SKILL`: Boolean flag for progression membership

**Usage**:
```bash
python variant_classifier.py
```

**Run time**: ~2-5 minutes for 8,000 skills

#### 2. Metadata Enrichment (Optional)

**Script**: `scripts/metadata_extractor.py`

**What it does**:
- Uses Claude Sonnet 4.5 to extract pedagogical metadata from skill descriptions
- Identifies text characteristics (fictional/informational, prose/poetry)
- Classifies skill domains (reading/writing/speaking/listening/language)
- Assesses task complexity and cognitive demand

**Extracted fields**:
- `text_type`: fictional | informational | mixed | not_applicable
- `text_mode`: prose | poetry | mixed | not_applicable
- `text_genre`: narrative | expository | argumentative | procedural | literary | not_applicable
- `skill_domain`: reading | writing | speaking | listening | language | not_applicable
- `task_complexity`: basic | intermediate | advanced
- `cognitive_demand`: recall | comprehension | application | analysis | synthesis | evaluation

**Output**: `outputs/skill_metadata_enriched.csv`

**Usage**:
```bash
python scripts/metadata_extractor.py \
    --content-area "English Language Arts" \
    --checkpoint-interval 50 \
    --output-dir ./outputs/metadata_enrichment
```

**Cost**: ~$0.005-0.01 per skill (~$40-80 for 8,000 ELA skills)  
**Run time**: ~1-2 hours for 8,000 skills

#### 3. Master Concepts Generation

**Script**: `scripts/generate_master_concepts.py`

**What it does**:
- Creates master concepts from State A variant groups
- Integrates LLM taxonomy mappings for concept naming
- Adds complexity bands (K-2, 3-5, 6-8, 9-12)
- Enriches with metadata if available
- Generates skill-to-concept bridge table

**New fields in master concepts**:
- `COMPLEXITY_BAND`: K-2 | 3-5 | 6-8 | 9-12 | Mixed
- `TEXT_TYPE`: Most common text type from variants
- `TEXT_MODE`: Most common text mode
- `SKILL_DOMAIN`: Most common skill domain
- `PREREQUISITE_CONCEPT_ID`: For future prerequisite tracking

**Output files**:
- `master-concepts.csv`: Master concept definitions
- `skill_master_concept_mapping.csv`: Skill-to-concept bridge

**Usage**:
```bash
python scripts/generate_master_concepts.py
```

**Run time**: <1 minute

### Workflow Sequence

#### Prerequisite: LLM Skill Mappings

Before running the pipeline, ensure you have LLM skill mappings:

```bash
# Check if mappings exist
ls -lh llm_skill_mappings.csv

# If not, run batch mapping first
python scripts/batch_map_skills.py \
    --content-area "English Language Arts" \
    --checkpoint-interval 10 \
    --output-dir ./outputs/ela_batch
```

#### Standard Workflow (Without Metadata)

```bash
# 1. Classify variants
python variant_classifier.py

# 2. Generate master concepts
python scripts/generate_master_concepts.py

# 3. Verify outputs
ls -lh outputs/variant-classification-report.csv
ls -lh outputs/progression-chains-summary.csv
ls -lh master-concepts.csv
```

#### Enhanced Workflow (With Metadata)

```bash
# 1. Classify variants
python variant_classifier.py

# 2. Extract metadata
python scripts/metadata_extractor.py \
    --content-area "English Language Arts" \
    --checkpoint-interval 50 \
    --output-dir ./outputs/metadata_enrichment

# 3. Generate master concepts (will auto-detect metadata)
python scripts/generate_master_concepts.py
```

#### Automated Workflow

Use the orchestration script:

```bash
./run_full_pipeline.sh
```

### When to Run Each Component

#### Variant Classification
**Run when**:
- Adding new skills to ROCK database
- ROCK skills updated/modified
- Testing different similarity thresholds
- Need fresh progression chain analysis

**Frequency**: After each significant ROCK skills update

#### Metadata Enrichment
**Run when**:
- First time setting up pipeline
- Want to enrich master concepts with pedagogical metadata
- Adding support for new skill domains

**Frequency**: Once initially, then incrementally for new skills

**Note**: Optional but recommended - master concepts will work without metadata but will lack `TEXT_TYPE`, `TEXT_MODE`, and `SKILL_DOMAIN` fields

#### Master Concepts Generation
**Run when**:
- After variant classification completes
- After adding new LLM skill mappings
- After metadata enrichment (to re-enrich concepts)
- Testing different concept grouping strategies

**Frequency**: After variant classification or metadata enrichment

### Integration with Demo App

The pipeline outputs feed directly into the Streamlit POC application:

```bash
# After running pipeline, restart Streamlit to see updates
cd ../poc
pkill -f streamlit
python -m streamlit run skill_bridge_app.py --server.port 8501
```

**Updated features**:
- 🔗 Variant Analysis page shows:
  - State A (cross-state variants)
  - State B (grade progressions) with complexity levels
  - **📈 Spiraled Skills tab** (NEW): Visual progression chains with complexity badges
  - Master concepts from State A groups
- 🔍 Master Concept Browser enriched with:
  - Complexity bands
  - Text type/mode/skill domain metadata (if enrichment run)

### Output Schema Changes

#### `variant-classification-report.csv`

**New columns**:
```
COMPLEXITY_LEVEL (int):        0-13 based on grade level
PREREQUISITE_SKILL_ID (str):   Previous skill ID in chain (null if first)
IS_SPIRAL_SKILL (bool):        True if part of grade progression
```

#### `progression-chains-summary.csv` (NEW)

**Columns**:
```
CHAIN_ID:              Unique chain identifier (SB-####)
CONCEPT_NAME:          Normalized skill concept name
CHAIN_LENGTH:          Number of grades in progression
GRADE_RANGE:           Grade span (e.g., "K-8", "3-12")
AUTHORITY:             State authority (e.g., "Texas", "CCSS")
EXAMPLE_SKILL_ID:      First skill ID in chain
EXAMPLE_SKILL_NAME:    First skill name in chain
```

#### `master-concepts.csv`

**New columns**:
```
COMPLEXITY_BAND (str):         K-2 | 3-5 | 6-8 | 9-12 | Mixed | Unknown
TEXT_TYPE (str):               fictional | informational | mixed | null
TEXT_MODE (str):               prose | poetry | mixed | null
SKILL_DOMAIN (str):            reading | writing | speaking | listening | language | null
PREREQUISITE_CONCEPT_ID (str): For future use (currently null)
```

### Troubleshooting

#### "No metadata enrichment found"

**Cause**: `outputs/skill_metadata_enriched.csv` doesn't exist  
**Impact**: Master concepts generated without text_type/text_mode/skill_domain fields  
**Fix**: Run metadata extraction (optional) or proceed without metadata

#### "Variant classification data not available"

**Cause**: `outputs/variant-classification-report.csv` missing  
**Fix**: Run `python variant_classifier.py` first

#### "LLM skill mappings not available"

**Cause**: `llm_skill_mappings.csv` empty or missing  
**Fix**: Run batch mapping first: `python scripts/batch_map_skills.py`

---

**Project**: ROCK Skills Taxonomy Bridge  
**Hackathon**: Renaissance Learning AI Hackathon 2025  
**Pipeline Status**: ✅ Operational  
**Last Updated**: October 16, 2025

