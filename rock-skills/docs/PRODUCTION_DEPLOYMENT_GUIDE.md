# Production Deployment Guide - ROCK Skills Metadata Extraction System

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Target Environment**: Production  
**Estimated Deployment Time**: 6-8 hours

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Full-Scale Extraction](#full-scale-extraction)
5. [Quality Validation](#quality-validation)
6. [Database Integration](#database-integration)
7. [API Deployment](#api-deployment)
8. [Monitoring Setup](#monitoring-setup)
9. [Rollback Procedures](#rollback-procedures)

---

## Overview

This guide walks through deploying the ROCK Skills Metadata Extraction System to production, including full-scale extraction of all 8,354 skills, quality validation, and system integration.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Layer                               │
│  SKILLS.csv (8,354 skills: 3,000 ELA + 5,224 Math)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Enhanced Metadata Extractor                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   spaCy    │  │  AWS       │  │  Rules     │           │
│  │ Structural │→ │  Bedrock   │→ │  Engine    │           │
│  │  Analysis  │  │  (LLM)     │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Output Layer (23 fields)                     │
│  skill_metadata_enhanced.csv + checkpoints                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             Production Database                              │
│  PostgreSQL / MongoDB with metadata schema                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               REST API Layer                                 │
│  Metadata query, search, and filtering endpoints            │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Phases

| Phase | Duration | Description |
|-------|----------|-------------|
| 1. Setup | 1 hour | Install dependencies, configure AWS, validate environment |
| 2. Extraction | 5-6 hours | Full-scale metadata extraction (8,354 skills) |
| 3. Validation | 1 hour | Quality checks, sample validation, error analysis |
| 4. Integration | 2 hours | Database schema, data loading, API setup |
| 5. Monitoring | 30 min | Dashboard configuration, alerting |

**Total**: 6-8 hours (most time is automated extraction)

---

## Prerequisites

### System Requirements

**Hardware**:
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Disk: 5GB free space
- Network: Stable internet connection to AWS

**Software**:
- Python 3.8+
- pip package manager
- AWS CLI configured
- Git (for version control)
- PostgreSQL 12+ or MongoDB 4+ (for production database)

### AWS Requirements

**Services**:
- AWS Bedrock access enabled
- Claude Sonnet 4.5 model access granted
- IAM credentials with Bedrock permissions

**Permissions Required**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-*"
    }
  ]
}
```

**Cost Budget**:
- Full extraction: $24-30
- Add 20% buffer for retries: ~$35 total
- Ongoing costs: ~$0.003 per skill for updates

---

## Environment Setup

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis

# Install Python dependencies
pip install -r ../../requirements.txt

# Additional dependencies for extraction
pip install boto3 spacy pandas numpy

# Download spaCy language model
python -m spacy download en_core_web_sm
```

**Verify Installation**:
```bash
# Test Python imports
python3 -c "import boto3, spacy, pandas, numpy; print('✓ All dependencies installed')"

# Test spaCy model
python3 -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy model loaded')"
```

---

### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI (interactive)
aws configure

# Enter:
# - AWS Access Key ID: [your-key-id]
# - AWS Secret Access Key: [your-secret-key]
# - Default region: us-west-2
# - Default output format: json
```

**Or set environment variables**:
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"
```

**Verify AWS Access**:
```bash
# Test Bedrock access
aws bedrock-runtime list-foundation-models --region us-west-2

# Test Claude Sonnet 4.5 access
aws bedrock-runtime invoke-model \
    --model-id us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --body '{"anthropic_version":"bedrock-2023-05-31","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}' \
    --region us-west-2 \
    /tmp/test-output.txt

# Should return response without errors
cat /tmp/test-output.txt
```

---

### Step 3: Prepare Directory Structure

```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis

# Create output directories
mkdir -p outputs/production_extraction/ela
mkdir -p outputs/production_extraction/math
mkdir -p outputs/production_extraction/combined
mkdir -p outputs/production_extraction/validation
mkdir -p logs

# Verify input data
ls -lh data/input/rock_schemas/SKILLS.csv

# Check skill counts
echo "ELA Skills: $(grep -c 'English Language Arts' data/input/rock_schemas/SKILLS.csv)"
echo "Math Skills: $(grep -c 'Mathematics' data/input/rock_schemas/SKILLS.csv)"
```

---

## Full-Scale Extraction

### Phase 1: Test Run (5 skills each)

**Purpose**: Validate setup before full extraction

```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis/scripts

# Test ELA extraction
python3 enhanced_metadata_extractor.py \
    --input ../../data/input/rock_schemas/SKILLS.csv \
    --content-area "English Language Arts" \
    --output-dir ../outputs/production_extraction/ela_test \
    --limit 5

# Test Math extraction
python3 enhanced_metadata_extractor.py \
    --input ../../data/input/rock_schemas/SKILLS.csv \
    --content-area "Mathematics" \
    --output-dir ../outputs/production_extraction/math_test \
    --limit 5
```

**Verify Test Results**:
```bash
# Check ELA test output
head -3 ../outputs/production_extraction/ela_test/skill_metadata_enhanced_*.csv

# Check Math test output
head -3 ../outputs/production_extraction/math_test/skill_metadata_enhanced_*.csv

# Verify all 23 fields present
head -1 ../outputs/production_extraction/ela_test/skill_metadata_enhanced_*.csv | tr ',' '\n' | wc -l
# Should output: 25 (23 fields + 2 extra)
```

---

### Phase 2: Full ELA Extraction (3,000 skills)

**Expected Duration**: 2-3 hours  
**Expected Cost**: $9-12

```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis/scripts

# Run in background with logging
nohup python3 enhanced_metadata_extractor.py \
    --input ../../data/input/rock_schemas/SKILLS.csv \
    --content-area "English Language Arts" \
    --output-dir ../outputs/production_extraction/ela \
    --checkpoint-interval 100 \
    > ../outputs/production_extraction/ela_extraction.log 2>&1 &

# Save PID for monitoring
echo $! > ../outputs/production_extraction/ela_extraction.pid
```

**Monitor Progress**:
```bash
cd ../outputs/production_extraction

# Run monitoring script
./monitor_extraction.sh

# Or check logs directly
tail -f ela_extraction.log

# Count checkpoints (×100 = approx skills completed)
ls -1 ela/checkpoint_*.csv | wc -l
```

---

### Phase 3: Full Math Extraction (5,224 skills)

**Expected Duration**: 3.5-4 hours  
**Expected Cost**: $15-18

```bash
cd /path/to/rock-ai-hackathon-2025/rock-skills/analysis/scripts

# Run in background with logging
nohup python3 enhanced_metadata_extractor.py \
    --input ../../data/input/rock_schemas/SKILLS.csv \
    --content-area "Mathematics" \
    --output-dir ../outputs/production_extraction/math \
    --checkpoint-interval 100 \
    > ../outputs/production_extraction/math_extraction.log 2>&1 &

# Save PID for monitoring
echo $! > ../outputs/production_extraction/math_extraction.pid
```

**Run Both in Parallel** (recommended):
- Start ELA extraction
- Immediately start Math extraction
- Both run simultaneously
- Total time: ~4-5 hours (limited by Math extraction)

---

### Phase 4: Completion Verification

**Wait for Completion**:
```bash
# Check if processes still running
ps aux | grep enhanced_metadata_extractor | grep -v grep

# When complete, processes will exit
# Monitor until both show "✗ NOT RUNNING"
./monitor_extraction.sh
```

**Verify Output Files**:
```bash
# ELA output
ls -lh ela/skill_metadata_enhanced_*.csv
# Should show final output file

# Math output
ls -lh math/skill_metadata_enhanced_*.csv
# Should show final output file

# Count skills extracted
wc -l ela/skill_metadata_enhanced_*.csv
# Should be ~3001 (including header)

wc -l math/skill_metadata_enhanced_*.csv
# Should be ~5225 (including header)
```

---

### Phase 5: Combine Results

```python
# Create combined dataset
import pandas as pd

# Load both datasets
ela_df = pd.read_csv('outputs/production_extraction/ela/skill_metadata_enhanced_20251017_XXXXXX.csv')
math_df = pd.read_csv('outputs/production_extraction/math/skill_metadata_enhanced_20251017_XXXXXX.csv')

# Add content area identifier
ela_df['CONTENT_AREA'] = 'English Language Arts'
math_df['CONTENT_AREA'] = 'Mathematics'

# Combine
combined_df = pd.concat([ela_df, math_df], ignore_index=True)

# Verify total
print(f"Total skills: {len(combined_df)}")  # Should be 8,224

# Save combined dataset
combined_df.to_csv('outputs/production_extraction/combined/all_skills_metadata.csv', index=False)
print("✓ Combined dataset saved")
```

---

## Quality Validation

### Automated Quality Checks

```python
# Run automated validation
import pandas as pd

df = pd.read_csv('outputs/production_extraction/combined/all_skills_metadata.csv')

# Check 1: Completeness
print("=== Completeness Checks ===")
print(f"Total skills: {len(df)}")
print(f"Skills with SKILL_ID: {df['SKILL_ID'].notna().sum()}")
print(f"Skills with actions: {(df['actions'] != '').sum()}")
print(f"Skills with cognitive_demand: {(df['cognitive_demand'] != '').sum()}")

# Check 2: Confidence Distribution
print("\n=== Confidence Distribution ===")
print(df['llm_confidence'].value_counts())
high_conf_rate = (df['llm_confidence'] == 'high').mean()
print(f"High confidence rate: {high_conf_rate:.1%}")

# Check 3: Field Population Rates
print("\n=== Field Population Rates ===")
fields = ['actions', 'targets', 'cognitive_demand', 'task_complexity', 
          'text_type', 'skill_domain', 'scope']
for field in fields:
    non_empty = (df[field] != '').sum()
    rate = non_empty / len(df)
    print(f"{field}: {rate:.1%}")

# Check 4: Domain-Specific Patterns
print("\n=== Domain Patterns ===")
ela_skills = df[df['CONTENT_AREA'] == 'English Language Arts']
math_skills = df[df['CONTENT_AREA'] == 'Mathematics']

print(f"ELA text_type = 'not_applicable': {(ela_skills['text_type'] == 'not_applicable').mean():.1%}")
print(f"Math text_type = 'not_applicable': {(math_skills['text_type'] == 'not_applicable').mean():.1%}")

# Check 5: Flag Issues
print("\n=== Flagged Issues ===")
low_conf = df[df['llm_confidence'] == 'low']
print(f"Low confidence skills: {len(low_conf)} ({len(low_conf)/len(df):.1%})")

# Save flagged skills for review
low_conf.to_csv('outputs/production_extraction/validation/low_confidence_skills.csv', index=False)
```

### Manual Sample Validation

Follow procedures in `PRODUCTION_QUALITY_STANDARDS.md`:
1. Extract stratified random sample (200 skills)
2. Expert review using validation checklist
3. Calculate accuracy metrics
4. Document findings

---

## Database Integration

### Schema Design

**PostgreSQL Schema**:
```sql
-- Create skills_metadata table
CREATE TABLE skills_metadata (
    skill_id UUID PRIMARY KEY,
    skill_name TEXT NOT NULL,
    skill_area_name VARCHAR(255),
    grade_level_short_name VARCHAR(10),
    content_area VARCHAR(50),
    
    -- Structural metadata
    actions TEXT,
    targets TEXT,
    qualifiers TEXT,
    root_verb VARCHAR(50),
    direct_objects TEXT,
    prepositional_phrases TEXT,
    key_concepts TEXT,
    complexity_markers TEXT,
    
    -- Educational metadata
    text_type VARCHAR(50),
    text_mode VARCHAR(50),
    text_genre VARCHAR(50),
    skill_domain VARCHAR(50),
    task_complexity VARCHAR(50),
    cognitive_demand VARCHAR(50),
    scope VARCHAR(50),
    
    -- Specifications
    support_level VARCHAR(50),
    complexity_band VARCHAR(20),
    
    -- Quality metrics
    llm_confidence VARCHAR(20),
    llm_notes TEXT,
    extraction_method VARCHAR(50),
    extraction_timestamp TIMESTAMP,
    
    -- Indexes for common queries
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_content_area ON skills_metadata(content_area);
CREATE INDEX idx_grade_level ON skills_metadata(grade_level_short_name);
CREATE INDEX idx_skill_domain ON skills_metadata(skill_domain);
CREATE INDEX idx_cognitive_demand ON skills_metadata(cognitive_demand);
CREATE INDEX idx_complexity_band ON skills_metadata(complexity_band);
CREATE INDEX idx_llm_confidence ON skills_metadata(llm_confidence);

-- Full-text search index on skill_name
CREATE INDEX idx_skill_name_fts ON skills_metadata USING gin(to_tsvector('english', skill_name));
```

### Data Loading

```python
# Load metadata into PostgreSQL
import pandas as pd
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://user:password@localhost:5432/rock_skills')

# Load combined metadata
df = pd.read_csv('outputs/production_extraction/combined/all_skills_metadata.csv')

# Clean data
df = df.rename(columns=lambda x: x.lower())  # Lowercase column names
df['extraction_timestamp'] = pd.to_datetime(df['extraction_timestamp'])

# Load to database
df.to_sql('skills_metadata', engine, if_exists='replace', index=False)

print(f"✓ Loaded {len(df)} skills to database")

# Verify
with engine.connect() as conn:
    count = conn.execute("SELECT COUNT(*) FROM skills_metadata").scalar()
    print(f"✓ Database contains {count} skills")
```

---

## API Deployment

### API Endpoints Design

```python
# Flask API example
from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Database connection
conn = psycopg2.connect("dbname=rock_skills user=user password=password")

@app.route('/api/skills/metadata/<skill_id>', methods=['GET'])
def get_skill_metadata(skill_id):
    """Get metadata for a single skill."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skills_metadata WHERE skill_id = %s", (skill_id,))
    result = cursor.fetchone()
    
    if not result:
        return jsonify({'error': 'Skill not found'}), 404
    
    # Convert to dict
    columns = [desc[0] for desc in cursor.description]
    skill_data = dict(zip(columns, result))
    
    return jsonify(skill_data)

@app.route('/api/skills/search', methods=['POST'])
def search_skills():
    """Search skills by metadata."""
    filters = request.json
    
    query = "SELECT * FROM skills_metadata WHERE 1=1"
    params = []
    
    if 'content_area' in filters:
        query += " AND content_area = %s"
        params.append(filters['content_area'])
    
    if 'cognitive_demand' in filters:
        query += " AND cognitive_demand = %s"
        params.append(filters['cognitive_demand'])
    
    if 'complexity_band' in filters:
        query += " AND complexity_band = %s"
        params.append(filters['complexity_band'])
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    # Convert to list of dicts
    columns = [desc[0] for desc in cursor.description]
    skills = [dict(zip(columns, row)) for row in results]
    
    return jsonify({'count': len(skills), 'skills': skills})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## Monitoring Setup

### Dashboard Metrics

Create monitoring dashboard tracking:
- **Extraction Metrics**: Success rate, average time per skill, cost per skill
- **Quality Metrics**: Confidence distribution, field population rates
- **Usage Metrics**: API call volume, query response times
- **Error Metrics**: Failed extractions, API timeouts, database errors

### Alerting

Set up alerts for:
- Low confidence rate <80%
- Extraction failures >5%
- API response time >1 second
- Database connection errors

---

## Rollback Procedures

### Scenario: Extraction Issues Discovered

1. **Stop using new metadata**: Switch API to use previous version
2. **Investigate issues**: Analyze flagged skills, check logs
3. **Fix extraction**: Adjust prompts, re-extract problematic skills
4. **Re-validate**: Run quality checks on corrected data
5. **Deploy fixed version**: Update database, switch API back

### Scenario: Database Corruption

1. **Restore from backup**: Load last good database snapshot
2. **Re-import metadata**: Load from CSV files
3. **Verify integrity**: Run data validation queries
4. **Resume operations**: Switch API to restored database

---

## Post-Deployment Checklist

- [ ] Full extraction completed (8,224 skills)
- [ ] Quality validation passed (≥90% accuracy)
- [ ] Database loaded and indexed
- [ ] API endpoints tested and documented
- [ ] Monitoring dashboard configured
- [ ] Backup procedures established
- [ ] Documentation complete and accessible
- [ ] Team trained on system usage
- [ ] Rollback procedures tested

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Next Review**: After initial production deployment  
**Maintained By**: ROCK Skills Analysis Team

