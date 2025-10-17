# Project 2: Skill Redundancy and Relationships

Identify redundant skills, create master concepts, and establish relationships to reduce apparent skill count by 60-75%.

## Quick Start

```bash
cd 02-skill-redundancy-relationships
pip install -r requirements.txt

# Run redundancy detection
python src/clustering/variant_classifier.py

# Generate master concepts
python src/clustering/master_concept_generator.py

# Results in outputs/master_concepts/ and outputs/relationships/
```

## What This Does

- **Detects Redundancy**: Finds duplicate and variant skills across states/grades
- **Creates Master Concepts**: Groups related skills under unified concepts
- **Maps Relationships**: Classifications (duplicate, variant, prerequisite, related)

## Key Files

- `src/clustering/variant_classifier.py` - Detect redundant skills
- `src/clustering/master_concept_generator.py` - Generate master concepts
- `src/detectors/semantic_similarity.py` - Similarity computations
- `notebooks/redundancy-analysis.ipynb` - Analysis and visualization

See [PROJECT_GOALS.md](./PROJECT_GOALS.md) for comprehensive documentation.

