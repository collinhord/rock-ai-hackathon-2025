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

**Project**: ROCK Skills Taxonomy Bridge  
**Hackathon**: Renaissance Learning AI Hackathon 2025  
**Pipeline Status**: ✅ Operational

