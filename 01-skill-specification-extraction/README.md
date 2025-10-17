# Project 1: Skill Specification Extraction

Extract comprehensive metadata and specifications from ROCK skill descriptions using hybrid NLP + LLM + rule-based inference.

## Quick Start

### Prerequisites

- Python 3.9+
- AWS credentials configured (for Bedrock access)
- Snowflake access (or use local CSV files)

### Installation

```bash
cd 01-skill-specification-extraction

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_lg
```

### Basic Usage

```python
from src.extractors import enhanced_metadata_extractor, spacy_processor
from shared.data_access import SkillDataLoader

# Load skills
loader = SkillDataLoader()
skills = loader.get_all_skills(content_area='English Language Arts')

# Extract metadata using spaCy
processor = spacy_processor.SpacyProcessor()
metadata = processor.extract_metadata(skills.iloc[0]['SKILL_NAME'])

print(f"Actions: {metadata['actions']}")
print(f"Targets: {metadata['targets']}")
print(f"Qualifiers: {metadata['qualifiers']}")
```

### Run Full Extraction Pipeline

```bash
# Extract metadata from all ELA skills
python scripts/extract_all_skills.sh --content-area "English Language Arts"

# Results saved to:
# - outputs/production/skill_metadata_enhanced.csv
# - outputs/production/extraction_summary.txt
```

### Analyze Results

```bash
# Generate quality report
python scripts/analyze_results.py \
    --input outputs/production/skill_metadata_enhanced.csv \
    --output outputs/reports/quality_report.json
```

## What This Project Does

**Input**: ROCK skill descriptions (text)
```
"Identify the main idea in a grade-level informational text"
```

**Output**: Structured metadata (23 fields)
```json
{
  "skill_id": 12345,
  "actions": ["identify"],
  "targets": ["main idea"],
  "qualifiers": ["grade-level", "informational"],
  "cognitive_level": "understand",
  "domain": "reading comprehension",
  "text_dependent": true,
  "complexity_band": "grade-level",
  "support_level": "independent",
  "context_type": "informational"
}
```

## Key Files

### Source Code

- `src/extractors/enhanced_metadata_extractor.py` - Main extraction logic with LLM
- `src/extractors/spacy_processor.py` - spaCy NLP extraction
- `src/extractors/metadata_extractor.py` - Base metadata extractor
- `src/prompts/` - LLM prompts as code (coming soon)
- `src/utils/validator.py` - Data validation utilities

### Scripts

- `scripts/extract_all_skills.sh` - Batch extraction pipeline
- `scripts/analyze_results.py` - Quality analysis
- `scripts/generate_validation_sample.py` - Create validation datasets

### Tests

- `tests/test_spacy_integration.py` - spaCy extraction tests
- `tests/test_data_validation.py` - Data quality tests

### Documentation

- `PROJECT_GOALS.md` - Comprehensive project goals and metrics
- `docs/METADATA_FIELD_REFERENCE.md` - All 29 metadata fields explained
- `docs/SPECIFICATION_INFERENCE_FRAMEWORK.md` - Inference rule documentation
- `docs/METADATA_ENRICHMENT_GUIDE.md` - How to use enrichment features

### Outputs (gitignored)

- `outputs/production/` - Production extraction results
- `outputs/validation/` - Validation samples
- `outputs/reports/` - Quality reports

## Metadata Fields Extracted

### Rule-Based Extraction (spaCy)

1. **Actions** (verbs): identify, analyze, solve, explain
2. **Targets** (objects): words, sentences, problems, characters
3. **Qualifiers** (modifiers): simple, complex, grade-level, multistep
4. **Grammatical Features**: tense, voice, modality
5. **Entities**: proper nouns, numbers, dates

### LLM-Assisted Extraction

6. **Cognitive Level**: remember, understand, apply, analyze, evaluate, create
7. **Domain**: reading comprehension, phonics, vocabulary, fluency
8. **Context**: informational text, fictional text, mixed media

### Inference Rules

9. **Text-Dependent**: requires reading passage vs. standalone
10. **Complexity Band**: foundational, grade-level, advanced
11. **Support Level**: scaffolded, independent, transfer
12. **Assessment Type**: formative, summative, diagnostic

See `docs/METADATA_FIELD_REFERENCE.md` for complete field definitions.

## Pipeline Architecture

```
┌─────────────────┐
│  ROCK Skills    │  Snowflake SKILLS table
│  (8,354 skills) │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  spaCy NLP      │  Extract actions, targets, qualifiers
│  Extraction     │  Fast, deterministic, 90-95% accuracy
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  LLM Enrichment │  Claude 3.5 for cognitive level, domain
│  (selective)    │  Used for 10-20% of ambiguous skills
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Inference      │  Deterministic rules for specifications
│  Engine         │  100% reproducible, explainable
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Output Files   │  skill_metadata_enhanced.csv (23 fields)
│                 │  skill_specifications_inferred.csv (6 fields)
└─────────────────┘
```

## Development

### Adding New Metadata Fields

1. Update `docs/METADATA_FIELD_REFERENCE.md` with field definition
2. Add extraction logic to appropriate extractor
3. Add inference rules if applicable
4. Update tests
5. Update schema files

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_spacy_integration.py -v

# Generate coverage report
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Cost Optimization

- **spaCy extraction**: Free, runs locally
- **LLM usage**: Selective (10-20% of skills)
- **Caching**: Results cached to avoid re-extraction
- **Batch processing**: Process multiple skills per LLM call

**Estimated Cost**: $30-50 for complete extraction of 8,354 skills

## Performance

- **spaCy extraction**: ~100 skills/second
- **LLM extraction**: ~5-10 skills/second (when used)
- **Full pipeline**: ~4-8 hours for 8,354 skills
- **Incremental updates**: <1 hour for 100 new skills

## Troubleshooting

### Common Issues

**Issue**: spaCy model not found
```bash
# Solution: Download language model
python -m spacy download en_core_web_lg
```

**Issue**: AWS Bedrock access denied
```bash
# Solution: Configure AWS credentials
aws configure --profile ai-poc
```

**Issue**: Out of memory during batch processing
```bash
# Solution: Reduce batch size
python scripts/extract_all_skills.sh --batch-size 100
```

See `docs/TROUBLESHOOTING.md` for more solutions.

## Contributing

See `../../CONTRIBUTING.md` for contribution guidelines.

## Related Projects

- **Project 2**: Skill Redundancy Detection (uses metadata from Project 1)
- **Project 3**: Base Skills Taxonomy (uses specifications from Project 1)
- **Shared Infrastructure**: `../../shared/` (data access, LLM, models)

## Links

- [PROJECT_GOALS.md](./PROJECT_GOALS.md) - Comprehensive project goals
- [Metadata Field Reference](./docs/METADATA_FIELD_REFERENCE.md)
- [Specification Inference Framework](./docs/SPECIFICATION_INFERENCE_FRAMEWORK.md)
- [Platform Architecture](../../ARCHITECTURE.md)

---

**Questions or Issues?** Contact ROCK Skills Analysis Team

