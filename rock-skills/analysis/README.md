# ROCK Skills Analysis Tools

Comprehensive analysis tools for ROCK skills data, including quantitative validation, variant classification, and LLM-assisted taxonomy mapping.

## Overview

This directory contains scripts and notebooks for analyzing the ROCK skills taxonomy fragmentation problem and implementing solution approaches.

## Directory Structure

```
analysis/
├── README.md                    # This file
├── QUICKSTART.md                # Quick start guide
├── requirements.txt             # Python dependencies
├── scripts/                     # Executable analysis scripts
│   ├── batch_map_skills.py
│   ├── variant_classifier.py
│   ├── calculate_validation_metrics.py
│   └── generate_gap_report.py
├── modules/                     # Reusable Python modules
│   ├── llm_mapping_assistant.py
│   ├── confidence_scorer.py
│   ├── refinement_engine.py
│   ├── taxonomy_gap_detector.py
│   └── semantic_similarity.py
├── notebooks/                   # Jupyter notebooks
│   └── redundancy-analysis.ipynb
├── docs/                        # Detailed documentation
│   ├── ENHANCED_VALIDATION_GUIDE.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── OPTIMIZATION_SUMMARY.md
│   ├── science_of_reading_rubric.md
│   └── metadata-gaps.md
└── outputs/                     # Generated outputs
    └── validation_batch_50/     # Example validation results
```

## Tools

### 1. Redundancy Analysis (`notebooks/redundancy-analysis.ipynb`)

**Purpose**: Quantitative validation of horizontal fragmentation in ROCK skills.

**Features**:
- Inventory analysis by content area, grade level, and education authority
- Pattern detection for similar skills across states
- Redundancy ratio calculations
- Visualization of fragmentation patterns
- Example extraction for documentation

**Usage**:
```bash
cd rock-skills/analysis
jupyter notebook notebooks/redundancy-analysis.ipynb
```

**Outputs**:
- Redundancy statistics and metrics
- Fragmentation visualizations
- Example skill clusters

---

### 2. Variant Classifier (`scripts/variant_classifier.py`)

**Purpose**: Classify ROCK skills into State A (cross-state variants) vs State B (grade progressions).

**Classification Logic**:
- **State A (Cross-State Variants)**: 
  - Normalized name similarity > 0.85
  - Grade difference ≤ 1
  - Different education authorities
  - **Use Case**: Enable P&I to tag content once and inherit all state variants

- **State B (Grade Progressions)**:
  - Normalized name similarity 0.6-0.8 (related but not identical)
  - Sequential grades (spiraling)
  - Same authority or universal (CCSS)
  - **Use Case**: Learning progression navigation with prerequisite chains

**Usage**:
```bash
cd rock-skills/analysis
python3 scripts/variant_classifier.py
```

**Outputs**:
- `variant-classification-report.csv`: All 8,224 skills classified with metadata
- `variant-classification-report_summary.csv`: Group-level summary statistics

**Output Fields**:
- `EQUIVALENCE_TYPE`: "state-variant", "grade-progression", or "unique"
- `EQUIVALENCE_GROUP_ID`: UUID linking related skills
- `PREREQUISITE_SKILL_IDS`: For State B, the prior skill in progression
- `COMPLEXITY_LEVEL`: Difficulty ranking within State B chains
- `AUTHORITIES`: Pipe-separated list of education authorities

---

### 3. LLM Mapping Assistant (`modules/llm_mapping_assistant.py`)

**Purpose**: Accelerate ROCK skill-to-taxonomy mapping using AWS Bedrock (Claude Sonnet 4.5).

**Two-Stage Approach**:
1. **Semantic Search**: Embedding-based retrieval (narrow to top 20 candidates)
2. **LLM Reasoning**: Claude ranks candidates with confidence and rationale

**Configuration**: Uses AWS Bedrock with the pattern from `textbook-schema-generator`:
- Model: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Region: `us-east-1`
- Timeout: 600s with 3 retries
- Max tokens: 4,000 per request

**Usage**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'analysis'))

from modules.llm_mapping_assistant import LLMMapperAssistant
import pandas as pd

# Load data
taxonomy_df = pd.read_csv('POC_science_of_reading_literacy_skills_taxonomy.csv')

# Initialize assistant
assistant = LLMMapperAssistant(taxonomy_df)

# Map a skill
suggestions = assistant.suggest_mappings(
    skill_id='SKILL_12345',
    skill_name='Identify main idea in informational text',
    skill_area='Reading Comprehension',
    content_area='ELA',
    grade_level='Grade 3',
    top_k=5
)

# Print suggestions
for suggestion in suggestions:
    print(f"{suggestion['taxonomy_path']}")
    print(f"Confidence: {suggestion['confidence']}")
    print(f"Rationale: {suggestion['rationale']}")
```

**Cost Tracking**:
```python
# Get usage statistics
stats = assistant.get_usage_stats()
print(f"API Calls: {stats['api_calls']}")
print(f"Total Tokens: {stats['total_tokens']}")
print(f"Estimated Cost: ${stats['estimated_cost_usd']:.2f}")
```

---

### 4. Batch Mapping Pipeline (`scripts/batch_map_skills.py`)

**Purpose**: Process large batches of skills with checkpoint/resume capability.

**Features**:
- Checkpoint saving every N skills
- Resume from previous run
- Human review queue for low-confidence mappings
- Progress tracking and logging
- Cost monitoring
- Error handling and recovery

**Usage**:
```bash
cd rock-skills/analysis

# Map first 100 ELA skills
python3 scripts/batch_map_skills.py \
  --start-index 0 \
  --batch-size 100 \
  --content-area "English Language Arts" \
  --checkpoint-interval 10 \
  --output-dir ./outputs

# Resume from checkpoint
python3 scripts/batch_map_skills.py \
  --start-index 100 \
  --batch-size 100 \
  --resume-from outputs/checkpoint_20251014_120000.csv \
  --output-dir ./outputs
```

**Arguments**:
- `--start-index`: Starting skill index (default: 0)
- `--batch-size`: Number of skills to process (default: all)
- `--content-area`: Filter to specific area (e.g., 'ELA', 'Math')
- `--checkpoint-interval`: Save every N skills (default: 10)
- `--resume-from`: Path to checkpoint file
- `--output-dir`: Output directory (default: current)

**Outputs**:
- `llm_assisted_mappings_YYYYMMDD_HHMMSS.csv`: All mappings
- `review_queue_YYYYMMDD_HHMMSS.csv`: Low-confidence mappings needing review
- `mapping_summary_YYYYMMDD_HHMMSS.txt`: Session statistics
- `checkpoint_YYYYMMDD_HHMMSS.csv`: Resume point

**Review Queue Criteria**:
- Confidence marked as "Low" by LLM
- Semantic similarity < 0.5

---

### 5. Semantic Similarity Tool (`semantic_similarity.py`)

**Purpose**: Embedding-based skill matching for taxonomy mapping assistance.

**Features**:
- Pre-compute embeddings for all taxonomy nodes
- Fast semantic search using sentence transformers
- Cosine similarity scoring

**Usage**: Primarily used as a library by `llm_mapping_assistant.py`.

---

## Data Files

### Generated Outputs

- **`variant-classification-report.csv`**: All 8,224 skills with State A/B classification
- **`variant-classification-report_summary.csv`**: Group-level statistics
- **`llm_assisted_mappings_*.csv`**: LLM-generated skill-to-taxonomy mappings
- **`review_queue_*.csv`**: Mappings requiring human review
- **`skill-taxonomy-mapping.csv`**: Validated mappings (manual + LLM-assisted)
- **`master-concepts.csv`**: Master concepts grouping fragmented skills
- **`fragmentation-examples.csv`**: Concrete examples of fragmentation

### Input Data

- **`metadata-gaps.md`**: Documentation of missing ROCK schema metadata

---

## Requirements

Install dependencies:
```bash
pip3 install -r requirements.txt
```

**Key Dependencies**:
- `pandas`, `numpy`: Data manipulation
- `scikit-learn`: TF-IDF, cosine similarity
- `matplotlib`, `seaborn`, `plotly`: Visualization
- `sentence-transformers`: Semantic embeddings
- `boto3`: AWS Bedrock integration
- `scipy`: Statistical analysis
- `networkx`: Prerequisite graph visualization

---

## Workflow

### Phase 1: Quantitative Validation
1. Run `redundancy-analysis.ipynb` to quantify fragmentation
2. Generate visualizations and statistics
3. Extract examples for documentation

### Phase 2: Variant Classification
1. Run `variant_classifier.py` to classify all skills
2. Review classification report
3. Identify State A groups (for P&I content tagging)
4. Identify State B chains (for learning progressions)

### Phase 3: LLM-Assisted Mapping
1. Test with `llm_mapping_assistant.py` on sample skills
2. Run `batch_map_skills.py` for full dataset
3. Review low-confidence mappings in review queue
4. Validate and export final mappings

---

## Cost Estimates

### LLM Usage (AWS Bedrock Claude Sonnet 4.5)

**Per-Skill Estimate**:
- Tokens per skill: ~1,500 (input) + ~500 (output) = ~2,000 total
- Cost per skill: ~$0.006 (using $0.003 per 1K tokens estimate)

**Full Dataset (8,224 skills)**:
- Total tokens: ~16.4M
- Estimated cost: **~$50**

**Filtered (2,000 ELA skills)**:
- Total tokens: ~4M
- Estimated cost: **~$12**

*Note: Actual costs depend on final token usage and AWS pricing.*

---

## Output Schema

### Variant Classification Report Columns

| Column | Description |
|--------|-------------|
| `SKILL_ID` | ROCK skill identifier |
| `SKILL_NAME` | Full skill name |
| `NORMALIZED_NAME` | Normalized for similarity comparison |
| `CONTENT_AREA_NAME` | Subject area (ELA, Math, Science, etc.) |
| `GRADE_LEVEL_NAME` | Grade level string |
| `GRADE_NUM` | Numeric grade (K=0, High School=12) |
| `SKILL_AREA_NAME` | ROCK skill area |
| `EQUIVALENCE_TYPE` | "state-variant", "grade-progression", "unique" |
| `EQUIVALENCE_GROUP_ID` | UUID for grouping related skills |
| `PREREQUISITE_SKILL_IDS` | Previous skill in State B chain |
| `COMPLEXITY_LEVEL` | 1-5 difficulty ranking for State B |
| `AUTHORITIES` | Education authorities using this skill |

### LLM Mapping Report Columns

| Column | Description |
|--------|-------------|
| `skill_id` | ROCK skill identifier |
| `skill_name` | Full skill name |
| `skill_area` | ROCK skill area |
| `content_area` | Subject area |
| `grade_level` | Grade level |
| `taxonomy_path` | Full path in Science of Reading taxonomy |
| `confidence` | "High", "Medium", "Low" |
| `rationale` | LLM's reasoning for the mapping |
| `semantic_similarity` | Cosine similarity score (0-1) |
| `needs_review` | Boolean flag for human review |
| `alternative_1` | Second-best mapping option |
| `alternative_2` | Third-best mapping option |
| `status` | "success", "error", "no_suggestions" |
| `timestamp` | Processing timestamp |

---

## Troubleshooting

### Common Issues

**1. AWS Credentials Not Configured**
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**2. Memory Issues with Large Files**
- The scripts use chunked loading for `STANDARD_SKILLS.csv` (591MB)
- Default: 2M rows (~200MB in memory)
- Adjust chunk size in code if needed

**3. Slow Classification Performance**
- State A/B classification uses TF-IDF similarity matrices
- For 8,224 skills, expect 15-30 minutes runtime
- Progress is logged to console

**4. LLM Rate Limiting**
- AWS Bedrock has default quotas (e.g., 50 requests/minute)
- The batch pipeline includes retry logic
- For large batches, consider adding delays between requests

---

## Next Steps

### Immediate (Post-Hackathon)
- [ ] Run variant classifier on all skills
- [ ] Map 100-200 ELA skills using LLM assistant
- [ ] Validate mapping accuracy against manual mappings
- [ ] Refine LLM prompts based on accuracy results

### Short-Term (1-2 months)
- [ ] Complete ELA skill mappings (~2,000 skills)
- [ ] Research Math taxonomy frameworks
- [ ] Pilot Math taxonomy structure
- [ ] Map 10-20 Math skills

### Long-Term (3-6 months)
- [ ] Production database design (PostgreSQL)
- [ ] API for taxonomy bridge layer (FastAPI)
- [ ] Integration with P&I product systems
- [ ] Scale to all content areas

---

## Support

For questions or issues:
- Review `rock-skills/docs/` for architecture context
- Check `rock-skills/README.md` for project overview
- Consult `rock-skills-discovery-strategy.plan.md` for full research plan

---

**Last Updated**: 2025-10-14  
**Author**: ROCK Skills Hackathon Team

