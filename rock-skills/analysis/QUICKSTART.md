# Quick Start: ROCK Skills Analysis Tools

Get up and running with the variant classification and LLM-assisted mapping tools in 5 minutes.

## Prerequisites

1. **Python 3.9+** installed
2. **AWS credentials configured** (for LLM mapping)
   ```bash
   aws configure
   # Or set environment variables:
   # export AWS_ACCESS_KEY_ID=your_key
   # export AWS_SECRET_ACCESS_KEY=your_secret
   # export AWS_DEFAULT_REGION=us-east-1
   ```

## Installation

```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis

# Install dependencies
pip3 install -r requirements.txt
```

**Note**: Installation may take 5-10 minutes due to large dependencies (torch, sentence-transformers).

## Quick Test Runs

### 1. Variant Classification (State A vs State B)

Classify all 8,224 ROCK skills into cross-state variants vs grade progressions:

```bash
python3 scripts/variant_classifier.py
```

**Runtime**: ~15-20 minutes  
**Output**:
- `variant-classification-report.csv` - All skills with classifications (2.6MB)
- `variant-classification-report_summary.csv` - Group summary (86KB)

**Preview Results**:
```bash
# View State A groups (cross-state variants)
head -20 variant-classification-report_summary.csv | column -t -s,

# View State B chains (grade progressions)
grep "grade-progression" variant-classification-report_summary.csv | head -10
```

**Expected Output**:
```
============================================================
CLASSIFICATION SUMMARY
============================================================

State A (cross-state variants): 383 skills
State B (grade progressions): 569 skills
Unique skills: 7,272 skills

State A groups: 187
State B chains: 220
```

### 2. LLM-Assisted Mapping (Test Mode)

Test LLM mapping on 3 sample ELA skills:

```bash
python3 llm_mapping_assistant.py
```

**Runtime**: ~30-60 seconds (3 skills × ~10s each)  
**Cost**: ~$0.05

**Expected Output**:
```
TESTING WITH SAMPLE SKILLS
============================================================

Suggestions for: Identify main idea in informational text

  1. Reading Comprehension > Comprehension Strategies > Main Idea
     Confidence: High
     Rationale: Direct alignment with main idea identification objective
     Semantic Similarity: 0.894

  2. Reading Comprehension > Text Features > Organizational Structure
     Confidence: Medium
     Rationale: Related skill for understanding text organization
```

### 3. Batch Mapping (Small Scale)

Map 10 ELA skills using LLM assistance:

```bash
python3 scripts/batch_map_skills.py \
  --start-index 0 \
  --batch-size 10 \
  --content-area "English Language Arts" \
  --checkpoint-interval 5 \
  --output-dir ./outputs
```

**Runtime**: ~2-3 minutes  
**Cost**: ~$0.15  
**Output**:
- `llm_assisted_mappings_YYYYMMDD_HHMMSS.csv` - Mapping results
- `mapping_summary_YYYYMMDD_HHMMSS.txt` - Session statistics
- `checkpoint_YYYYMMDD_HHMMSS.csv` - Resume point

**Monitor Progress**:
```
[1/10] Processing: Identify main idea in informational text...
  ✓ Mapped with confidence: High

[2/10] Processing: Determine meaning of unknown words using context...
  ✓ Mapped with confidence: Medium

--- Checkpoint at 5 skills ---
✓ Checkpoint saved: checkpoint_20251014_161234.csv
```

## Common Workflows

### Workflow 1: Full Classification + Sample Mapping

```bash
# Step 1: Classify all skills (one-time, ~20 min)
python3 scripts/variant_classifier.py

# Step 2: Map 50 ELA skills to test LLM accuracy
python3 scripts/batch_map_skills.py \
  --start-index 0 \
  --batch-size 50 \
  --content-area "English Language Arts" \
  --output-dir ./outputs

# Step 3: Review low-confidence mappings
head outputs/review_queue_*.csv
```

### Workflow 2: Resume from Checkpoint

```bash
# Initial run (stopped at 50 skills)
python3 scripts/batch_map_skills.py \
  --start-index 0 \
  --batch-size 100 \
  --content-area "English Language Arts" \
  --output-dir ./outputs

# Resume from checkpoint
python3 scripts/batch_map_skills.py \
  --start-index 50 \
  --batch-size 100 \
  --content-area "English Language Arts" \
  --resume-from outputs/checkpoint_20251014_120000.csv \
  --output-dir ./outputs
```

### Workflow 3: Full ELA Mapping (~2,000 skills)

```bash
# Run in batches to avoid timeouts
for i in {0..2000..100}; do
  python3 scripts/batch_map_skills.py \
    --start-index $i \
    --batch-size 100 \
    --content-area "English Language Arts" \
    --checkpoint-interval 25 \
    --output-dir ./outputs
  
  # Small delay between batches
  sleep 60
done
```

**Estimated**:
- **Runtime**: 6-8 hours
- **Cost**: ~$50-60
- **Output**: 2,000 ELA skills mapped to Science of Reading taxonomy

## Interpreting Results

### Variant Classification Report

**Key Columns**:
- `EQUIVALENCE_TYPE`: "state-variant", "grade-progression", "unique"
- `EQUIVALENCE_GROUP_ID`: UUID linking related skills
- `PREREQUISITE_SKILL_IDS`: Prior skill in State B chain
- `COMPLEXITY_LEVEL`: Difficulty ranking (1-5) for State B

**Example Row (State A)**:
```csv
SKILL_12345,Blend phonemes to form words,blend phonemes form words,ELA,Grade K,0,Phonemic Awareness,state-variant,uuid-abc123,,,TX|CA|CCSS
```

**Example Row (State B)**:
```csv
SKILL_67890,Compose informative text grade 3,compose informative text,ELA,Grade 3,3,Writing,grade-progression,uuid-def456,SKILL_67889,3,CCSS
```

### LLM Mapping Report

**Key Columns**:
- `confidence`: "High", "Medium", "Low"
- `needs_review`: `True` if confidence=Low or similarity<0.5
- `semantic_similarity`: 0-1 score (higher = better match)
- `alternative_1/2`: Backup options

**Example Row**:
```csv
SKILL_12345,Identify main idea,Reading Comprehension,ELA,Grade 3,"Reading > Comprehension > Main Idea",High,"Direct alignment with main idea objective",0.894,False,"Reading > Structure","Reading > Details",success,2025-10-14T16:30:00
```

### Review Queue

Skills flagged for human review appear in `review_queue_*.csv`. Criteria:
- Confidence = "Low"
- Semantic similarity < 0.5
- Ambiguous or multiple possible mappings

**Action**: Manually review and validate or correct mappings.

## Troubleshooting

### Issue: AWS Credentials Error

```
ClientError: An error occurred (UnrecognizedClientException) when calling the InvokeModel operation
```

**Fix**:
```bash
aws configure
# Enter your AWS credentials
```

### Issue: Out of Memory

```
MemoryError: Unable to allocate array
```

**Fix**: Reduce chunk size in `variant_classifier.py`:
```python
# Line 490: Reduce from 100000 to 50000
for i, chunk in enumerate(pd.read_csv(..., chunksize=50000)):
```

### Issue: Bedrock Rate Limiting

```
ThrottlingException: Rate exceeded
```

**Fix**: Add delay in `batch_map_skills.py`:
```python
import time
result = self.map_skill(skill_row)
time.sleep(1)  # Add 1s delay between requests
```

### Issue: Slow Classification

**Expected**: 15-30 minutes for 8,224 skills  
**If slower**: Check CPU usage, close other applications

## Next Steps

After running the tools:

1. **Review Classification Results**
   - Spot-check State A groups for accuracy
   - Validate State B chains make sense developmentally

2. **Validate LLM Mappings**
   - Compare against manual mappings (if available)
   - Review low-confidence items in review queue
   - Refine prompts if accuracy < 75%

3. **Scale to Production**
   - Map all ELA skills (~2,000)
   - Research Math taxonomy frameworks
   - Design PostgreSQL schema for production
   - Build FastAPI for taxonomy bridge layer

## Support & Documentation

- **Full README**: `analysis/README.md`
- **Problem Statement**: `docs/2-problem-statement.md`
- **Project Overview**: `rock-skills/README.md`
- **Research Plan**: `rock-skills-discovery-strategy.plan.md`

## Cost Summary

| Task | Runtime | AWS Cost | Total |
|------|---------|----------|-------|
| Variant Classification | 20 min | $0 | $0 |
| LLM Test (3 skills) | 1 min | $0.05 | $0.05 |
| Batch Mapping (50 skills) | 8 min | $1.20 | $1.20 |
| Full ELA Mapping (2,000) | 6-8 hrs | $50-60 | $50-60 |

**Budget Recommendation**: $100 for initial exploration phase

---

**Happy Analyzing!** 🚀

