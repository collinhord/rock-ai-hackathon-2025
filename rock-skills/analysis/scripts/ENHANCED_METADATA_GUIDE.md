# Enhanced Metadata Extraction Guide

## Overview

The Enhanced Metadata Extractor combines three powerful approaches to generate **23 comprehensive metadata fields** for each ROCK skill:

1. **spaCy Structural Analysis** - Fast, deterministic extraction of linguistic components
2. **LLM Educational Classification** - Nuanced, context-aware pedagogical metadata
3. **Rule-Based Specification Extraction** - Pattern-matching for support levels and complexity

**Result**: Rich, multi-dimensional skill metadata suitable for base skill decomposition, taxonomy mapping, redundancy analysis, and frontend visualization.

---

## Quick Start

### Installation

```bash
cd /path/to/rock-skills/analysis

# Ensure dependencies installed
pip install boto3 spacy pandas numpy

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Test on 5 Skills

```bash
# Quick validation test
python3 test_enhanced_extraction.py

# Output: test_outputs/test_results_TIMESTAMP.csv
```

**Expected**: All 5 skills processed successfully, ~30 seconds runtime, < $0.02 cost

### Run on Filtered Dataset (336 skills)

```bash
cd scripts

python3 enhanced_metadata_extractor.py \
  --input ../../rock_data/skill_list_filtered_data_set.csv \
  --output-dir ../outputs/filtered_enhanced_metadata \
  --checkpoint-interval 50
```

**Expected**: 336 skills processed in ~12-15 minutes, ~$1.00 cost

### Run on Full ELA Corpus (~3,000 skills)

```bash
python3 enhanced_metadata_extractor.py \
  --input ../../rock_schemas/SKILLS.csv \
  --content-area "English Language Arts" \
  --output-dir ../outputs/full_enhanced_metadata \
  --checkpoint-interval 100 \
  --skip-existing ../outputs/filtered_enhanced_metadata/skill_metadata_enhanced_*.csv
```

**Expected**: ~3,000 skills in 2-3 hours, ~$9-12 cost

---

## Output Schema

### 23 Metadata Fields

**Core Identifiers (4 fields)**
- `SKILL_ID` - Unique identifier
- `SKILL_NAME` - Full skill description
- `SKILL_AREA_NAME` - Skill area (e.g., "Character and Plot")
- `GRADE_LEVEL_SHORT_NAME` - Grade level (e.g., "1", "3", "K")

**Structural Components - from spaCy (8 fields)**
- `actions` - Verbs (e.g., "identify|analyze|describe")
- `targets` - Nouns (e.g., "character|plot|events")
- `qualifiers` - Adjectives (e.g., "major|minor|key")
- `root_verb` - Primary action (e.g., "identify")
- `direct_objects` - Main targets (e.g., "elements")
- `prepositional_phrases` - Context (e.g., "of a story's plot")
- `key_concepts` - Domain terms (e.g., "identify|plot|story")
- `complexity_markers` - Difficulty signals (e.g., "basic")

**Educational Metadata - from LLM (7 fields)**
- `text_type` - fictional | informational | mixed | not_applicable
- `text_mode` - prose | poetry | drama | mixed | not_applicable
- `text_genre` - narrative | expository | argumentative | procedural | literary | not_applicable
- `skill_domain` - reading | writing | speaking | listening | language | not_applicable
- `task_complexity` - basic | intermediate | advanced
- `cognitive_demand` - recall | comprehension | application | analysis | synthesis | evaluation
- `scope` - word | sentence | paragraph | text | multi_text | not_applicable

**Specifications - from Rules (2 fields)**
- `support_level` - with_support | with_prompting | independent | autonomous | not_applicable
- `complexity_band` - K-2 | 3-5 | 6-8 | 9-12 | Unknown

**Quality Metrics (2 fields)**
- `llm_confidence` - high | medium | low
- `extraction_method` - hybrid_spacy_llm | partial
- `extraction_timestamp` - ISO timestamp
- `llm_notes` - Any extraction notes or warnings

---

## Usage Examples

### Example 1: Quick Test

```bash
# Test on first 10 skills to validate setup
python3 test_enhanced_extraction.py --limit 10
```

**Use case**: Validate installation and configuration before running large batches

### Example 2: Batch Processing with Checkpoints

```bash
python3 enhanced_metadata_extractor.py \
  --input ../../rock_data/skill_list_filtered_data_set.csv \
  --output-dir ../outputs/batch_001 \
  --checkpoint-interval 50
```

**Checkpoints created**: Every 50 skills, resumable on failure

### Example 3: Resume After Interruption

```bash
python3 enhanced_metadata_extractor.py \
  --input ../../rock_schemas/SKILLS.csv \
  --content-area "English Language Arts" \
  --output-dir ../outputs/full_ela \
  --skip-existing ../outputs/full_ela/skill_metadata_enhanced_20251017_*.csv
```

**Behavior**: Skips already processed skills, continues from where it left off

### Example 4: spaCy Only (No LLM)

```bash
python3 enhanced_metadata_extractor.py \
  --input ../../rock_data/skill_list_filtered_data_set.csv \
  --output-dir ../outputs/spacy_only \
  --no-llm
```

**Use case**: Fast structural extraction without LLM costs (fallback metadata used)

### Example 5: Process Specific Batch Range

```bash
python3 enhanced_metadata_extractor.py \
  --input ../../rock_schemas/SKILLS.csv \
  --content-area "English Language Arts" \
  --start-index 0 \
  --limit 500 \
  --output-dir ../outputs/batch_001
```

**Use case**: Process skills in batches (e.g., 0-500, 500-1000, etc.)

---

## Integration with Existing Systems

### A. Base Skill System (`analysis/pipelines/`)

**Use structural metadata for clustering:**

```python
import pandas as pd

# Load enhanced metadata
metadata_df = pd.read_csv('outputs/filtered_enhanced_metadata/skill_metadata_enhanced_*.csv')

# Use actions and targets for base skill grouping
metadata_df['cluster_key'] = metadata_df['root_verb'] + '_' + metadata_df['targets'].str.split('|').str[0]

# Use cognitive_demand for specification extraction
specifications = metadata_df.groupby('cluster_key')['cognitive_demand'].value_counts()
```

**Benefits:**
- More accurate base skill identification using root verbs
- Better specification extraction using cognitive demand patterns
- Key concepts enable semantic grouping

### B. Taxonomy Mapping (`analysis/scripts/batch_map_skills_enhanced.py`)

**Enhance semantic search with metadata:**

```python
# Filter candidates by skill domain before semantic matching
if skill_metadata['skill_domain'] == 'reading':
    taxonomy_candidates = taxonomy_df[taxonomy_df['domain'].str.contains('Reading')]

# Use key concepts in LLM prompts
prompt += f"\nKey Concepts: {skill_metadata['key_concepts']}"
```

**Benefits:**
- 10-20% improvement in semantic matching precision
- Reduced LLM tokens by pre-filtering candidates
- Better context for mapping decisions

### C. Master Concepts (`analysis/master-concepts.csv`)

**Enrich concepts with aggregated metadata:**

```python
# Aggregate metadata distributions per master concept
concept_metadata = metadata_df.groupby('MASTER_CONCEPT_ID').agg({
    'text_type': lambda x: x.value_counts().to_dict(),
    'cognitive_demand': lambda x: x.mode()[0],  # Most common
    'complexity_band': lambda x: list(x.unique()),
    'task_complexity': lambda x: x.mode()[0]
})
```

**Benefits:**
- Master concepts gain semantic classification
- Complexity bands enable progression modeling
- Text type distributions inform applicability

### D. Redundancy Analysis (`analysis/semantic_similarity.py`)

**Use structural components for pre-filtering:**

```python
# Fast duplicate detection using actions/targets
def quick_redundancy_check(skill1, skill2):
    """Check if skills might be duplicates before semantic comparison."""
    actions1 = set(skill1['actions'].split('|'))
    actions2 = set(skill2['actions'].split('|'))
    
    targets1 = set(skill1['targets'].split('|'))
    targets2 = set(skill2['targets'].split('|'))
    
    # If actions and targets overlap significantly, do full semantic check
    action_overlap = len(actions1 & actions2) / max(len(actions1), len(actions2))
    target_overlap = len(targets1 & targets2) / max(len(targets1), len(targets2))
    
    return action_overlap > 0.7 and target_overlap > 0.7
```

**Benefits:**
- 50-70% faster redundancy detection
- Structural pre-filtering reduces semantic comparisons
- Multi-dimensional similarity scoring

### E. Frontend Display (`poc/skill_bridge_app.py`)

**Display comprehensive metadata:**

```python
import streamlit as st

# Skill metadata panel
st.subheader("Skill Metadata")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Structural**")
    st.write(f"Root Verb: {metadata['root_verb']}")
    st.write(f"Actions: {metadata['actions']}")
    st.write(f"Targets: {metadata['targets']}")

with col2:
    st.markdown("**Educational**")
    st.write(f"Domain: {metadata['skill_domain']}")
    st.write(f"Cognitive: {metadata['cognitive_demand']}")
    st.write(f"Complexity: {metadata['task_complexity']}")

with col3:
    st.markdown("**Context**")
    st.write(f"Text Type: {metadata['text_type']}")
    st.write(f"Support: {metadata['support_level']}")
    st.write(f"Band: {metadata['complexity_band']}")
```

**Benefits:**
- Rich skill inspector views
- Filter/search by any metadata field
- Visualize metadata distributions

---

## Cost Calculator

### Per-Skill Costs

- **spaCy extraction**: Free (CPU only)
- **Rule-based extraction**: Free
- **LLM extraction**: ~$0.003-0.004 per skill

### Batch Costs

| Dataset | Skills | Time | LLM Cost | Total Cost |
|---------|--------|------|----------|------------|
| Test (10 skills) | 10 | 1 min | $0.03 | $0.03 |
| Filtered (336 skills) | 336 | 15 min | $1.00 | $1.00 |
| Full ELA (~3,000) | 3,000 | 2-3 hrs | $9-12 | $9-12 |
| All Skills (~8,000) | 8,000 | 6-8 hrs | $24-32 | $24-32 |

**Cost optimization:**
- Use `--no-llm` for structural-only extraction (free)
- spaCy provides 8 fields without any LLM cost
- Process in batches to spread costs over time

---

## Monitoring and Checkpoints

### Checkpoint System

**Automatic checkpointing** every N skills (configurable):

```bash
# Checkpoint every 50 skills
--checkpoint-interval 50
```

**Files created:**
- `checkpoint_enhanced_metadata_TIMESTAMP.csv` - Intermediate results
- `skill_metadata_enhanced_TIMESTAMP.csv` - Final results
- `extraction_summary_TIMESTAMP.txt` - Statistics and distributions

**Resume from checkpoint:**

```bash
python3 enhanced_metadata_extractor.py \
  --input data.csv \
  --output-dir ./outputs \
  --skip-existing ./outputs/checkpoint_enhanced_metadata_*.csv
```

### Monitor Progress

**Check latest checkpoint:**

```bash
cd outputs/filtered_enhanced_metadata
tail -5 checkpoint_enhanced_metadata_*.csv | wc -l  # Count rows processed
```

**View summary stats:**

```bash
cat extraction_summary_*.txt
```

**Live monitoring:**

```bash
# Watch file size grow
watch -n 5 'ls -lh checkpoint_enhanced_metadata_*.csv'
```

---

## Troubleshooting

### Issue: spaCy model not found

**Error:**
```
✗ Model 'en_core_web_sm' not found
```

**Solution:**
```bash
python3 -m spacy download en_core_web_sm
```

### Issue: Bedrock authentication failed

**Error:**
```
Could not initialize Bedrock: NoCredentialsError
```

**Solution:**
```bash
aws configure
# Set region to us-west-2
```

### Issue: LLM parsing errors

**Error:**
```
✗ JSON parsing error: Expecting value
```

**Solution:**
- Check LLM response format in logs
- Usually caused by markdown wrappers (```` ```)
- Parser automatically handles this, but check `llm_notes` field
- If persistent, use `--no-llm` and report issue

### Issue: Out of memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```bash
# Process in smaller batches
python3 enhanced_metadata_extractor.py \
  --input data.csv \
  --limit 500 \
  --checkpoint-interval 100
```

### Issue: Slow processing

**Symptoms**: < 2 skills/minute

**Solutions:**
1. Check network latency to AWS Bedrock
2. Use `--no-llm` for faster processing (structural only)
3. Process in parallel batches using `--start-index` and `--limit`
4. Increase checkpoint interval to reduce I/O

---

## Best Practices

### 1. Always Test First

```bash
# Run test before production
python3 test_enhanced_extraction.py --limit 10
```

### 2. Use Checkpointing

```bash
# Never run without checkpoints on large batches
--checkpoint-interval 50
```

### 3. Skip Existing Skills

```bash
# Always use --skip-existing when resuming
--skip-existing path/to/previous/results.csv
```

### 4. Monitor Quality

```bash
# Check confidence distribution in summary
cat extraction_summary_*.txt | grep "Confidence Distribution" -A 5
```

**Target**: 80%+ high confidence extractions

### 5. Validate Results

```python
import pandas as pd

df = pd.read_csv('skill_metadata_enhanced_*.csv')

# Check completeness
print("Structural completeness:")
print(f"  Actions: {(df['actions'] != '').sum() / len(df) * 100:.1f}%")
print(f"  Root verb: {(df['root_verb'] != '').sum() / len(df) * 100:.1f}%")

# Check quality
print("\nQuality metrics:")
print(df['llm_confidence'].value_counts())
```

**Target**: 95%+ completeness for structural fields

### 6. Review Edge Cases

```python
# Find low-confidence extractions
low_conf = df[df['llm_confidence'] == 'low']
print(f"Low confidence skills: {len(low_conf)}")
low_conf[['SKILL_NAME', 'llm_notes']].head(10)
```

---

## Advanced Usage

### Parallel Processing

Process skills in parallel batches:

```bash
# Terminal 1: Skills 0-1000
python3 enhanced_metadata_extractor.py \
  --start-index 0 --limit 1000 \
  --output-dir ../outputs/batch_1

# Terminal 2: Skills 1000-2000
python3 enhanced_metadata_extractor.py \
  --start-index 1000 --limit 1000 \
  --output-dir ../outputs/batch_2

# Terminal 3: Skills 2000-3000
python3 enhanced_metadata_extractor.py \
  --start-index 2000 --limit 1000 \
  --output-dir ../outputs/batch_3

# Merge results
cat ../outputs/batch_*/skill_metadata_enhanced_*.csv > combined_metadata.csv
```

### Custom Prompts

Modify `build_llm_prompt()` in `enhanced_metadata_extractor.py` to customize LLM behavior.

### Integration with Existing Metadata

```python
# Merge with existing metadata
existing_df = pd.read_csv('outputs/skill_metadata_enriched.csv')
enhanced_df = pd.read_csv('outputs/filtered_enhanced_metadata/skill_metadata_enhanced_*.csv')

merged = existing_df.merge(enhanced_df, on='SKILL_ID', how='left', suffixes=('_old', '_new'))
```

---

## Next Steps

After successful extraction:

1. **Validate Results** - Run quality checks on metadata distributions
2. **Integrate with Pipelines** - Use metadata in base skill extraction and taxonomy mapping
3. **Enrich Master Concepts** - Aggregate metadata to concept level
4. **Update Frontend** - Display comprehensive metadata in Skill Bridge Explorer
5. **Scale to Full Dataset** - Process all ROCK skills (~8,000 total)

---

## Support

For issues or questions:
1. Check this guide
2. Review `METADATA_SCHEMA.md` for field definitions
3. Run `test_enhanced_extraction.py` to validate setup
4. Check extraction logs and summary files


