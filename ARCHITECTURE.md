# ROCK Skills Platform - Architecture

**Version**: 2.0  
**Last Updated**: October 17, 2025

## System Overview

The ROCK Skills Platform is a monorepo containing three interconnected projects that form a data pipeline for processing and organizing educational skills data from the ROCK database.

```
┌──────────────────────────────────────────────────────────────────┐
│                    ROCK Skills Platform                           │
│                   (Monorepo Architecture)                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────┐
│  Snowflake   │  ROCK_DB.SKILLS (8,354 skills)
│  ROCK Data   │  
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────────────────────────────────────┐
│  Project 1: Skill Specification Extraction                        │
│  • Extract 23 metadata fields (spaCy NLP)                        │
│  • Infer 6 specifications (rule-based)                           │
│  • Output: skill_metadata_enhanced.csv                           │
└──────┬───────────────────────────────────────────────────────────┘
       │ (metadata enriches)
       ↓
┌──────────────────────────────────────────────────────────────────┐
│  Project 2: Skill Redundancy & Relationships                      │
│  • Detect 60-75% redundancy                                      │
│  • Generate ~2,500 master concepts                               │
│  • Output: master_concepts.csv, skill_relationships.csv          │
└──────┬───────────────────────────────────────────────────────────┘
       │ (master concepts feed)
       ↓
┌──────────────────────────────────────────────────────────────────┐
│  Project 3: Base Skills Taxonomy                                  │
│  • Build universal taxonomy (~500-1,000 base skills)             │
│  • Align to scientific frameworks                                │
│  • Output: base_skills_taxonomy.csv                             │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│   Product    │  Adaptive learning, content alignment, search
│   Features   │
└──────────────┘
```

## Three Project Domains

### Project 1: Skill Specification Extraction
**Directory**: `01-skill-specification-extraction/`  
**Purpose**: Extract machine-readable metadata from skill descriptions  
**Technology**: Python, spaCy NLP, AWS Bedrock (Claude)  
**Input**: ROCK SKILLS table (SKILL_ID, SKILL_NAME)  
**Output**: 29 metadata fields per skill  
**Status**: In Development

**Key Features**:
- Rule-based extraction (spaCy): actions, targets, qualifiers
- LLM-assisted extraction: cognitive level, domain
- Deterministic inference: text_dependent, complexity_band
- Cost-optimized: <$50 for 8,354 skills

### Project 2: Skill Redundancy & Relationships
**Directory**: `02-skill-redundancy-relationships/`  
**Purpose**: Identify redundant skills and create master concepts  
**Technology**: Python, sentence-transformers, scikit-learn  
**Input**: ROCK SKILLS + Project 1 metadata (optional)  
**Output**: Master concepts, skill relationships  
**Status**: Partial Implementation

**Key Features**:
- Semantic similarity using embeddings
- Cross-state variant detection
- Grade progression analysis
- Master concept generation from variant groups

### Project 3: Base Skills Taxonomy
**Directory**: `03-base-skills-taxonomy/`  
**Purpose**: Build universal taxonomy aligned with scientific frameworks  
**Technology**: Python, LLM-assisted categorization  
**Input**: ROCK SKILLS + Project 2 master concepts + Project 1 metadata  
**Output**: Base skills taxonomy, skill-to-base mappings  
**Status**: Early Development

**Key Features**:
- Hierarchical taxonomy structure
- Science of Reading framework alignment
- MECE (Mutually Exclusive, Collectively Exhaustive) validation
- Framework comparison and coverage analysis

## Shared Infrastructure

### Data Access Layer
**Location**: `shared/data_access/`  
**Purpose**: Unified Snowflake access with local CSV fallback  
**Key Class**: `SkillDataLoader`

**Features**:
- Connection pooling and caching
- Transparent fallback to local CSV files
- Consistent query interface for all projects

### LLM Infrastructure
**Location**: `shared/llm/`  
**Purpose**: AWS Bedrock integration for all projects  
**Key Class**: `BedrockLanguageModels`

**Features**:
- Multi-model support (Claude 3.5, Claude 3, Titan)
- Cost tracking and token counting
- Prompts-as-code pattern
- Reusable across all three projects

### Data Models
**Location**: `shared/models/`  
**Purpose**: Common data structures  
**Key Classes**: `Skill`, `Metadata`, `Taxonomy`

**Features**:
- Type-safe data models (dataclasses)
- Pandas integration
- Serialization/deserialization

### Utilities
**Location**: `shared/utils/`  
**Purpose**: Common utilities  
**Modules**: `logging_config`, `validation`, `export`

## Technology Stack

### Core
- **Python 3.9+**: Primary language
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

### NLP & ML
- **spaCy 3.x** (en_core_web_lg): NLP extraction
- **sentence-transformers**: Embeddings
- **scikit-learn**: Clustering, similarity
- **NetworkX**: Graph analysis

### Cloud & Data
- **AWS Bedrock** (Claude 3.5): LLM assistance
- **Snowflake**: Data warehouse (optional)
- **boto3**: AWS SDK

### Development
- **pytest**: Testing
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **Jupyter**: Notebooks

## Design Decisions

### Why Monorepo?
✅ Projects share same data source (Snowflake)  
✅ Sequential pipeline dependencies  
✅ Atomic commits across projects  
✅ Easier dependency management  
✅ Better for hackathon → production transition

### Why Numbered Prefixes (01-, 02-, 03-)?
✅ Clear ordering and dependencies  
✅ Immediately visible which project is which  
✅ Alphabetical sorting maintains pipeline order  
✅ Easy to add Project 4, 5, etc.

### Why Shared Infrastructure?
✅ DRY principle (Don't Repeat Yourself)  
✅ Consistent LLM interface across projects  
✅ Unified data access and caching  
✅ Easier to maintain and test

### Why Hybrid spaCy + LLM?
✅ Cost optimization (spaCy is free)  
✅ Speed (spaCy is 10-20x faster)  
✅ Accuracy (LLM for ambiguous cases)  
✅ Scalability (can process 8,000+ skills)

## Data Flow

```
┌─────────────────┐
│  Snowflake      │  8,354 skills from ROCK_DB
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Shared Cache   │  Local CSV caching (data/cache/)
└────────┬────────┘
         │
         ├──→ [Project 1] → skill_metadata_enhanced.csv (23 fields)
         │         │
         │         ├──→ [Project 2] → master_concepts.csv (~2,500)
         │         │         │
         │         │         └──→ [Project 3] → base_skills_taxonomy.csv
         │         │
         │         └──→ [Project 2] (enriches similarity)
         │
         └──→ [Project 2] (standalone, can run without Project 1)
                   │
                   └──→ [Project 3]
```

### Data Contracts

**Project 1 → Project 2**:
- Optional enrichment (Project 2 can run standalone)
- Format: CSV with SKILL_ID + 23 metadata fields
- Improves similarity matching accuracy

**Project 2 → Project 3**:
- Required input (Project 3 depends on master concepts)
- Format: CSV with MASTER_CONCEPT_ID + taxonomy mappings
- Reduces skill count before taxonomy building

## Deployment Architecture

### Development
- Local Python environment
- Local CSV data (cached from Snowflake)
- AWS Bedrock via boto3 credentials

### Production (Future)
- Containerized applications (Docker)
- Scheduled batch processing (Airflow/cron)
- Cloud storage for outputs (S3)
- Monitoring and alerting

## Security & Access

### Data Access
- Snowflake credentials via environment variables
- AWS credentials via boto3 configuration
- No credentials in code or config files

### API Keys
- AWS Bedrock: IAM role or access keys
- Stored in environment or AWS credentials file

## Performance Metrics

| Project | Processing Time | Cost | Scalability |
|---------|----------------|------|-------------|
| Project 1 | 4-8 hours | <$50 | 8,000+ skills |
| Project 2 | 2-4 hours | Free | 8,000+ skills |
| Project 3 | 1-2 hours | <$20 | 2,500 concepts |

## Future Enhancements

### Short-Term
- Real-time extraction API (Project 1)
- Interactive validation UI (Project 2)
- Multi-taxonomy support (Project 3)
- CI/CD pipeline integration

### Long-Term
- Project 4: Learning Progressions
- Project 5: Content Alignment Engine
- Project 6: Adaptive Assessment Builder
- Unified API layer for all projects

## Links

- [Platform README](./README.md)
- [Data Flow Diagram](./DATA_FLOW.md)
- [Development Setup](./DEVELOPMENT_SETUP.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

---

**Questions?** Contact ROCK Skills Analysis Team

