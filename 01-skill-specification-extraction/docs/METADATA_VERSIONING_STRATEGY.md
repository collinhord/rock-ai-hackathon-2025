# Metadata Versioning and Change Management Strategy

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Status**: Phase 4.4 - Versioning System Design

## Overview

This document defines the versioning strategy for ROCK Skills metadata, including schema versioning, extraction versioning, change management, and migration procedures.

---

## Version Types

### 1. Schema Version

**Format**: `MAJOR.MINOR.PATCH`

**Example**: `2.1.3`

**Version Components**:
- **MAJOR**: Breaking changes to field structure, data types, or semantics
  - Example: Renaming fields, removing fields, changing enums
  - Requires migration scripts
  - May break existing integrations

- **MINOR**: Backward-compatible additions
  - Example: Adding new fields, extending enum values
  - Optional migration
  - No breaking changes

- **PATCH**: Bug fixes, clarifications, documentation updates
  - Example: Fixing extraction logic, updating field descriptions
  - No schema changes
  - No migration needed

**Current Version**: `1.0.0`  
**Target Version**: `2.0.0` (after cross-domain analysis complete)

---

### 2. Extraction Version

**Format**: `YYYYMMDD-HHmm` (timestamp)

**Example**: `20251017-1430`

**Purpose**:
- Track when metadata was extracted
- Enable temporal queries ("show me skills extracted after date X")
- Identify stale metadata needing refresh

**Stored In**: `extraction_timestamp` field per skill

---

### 3. Model Version

**Format**: Model identifier string

**Example**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

**Purpose**:
- Track which LLM model version extracted metadata
- Enable A/B comparisons between models
- Support model upgrades without full re-extraction

**Stored In**: `extraction_method` field (includes model info)

---

### 4. Prompt Version

**Format**: `vMAJOR.MINOR`

**Example**: `v1.2`

**Purpose**:
- Track prompt engineering iterations
- Correlate quality metrics with prompt versions
- Enable rollback to previous prompts

**Management**:
- Store prompts in version control with tags
- Document prompt changes in commit messages
- Link prompt version to extraction batches

---

## Schema Version History

### Version 1.0.0 (Current - October 2025)

**Description**: Baseline schema optimized for ELA skills

**Fields**: 23 total
- 4 Core Identifiers
- 8 Structural Components (spaCy)
- 7 Educational Metadata (LLM)
- 2 Specifications (Rules)
- 4 Quality Metrics (Auto)

**Known Limitations**:
- `text_type`, `text_mode`, `text_genre` poorly suited for Math
- `skill_domain` lacks Math-specific values
- `scope` values are ELA-centric
- No Math representation or operation type fields

**Extraction Coverage**:
- ELA: 3,000 skills (estimated 90%+ quality)
- Math: 5,224 skills (estimated 60% text_* fields not_applicable)

---

### Version 2.0.0 (Planned - Q4 2025)

**Description**: Unified cross-domain schema for ELA and Math

**Breaking Changes**:
1. **Field Renames**:
   - `text_type` → `content_type`
   - `text_mode` → `content_mode`
   
2. **Extended Enum Values**:
   - `skill_domain`: Add number_operations, algebraic_thinking, geometry, data_analysis, measurement
   - `scope`: Add number, expression, equation, problem, proof, multi_step
   - `content_type`: Add symbolic, visual, concrete, verbal

3. **New Fields** (optional):
   - `mathematical_domain` (conditional for Math)
   - `representation_type` (symbolic, visual, concrete, verbal)
   - `operation_type` (computation, construction, interpretation, modeling, proof)

**Migration Required**: Yes  
**Migration Script**: `migrate_v1_to_v2.py`  
**Estimated Re-Extraction**: 20-30% of skills (mostly Math)

---

## Metadata Lifecycle

### State 1: Extracted

**Description**: Metadata freshly extracted from source skill description

**Attributes**:
- `extraction_timestamp`: Current timestamp
- `extraction_method`: hybrid_spacy_llm
- `llm_confidence`: high/medium/low
- `validation_status`: pending (if tracked)

**Actions**:
- Run automated quality checks
- Flag low-confidence extractions
- Store in staging database

---

### State 2: Validated

**Description**: Metadata reviewed and approved by domain expert

**Attributes**:
- `validation_status`: validated
- `validated_by`: Expert ID
- `validated_at`: Timestamp
- `validation_notes`: Any corrections or comments

**Actions**:
- Promote to production database
- Enable for user-facing features
- Update quality metrics

---

### State 3: Published

**Description**: Metadata live in production, accessible via API

**Attributes**:
- `published_status`: published
- `published_at`: Timestamp
- `schema_version`: Version when published

**Actions**:
- Serve via REST API
- Enable semantic search
- Track usage metrics

---

### State 4: Deprecated

**Description**: Metadata superseded by new extraction or skill update

**Attributes**:
- `deprecated_status`: deprecated
- `deprecated_at`: Timestamp
- `replaced_by`: New skill ID or extraction version

**Actions**:
- Mark in database (soft delete)
- Redirect API requests to new version
- Archive after retention period

---

## Change Management

### Backward-Compatible Changes (Minor Versions)

**Examples**:
- Adding new optional fields
- Extending enum values (adding, not removing)
- Adding new extraction methods
- Documentation updates

**Process**:
1. Update schema documentation
2. Update extraction code to populate new fields
3. Deploy extraction updates
4. Existing data remains valid (new fields null/empty)
5. Gradually backfill new fields via incremental re-extraction

**Migration**: Optional, no breaking changes

---

### Breaking Changes (Major Versions)

**Examples**:
- Renaming fields
- Removing fields
- Changing enum values (removing, renaming)
- Changing data types

**Process**:
1. **Proposal Phase** (2 weeks):
   - Document breaking changes
   - Gather stakeholder feedback
   - Create migration plan
   
2. **Development Phase** (2-4 weeks):
   - Update schema definition
   - Write migration scripts
   - Update extraction code
   - Test on sample dataset
   
3. **Migration Phase** (1 week):
   - Run migration on full dataset
   - Validate migrated data
   - Run quality checks
   
4. **Deployment Phase** (1 week):
   - Deploy updated API
   - Update documentation
   - Notify integrators
   - Monitor for issues

**Migration**: Required for all existing data

---

## Migration Scripts

### Script Template: v1.0 to v2.0

```python
#!/usr/bin/env python3
"""
Migrate metadata from schema v1.0 to v2.0

Changes:
1. Rename text_type → content_type
2. Rename text_mode → content_mode
3. Map skill_domain values for Math skills
4. Extend scope values for Math skills
"""

import pandas as pd
from datetime import datetime

def migrate_v1_to_v2(input_file, output_file):
    """Migrate metadata from v1.0 to v2.0 schema."""
    
    print("Loading v1.0 metadata...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} skills")
    
    # 1. Rename fields
    print("Renaming fields...")
    df = df.rename(columns={
        'text_type': 'content_type',
        'text_mode': 'content_mode'
    })
    
    # 2. Map skill_domain for Math skills
    print("Mapping skill_domain for Math...")
    math_skills = df['CONTENT_AREA'] == 'Mathematics'
    
    # Extract from SKILL_AREA_NAME
    skill_area_mapping = {
        'Algebraic Thinking': 'algebraic_thinking',
        'Whole Numbers': 'number_operations',
        'Fraction': 'number_operations',
        'Decimal': 'number_operations',
        'Geometry': 'geometry',
        'Measurement': 'measurement',
        'Data': 'data_analysis',
        'Probability': 'data_analysis',
    }
    
    def map_math_domain(row):
        if row['CONTENT_AREA'] != 'Mathematics':
            return row['skill_domain']
        
        # Try to map from SKILL_AREA_NAME
        for keyword, domain in skill_area_mapping.items():
            if keyword in row['SKILL_AREA_NAME']:
                return domain
        
        # Default to not_applicable if can't map
        return 'not_applicable'
    
    df['skill_domain'] = df.apply(map_math_domain, axis=1)
    
    # 3. Extend scope for Math skills
    print("Extending scope for Math...")
    def map_math_scope(row):
        if row['CONTENT_AREA'] != 'Mathematics':
            return row['scope']
        
        # Analyze SKILL_NAME for scope indicators
        skill = row['SKILL_NAME'].lower()
        
        if any(word in skill for word in ['equation', 'solve']):
            return 'equation'
        elif any(word in skill for word in ['expression', 'simplify', 'evaluate']):
            return 'expression'
        elif any(word in skill for word in ['multi-step', 'multiple', 'several']):
            return 'multi_step'
        elif any(word in skill for word in ['prove', 'justify', 'demonstrate']):
            return 'proof'
        elif any(word in skill for word in ['problem', 'situation']):
            return 'problem'
        elif any(word in skill for word in ['digit', 'place value', 'number']):
            return 'number'
        else:
            return 'not_applicable'
    
    df['scope'] = df.apply(map_math_scope, axis=1)
    
    # 4. Add schema version
    df['schema_version'] = '2.0.0'
    df['migration_timestamp'] = datetime.now().isoformat()
    
    # 5. Save migrated data
    print(f"Saving v2.0 metadata to {output_file}...")
    df.to_csv(output_file, index=False)
    
    # 6. Validation report
    print("\n=== Migration Summary ===")
    print(f"Total skills migrated: {len(df)}")
    print(f"ELA skills: {(df['CONTENT_AREA'] == 'English Language Arts').sum()}")
    print(f"Math skills: {(df['CONTENT_AREA'] == 'Mathematics').sum()}")
    print(f"\nMath skill_domain distribution:")
    math_df = df[df['CONTENT_AREA'] == 'Mathematics']
    print(math_df['skill_domain'].value_counts())
    print(f"\nMath scope distribution:")
    print(math_df['scope'].value_counts())
    
    # Flag skills needing re-extraction
    needs_reextract = df[
        (df['CONTENT_AREA'] == 'Mathematics') &
        (df['skill_domain'] == 'not_applicable')
    ]
    print(f"\nSkills needing re-extraction: {len(needs_reextract)}")
    
    if len(needs_reextract) > 0:
        needs_reextract.to_csv(
            output_file.replace('.csv', '_needs_reextraction.csv'),
            index=False
        )
    
    print("\n✓ Migration complete!")
    return df

if __name__ == '__main__':
    migrate_v1_to_v2(
        'outputs/production_extraction/combined/all_skills_metadata_v1.csv',
        'outputs/production_extraction/combined/all_skills_metadata_v2.csv'
    )
```

---

## Re-Extraction Strategy

### Full Re-Extraction

**When**: Major schema version changes, model upgrades

**Process**:
1. Update extraction code for new schema
2. Run full extraction on all skills
3. Validate sample for quality
4. Run migration on historical data (if needed)
5. Compare new vs old extractions
6. Replace production metadata

**Estimated Time**: 5-6 hours for 8,354 skills  
**Estimated Cost**: $24-30

---

### Incremental Re-Extraction

**When**: Minor schema updates, prompt improvements, quality issues

**Process**:
1. Identify skills needing re-extraction:
   - Low confidence skills
   - Skills with specific field issues
   - Skills in affected skill areas
2. Extract metadata only for identified skills
3. Merge with existing metadata
4. Validate sample
5. Update production database

**Selection Criteria**:
```python
# Skills needing re-extraction
needs_reextract = df[
    (df['llm_confidence'] == 'low') |
    (df['skill_domain'] == 'not_applicable') & (df['CONTENT_AREA'] == 'Mathematics') |
    (df['extraction_timestamp'] < cutoff_date)
]
```

---

### Targeted Re-Extraction

**When**: Specific field improvements, bug fixes

**Process**:
1. Identify affected skills (by skill area, grade level, etc.)
2. Re-extract only specific fields using updated logic
3. Merge updated fields with existing metadata
4. Validate changes
5. Update production database

**Example**: Re-extract `skill_domain` for Math skills only

---

## Database Schema for Versioning

```sql
-- Skills metadata table with versioning
CREATE TABLE skills_metadata (
    skill_id UUID,
    metadata_version INTEGER,
    schema_version VARCHAR(10),
    
    -- All metadata fields...
    skill_name TEXT,
    actions TEXT,
    -- ... (23 fields)
    
    -- Versioning fields
    extraction_timestamp TIMESTAMP,
    extraction_method VARCHAR(50),
    llm_model_version VARCHAR(100),
    prompt_version VARCHAR(10),
    
    -- Lifecycle fields
    validation_status VARCHAR(20),
    validated_by VARCHAR(100),
    validated_at TIMESTAMP,
    published_status VARCHAR(20),
    published_at TIMESTAMP,
    deprecated_at TIMESTAMP,
    replaced_by_version INTEGER,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (skill_id, metadata_version)
);

-- Index for getting latest version
CREATE INDEX idx_latest_version ON skills_metadata(skill_id, metadata_version DESC);

-- View for latest metadata only
CREATE VIEW skills_metadata_latest AS
SELECT DISTINCT ON (skill_id) *
FROM skills_metadata
ORDER BY skill_id, metadata_version DESC;
```

---

## API Versioning

### URL Versioning

```
GET /api/v1/skills/{skill_id}/metadata
GET /api/v2/skills/{skill_id}/metadata
```

**v1 API**: Returns schema v1.0 format (with field mappings if using v2.0 data)  
**v2 API**: Returns schema v2.0 format

---

### Header Versioning

```
GET /api/skills/{skill_id}/metadata
Accept: application/json; version=1
```

---

### Response Format

```json
{
  "skill_id": "uuid",
  "metadata": {
    // All metadata fields
  },
  "version_info": {
    "schema_version": "2.0.0",
    "extraction_timestamp": "2025-10-17T14:30:00Z",
    "llm_model": "claude-sonnet-4-5",
    "prompt_version": "v1.2"
  }
}
```

---

## Quality Assurance During Migration

### Pre-Migration Checks

```python
def validate_pre_migration(df):
    """Validate data before migration."""
    issues = []
    
    # Check for required fields
    required = ['SKILL_ID', 'SKILL_NAME', 'cognitive_demand']
    for field in required:
        if df[field].isna().any():
            issues.append(f"Missing values in {field}")
    
    # Check for duplicate skill IDs
    if df['SKILL_ID'].duplicated().any():
        issues.append("Duplicate SKILL_IDs found")
    
    # Check extraction completeness
    if (df['actions'] == '').mean() > 0.1:
        issues.append(f"High rate of missing actions: {(df['actions'] == '').mean():.1%}")
    
    return issues
```

### Post-Migration Validation

```python
def validate_post_migration(old_df, new_df):
    """Validate data after migration."""
    issues = []
    
    # Check row count unchanged
    if len(old_df) != len(new_df):
        issues.append(f"Row count mismatch: {len(old_df)} → {len(new_df)}")
    
    # Check all skill IDs present
    missing_ids = set(old_df['SKILL_ID']) - set(new_df['SKILL_ID'])
    if missing_ids:
        issues.append(f"Missing {len(missing_ids)} skill IDs after migration")
    
    # Check renamed fields
    if 'content_type' not in new_df.columns:
        issues.append("Field 'content_type' not found (should be renamed from 'text_type')")
    
    # Check data integrity
    if new_df['SKILL_NAME'].isna().any():
        issues.append("SKILL_NAME contains null values after migration")
    
    return issues
```

---

## Rollback Procedures

### Scenario: Migration Issues Discovered

1. **Immediate**: Switch API to serve v1.0 schema (from backup database)
2. **Investigate**: Analyze migration issues, identify root cause
3. **Fix**: Correct migration script, test on sample
4. **Re-migrate**: Run corrected migration on full dataset
5. **Validate**: Run quality checks
6. **Deploy**: Switch API back to migrated data

### Scenario: Quality Degradation After Re-Extraction

1. **Immediate**: Revert to previous extraction version in database
2. **Investigate**: Compare old vs new extractions, identify quality issues
3. **Fix**: Adjust prompts or extraction logic
4. **Re-extract**: Run corrected extraction on sample
5. **Validate**: Confirm quality improvements
6. **Deploy**: Run full re-extraction

---

## Version Control Integration

### Git Tags for Schema Versions

```bash
# Tag schema version
git tag -a schema-v1.0.0 -m "Baseline schema for ELA skills"
git push origin schema-v1.0.0

# Tag when deploying new schema
git tag -a schema-v2.0.0 -m "Unified cross-domain schema"
git push origin schema-v2.0.0
```

### Extraction Batch Tracking

```bash
# Tag major extraction batches
git tag -a extraction-20251017-ela -m "Full ELA extraction (3,000 skills)"
git tag -a extraction-20251017-math -m "Full Math extraction (5,224 skills)"
```

---

## Communication Plan

### For Major Version Changes

**Timeline**: 4 weeks before deployment

**Stakeholders**:
- Product team (API consumers)
- Data engineering team
- Frontend developers
- QA team

**Communications**:
1. **Week -4**: Announcement email with breaking changes
2. **Week -3**: Technical specification doc shared
3. **Week -2**: Migration scripts available for testing
4. **Week -1**: Final reminder, deprecation notices
5. **Week 0**: Deployment, post-deployment support

### For Minor Version Changes

**Timeline**: 1 week before deployment

**Communication**: Email announcement with changelog

---

## Changelog Template

### Version 2.0.0 (2025-11-XX)

**Breaking Changes**:
- Renamed `text_type` to `content_type`
- Renamed `text_mode` to `content_mode`
- Extended `skill_domain` enum with Math-specific values

**New Features**:
- Added Math-specific scope values
- Added `representation_type` field (optional)
- Added `mathematical_domain` field (optional)

**Improvements**:
- Improved Math skill extraction accuracy
- Enhanced cross-domain prompt engineering
- Updated vocabulary dictionaries

**Migration**:
- Migration script: `migrate_v1_to_v2.py`
- Estimated migration time: 10 minutes
- Re-extraction recommended for Math skills with `skill_domain = not_applicable`

**API Changes**:
- v2 API endpoint available: `/api/v2/skills/{id}/metadata`
- v1 API deprecated, sunset date: 2026-02-01

---

## Sunset Policy

**Minor Versions**: Supported for 6 months after next minor release

**Major Versions**: Supported for 12 months after next major release

**API Endpoints**: 
- Deprecated versions remain functional for sunset period
- Warning headers included in responses
- Sunset date communicated in API documentation

**Example**:
- v1.0 released: 2025-10-01
- v2.0 released: 2025-12-01
- v1.0 sunset date: 2026-12-01 (12 months)

---

## Metadata Refresh Strategy

### Trigger Conditions

1. **Schema Update**: New schema version released
2. **Model Upgrade**: New LLM model available
3. **Quality Issue**: Systematic extraction errors identified
4. **Skill Update**: Source skill descriptions changed
5. **Age**: Metadata >12 months old

### Refresh Frequency

**Full Refresh**: Annually (all 8,354 skills)
- Expected cost: $24-30
- Expected time: 5-6 hours
- Scheduled maintenance window

**Incremental Refresh**: Quarterly (flagged skills only)
- Low confidence skills
- Updated skill descriptions
- New skills added to corpus

**Targeted Refresh**: As needed (specific issues)
- Bug fixes
- Prompt improvements
- Quality issues in specific skill areas

---

## Monitoring and Alerting

### Version Distribution

Track in monitoring dashboard:
- % of skills on latest schema version
- % of skills extracted in last 30/90/365 days
- % of skills with deprecated extraction methods

### Quality Metrics by Version

Compare across schema versions:
- High confidence rate
- Field population rates
- User satisfaction scores
- API query success rates

### Alerts

- **Warning**: >10% of skills on deprecated schema version
- **Critical**: >20% of skills with extractions >12 months old
- **Info**: New schema version available for deployment

---

## Document Version

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Next Review**: After schema v2.0 deployment  
**Maintained By**: ROCK Skills Analysis Team

