# Data Directory

This directory contains **shared data** used across multiple projects. Project-specific data and frameworks are located within their respective project directories.

## Structure

```
data/
├── reference/              # Reference data used by all projects
│   ├── rock_schemas/       # ROCK database CSVs (Snowflake exports)
│   └── standards/          # State standards reference data
├── samples/                # Sample/test data
│   └── sample_data.csv     # Generic test data
└── cache/                  # Snowflake query cache (gitignored)
```

## ROCK Schemas

**Location**: `data/reference/rock_schemas/`  
**Source**: Snowflake ROCK_DB.SKILLS schema  
**Used By**: All three projects

Contains exported CSV files from the ROCK database:
- `SKILLS.csv` - 8,355 ROCK skills
- `SKILL_AREAS.csv` - Skill area classifications
- `STANDARDS.csv` - State standards
- `STANDARD_SKILLS.csv` - Skill-to-standard mappings
- `STANDARD_SETS.csv` - Standard sets by state
- `STANDARD_SET_DOMAINS.csv` - Domain classifications
- `STANDARD_SET_DOMAIN_GROUPS.csv` - Domain groups

## Samples

**Location**: `data/samples/`  
**Purpose**: Test data for development and validation

Contains small sample datasets for:
- Unit testing
- Integration testing
- Demo purposes
- Development without Snowflake access

## Cache

**Location**: `data/cache/` (gitignored)  
**Purpose**: Local cache for Snowflake queries

The shared data access layer (`shared/data_access/snowflake_connector.py`) caches query results here to:
- Reduce Snowflake query costs
- Speed up development iteration
- Enable offline development

Cache files are automatically managed and excluded from git.

## Project-Specific Data

**Note**: Framework-specific data is **NOT** in this shared directory.

### Framework Data → Project 3
**Location**: `03-base-skills-taxonomy/frameworks/`  
**Reason**: 100% Project 3 specific

Contains:
- Framework PDFs (Science of Reading, Cambridge Math)
- Framework analysis scripts
- Framework extraction outputs
- Taxonomy validation results

See `03-base-skills-taxonomy/frameworks/README.md` for details.

## Data Access

All projects should use the shared data loader:

```python
from shared.data_access import SkillDataLoader

# Load ROCK skills
loader = SkillDataLoader()
skills = loader.get_all_skills()

# Filter by content area
ela_skills = loader.get_all_skills(content_area='English Language Arts')

# Uses caching automatically
```

## Adding New Reference Data

When adding new shared reference data:

1. Place in `data/reference/<category>/`
2. Update this README
3. Update `shared/data_access/` if new loader methods needed
4. **If project-specific**: Put in project directory, not here

## Guidelines

**✅ Store here**:
- ROCK database exports (used by all projects)
- State standards (used by multiple projects)
- Generic sample/test data
- Shared reference datasets

**❌ Don't store here**:
- Project-specific frameworks (→ Project 3)
- Project-specific analysis outputs (→ project/outputs/)
- Temporary files
- Large binary files
- Generated data (use project outputs/)

---

**Last Updated**: October 17, 2025

