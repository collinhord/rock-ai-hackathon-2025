# Taxonomy Builder

A comprehensive toolkit for validating, analyzing, and improving educational taxonomies using LLM-assisted analysis.

## Overview

The Taxonomy Builder provides tools to:

- **Validate** taxonomy structure for consistency, duplicates, and logical relationships
- **Compare** your taxonomy against external academic frameworks
- **Suggest** improvements using LLM analysis
- **Generate** comprehensive reports on taxonomy quality

## Features

### ✅ Validation

- Hierarchy integrity checking
- Duplicate detection (exact and fuzzy)
- Naming consistency analysis
- Coverage gap identification
- Parent-child relationship validation

### 📊 Framework Comparison

- Parse PDF, DOCX, and TXT framework documents
- Extract taxonomy structures using LLM
- Compare against your taxonomy
- Identify gaps and alignment opportunities
- Generate actionable recommendations

### 🤖 LLM-Assisted Analysis

- Structural validation and suggestions
- Naming consistency improvements
- Conceptual hierarchy validation
- Framework extraction and comparison
- Uses AWS Bedrock (Claude) or OpenAI

### 🗄️ Multiple Data Formats

- **CSV**: Original format (backward compatible)
- **JSON**: UUID mapping for stable identifiers
- **SQLite**: High-performance relational database
- **Compatibility layer**: Ensures existing scripts continue working

## Installation

```bash
cd /path/to/rock-skills/taxonomy_builder
pip install -r requirements.txt
```

### Requirements

- Python 3.9+
- pandas, numpy
- boto3 (for AWS Bedrock) or openai (for OpenAI)
- PyPDF2, python-docx (for document parsing)
- fuzzywuzzy (for similarity matching)

## Quick Start

### Validate Taxonomy

```bash
python cli.py validate --output validation_report.md
```

### Compare with Framework

First, add your framework documents to the `frameworks/` directory (organized by subject):

```bash
# Add frameworks to appropriate directory
cp ~/Downloads/scarborough_rope.pdf ../frameworks/input/ela/
cp ~/Downloads/nctm_standards.pdf ../frameworks/input/math/
```

Then analyze:

```bash
# Compare a single framework
python cli.py compare ../frameworks/input/ela/scarborough_rope.pdf \
    --output ../frameworks/output/scarborough_analysis.md

# Batch process all ELA frameworks
for file in ../frameworks/input/ela/*.pdf; do
    basename=$(basename "$file" .pdf)
    python cli.py compare "$file" --output "../frameworks/output/${basename}_analysis.md"
done
```

**See `../frameworks/README.md` for complete framework organization guide.**

### Get Suggestions

```bash
# Naming consistency suggestions
python cli.py suggest --aspect naming --output naming_suggestions.json

# Structural suggestions
python cli.py suggest --aspect structure --output structure_suggestions.json
```

### Generate Comprehensive Report

```bash
python cli.py report --output full_report.md
```

## Architecture

### Data Flow

```
CSV (source of truth)
  ↓
UUID Mapping (JSON)
  ↓
SQLite Database (for performance)
  ↓
Compatibility Layer (unified access)
  ↓
Validation & Analysis Tools
```

### Key Components

#### 1. Compatibility Layer (`compatibility.py`)

Provides unified access to taxonomy data in multiple formats:

```python
from taxonomy_builder import TaxonomyAccess

with TaxonomyAccess() as tax:
    # Access as DataFrame (backward compatible)
    df = tax.get_taxonomy_df()
    
    # Use UUIDs
    uuid = tax.path_to_uuid("Strand > Pillar > Domain")
    path = tax.uuid_to_path(uuid)
    
    # Query database (high performance)
    children = tax.get_children(uuid)
    descendants = tax.get_descendants(uuid)
    strands = tax.get_nodes_by_level('Strand')
```

#### 2. Validator (`validator.py`)

Comprehensive taxonomy validation:

```python
from taxonomy_builder import TaxonomyAccess, TaxonomyValidator

with TaxonomyAccess() as tax:
    validator = TaxonomyValidator(tax)
    report = validator.validate()
    
    print(f"Total issues: {report.total_issues}")
    
    # Save reports
    with open('report.md', 'w') as f:
        f.write(report.to_markdown())
```

#### 3. LLM Interface (`llm_interface.py`)

LLM interactions for analysis:

```python
from taxonomy_builder import LLMInterface

# Use AWS Bedrock (Claude)
llm = LLMInterface(provider='bedrock')

# Or use OpenAI
llm = LLMInterface(provider='openai', model='gpt-4-turbo-preview')

# Get suggestions
suggestions = llm.validate_structure(taxonomy_summary)
naming_improvements = llm.suggest_naming_improvements(names_by_level)
```

#### 4. Framework Analyzer (`framework_analyzer.py`)

Parse and compare frameworks:

```python
from taxonomy_builder import TaxonomyAccess, LLMInterface, FrameworkAnalyzer

with TaxonomyAccess() as tax:
    llm = LLMInterface(provider='bedrock')
    analyzer = FrameworkAnalyzer(tax, llm)
    
    # Analyze single framework
    result = analyzer.analyze_framework('framework.pdf')
    
    # Batch analyze multiple frameworks
    results = analyzer.batch_analyze(['fw1.pdf', 'fw2.pdf'])
    
    # Generate report
    report = analyzer.generate_report(results, 'report.md')
```

## Database Schema

The SQLite database provides high-performance querying:

### Tables

**taxonomy_nodes**
- uuid (PRIMARY KEY)
- level (Strand, Pillar, Domain, etc.)
- name
- parent_uuid
- full_path
- path_hash

**taxonomy_hierarchy** (closure table)
- ancestor_uuid
- descendant_uuid
- depth

**taxonomy_metadata**
- uuid
- annotation
- examples

### Example Queries

```sql
-- Get all strands
SELECT * FROM taxonomy_nodes WHERE level='Strand';

-- Get children of a node
SELECT * FROM taxonomy_nodes WHERE parent_uuid='<uuid>';

-- Get all descendants
SELECT n.* FROM taxonomy_nodes n
JOIN taxonomy_hierarchy h ON n.uuid = h.descendant_uuid
WHERE h.ancestor_uuid = '<uuid>';
```

## Backward Compatibility

**IMPORTANT**: The original CSV format is preserved as the source of truth. Existing scripts that load the CSV directly will continue to work without modification:

```python
# Old code (still works)
import pandas as pd
df = pd.read_csv('POC_science_of_reading_literacy_skills_taxonomy.csv')

# New code (recommended for new features)
from taxonomy_builder import TaxonomyAccess
with TaxonomyAccess() as tax:
    df = tax.get_taxonomy_df()  # Same result
```

The UUID mapping and database are **separate files** that don't modify the CSV:

- `POC_science_of_reading_literacy_skills_taxonomy.csv` - Original (unchanged)
- `taxonomy_uuid_map.json` - UUID mappings (new)
- `taxonomy.db` - SQLite database (new)

## Validation Criteria

### Hierarchy Integrity

- No orphaned nodes (parent_uuid references valid node)
- Correct level ordering (Strand → Pillar → Domain → ...)
- No cycles in hierarchy

### Naming Consistency

- Consistent capitalization within levels
- No extra whitespace
- No double spaces
- Consistent use of "and" vs "&"

### Duplicate Detection

- Exact duplicates (same name at same level)
- Near-duplicates (85%+ similarity)
- Flags for manual review

### Coverage Analysis

- Nodes with only one child (may indicate incomplete structure)
- Excessively deep hierarchies
- Imbalanced branches

## Prompts

LLM prompts are stored in `prompts/` directory:

- `structural_validation.txt` - Taxonomy structure analysis
- `framework_extraction.txt` - Extract taxonomies from documents
- `comparison_analysis.txt` - Compare taxonomies
- `naming_consistency.txt` - Naming improvement suggestions

You can customize these prompts to adjust the analysis behavior.

## Costs

LLM usage costs depend on the provider and model:

**AWS Bedrock (Claude Sonnet 4.5)**
- Input: $0.003 per 1K tokens
- Output: $0.015 per 1K tokens
- Typical validation: ~$0.10-0.50
- Framework comparison: ~$0.50-2.00

**OpenAI (GPT-4 Turbo)**
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens
- Costs ~3x higher than Bedrock

## Examples

### Example 1: Find Duplicates

```python
from taxonomy_builder import TaxonomyAccess, TaxonomyValidator

with TaxonomyAccess() as tax:
    validator = TaxonomyValidator(tax)
    report = validator.validate()
    
    # Filter for duplicate issues
    duplicates = [i for i in report.issues if i.category == 'duplicate']
    
    for dup in duplicates:
        print(f"{dup.severity}: {dup.message}")
```

### Example 2: Search Taxonomy

```python
from taxonomy_builder import TaxonomyAccess

with TaxonomyAccess() as tax:
    # Search for nodes containing "reading"
    results = tax.search_nodes("reading")
    
    for node in results:
        print(f"{node.level}: {node.name}")
        print(f"  Path: {node.full_path}")
```

### Example 3: Analyze Framework

```bash
# Parse PDF framework and compare with taxonomy
python cli.py compare scarborough_rope.pdf --output rope_comparison.md

# The report will include:
# - Extracted taxonomy from PDF
# - Concepts missing from our taxonomy
# - Concepts in our taxonomy not in framework
# - Recommendations for alignment
```

## Troubleshooting

### "boto3 not available"

Install AWS SDK:
```bash
pip install boto3
```

Configure AWS credentials:
```bash
aws configure
# Or set environment variables:
# export AWS_ACCESS_KEY_ID=...
# export AWS_SECRET_ACCESS_KEY=...
# export AWS_DEFAULT_REGION=us-west-2
```

### "PyPDF2 not available"

Install PDF parsing library:
```bash
pip install PyPDF2
```

### Database out of sync with CSV

Regenerate the database:
```bash
cd ../scripts
python3 generate_uuid_map.py
python3 csv_to_db.py
```

## Development

### Running Tests

```python
# Test validator
cd taxonomy_builder
python3 validator.py

# Test compatibility layer
python3 compatibility.py

# Test LLM interface (requires credentials)
python3 llm_interface.py
```

### Adding New Validation Rules

Edit `validator.py` and add your check to the `validate()` method:

```python
def _validate_my_rule(self):
    """My custom validation rule."""
    # Check something
    if issue_found:
        self.issues.append(ValidationIssue(
            severity='warning',
            category='custom',
            message='Description of issue',
            details={'key': 'value'}
        ))
```

## Future Enhancements

- [ ] Semantic similarity-based parent-child validation
- [ ] Automated taxonomy merging tools
- [ ] Visual taxonomy browser/editor
- [ ] Integration with taxonomy versioning system
- [ ] Batch validation for taxonomy change proposals

## License

See main repository LICENSE file.

## Support

For questions or issues, contact the ROCK Skills development team.

