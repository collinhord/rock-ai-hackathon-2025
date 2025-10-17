# Project 3: Base Skills Taxonomy

Build a universal taxonomy of core competencies from ROCK skills, aligned with scientific frameworks.

## Quick Start

```bash
cd 03-base-skills-taxonomy
pip install -r requirements.txt

# Build taxonomy
python src/taxonomy/taxonomy_builder.py

# Validate coverage
python scripts/validate_taxonomy.py

# Analyze frameworks (PDFs in frameworks/input/)
python frameworks/analyze_ela_frameworks.py
```

## What This Does

- **Creates Base Skills**: Universal taxonomy of ~500-1,000 core competencies
- **Maps ROCK Skills**: Links 8,354 ROCK skills to base skills
- **Aligns Frameworks**: Maps to Science of Reading, Math progressions, etc.
- **Analyzes Framework PDFs**: Extracts concepts from research documents

## Structure

```
03-base-skills-taxonomy/
├── frameworks/               # Framework analysis (project-specific)
│   ├── input/                # Framework PDFs
│   │   ├── ela/              # Science of Reading PDFs
│   │   ├── math/             # Cambridge Math ontology
│   │   └── science/          # Science frameworks
│   ├── output/               # Analysis results
│   ├── analyze_ela_frameworks.py
│   ├── process_framework_pdfs.py
│   ├── validate_taxonomy_coverage.py
│   └── science_of_reading.csv
├── src/                      # Core taxonomy code
├── scripts/                  # Automation scripts
└── docs/                     # Documentation
```

## Frameworks

This project includes **framework-specific data and tools**:

- **Science of Reading** (Scarborough's Reading Rope, Duke 2021)
- **Cambridge Mathematics Ontology**
- Framework extraction and validation scripts
- Taxonomy coverage analysis

All framework data is **project-specific** and lives in `frameworks/`. See `frameworks/README.md` for details.

## Dependencies

- **Project 2**: Uses master concepts as input
- **Project 1**: Uses metadata to inform categorization
- **Frameworks**: Science of Reading, Cambridge Math (in frameworks/)

See [PROJECT_GOALS.md](./PROJECT_GOALS.md) for comprehensive documentation.

