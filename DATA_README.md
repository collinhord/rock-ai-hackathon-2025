# Data Acquisition Guide

This document explains how to obtain the required source data to run the ROCK Skills Taxonomy system.

## Required Data Files

The system requires ROCK production schema data files that are excluded from version control due to their size and proprietary nature.

### Location

Data files should be placed in:
```
rock-skills/rock_data/
```

### Required Files

The following CSV files from the ROCK production database are needed:

1. **SKILLS.csv** (~8,355 rows)
   - Contains all ROCK skills with names, descriptions, IDs
   - Primary source for skill extraction

2. **STANDARD_SKILLS.csv** (~2M+ rows)
   - Maps skills to standards
   - Required for cross-state alignment analysis

3. **STANDARDS.csv**
   - Contains state standards information
   - Required for standards analysis

4. **SKILL_AREAS.csv**
   - Content area classifications (ELA, Math, etc.)
   - Required for content area filtering

5. **STANDARD_SETS.csv**
   - Standard set metadata (states, grades)
   - Required for state-specific analysis

6. **STANDARD_SET_DOMAINS.csv**
   - Domain classifications within standard sets
   - Required for domain-level analysis

7. **STANDARD_SET_DOMAIN_GROUPS.csv**
   - Domain group hierarchies
   - Required for hierarchical analysis

## How to Obtain Data

### For Renaissance Employees

1. **Database Access Required**: Contact your team lead or data engineering team for access to the ROCK production database

2. **Export Queries**: Use the following SQL pattern to export data:
   ```sql
   SELECT * FROM SKILLS 
   ORDER BY SKILL_ID;
   ```

3. **Export Format**: Export as CSV with headers, UTF-8 encoding

4. **File Placement**: Place files in `rock-skills/rock_data/`

### For External Collaborators

Contact the project maintainer for:
- Sample dataset (anonymized subset for testing)
- Synthetic data (generated test data)
- Data access agreement (if appropriate)

## Data Verification

After obtaining the files, verify data integrity:

```bash
cd rock-skills
python3 scripts/verify_data_integrity.py
```

Expected output:
```
✓ SKILLS.csv: 8,355 skills loaded
✓ STANDARD_SKILLS.csv: 2,431,234 mappings loaded
✓ STANDARDS.csv: 145,678 standards loaded
✓ All required columns present
✓ No critical data quality issues
```

## Data Security

⚠️ **Important**: ROCK data contains proprietary curriculum information

- **Never commit** CSV files to version control (.gitignore already excludes them)
- **Never share** production data outside Renaissance
- **Use secure channels** for data transfer
- **Delete** when no longer needed

## Sample Data for Testing

A small sample dataset (333 skills) is available for testing:

```
rock-skills/rock_data/skill_list_filtered_data_set.csv
```

This subset can be used to:
- Test pipelines without full data access
- Run demos and POCs
- Develop and debug features

## Alternative: Use Existing Outputs

If you only need to explore the UI and don't need to regenerate the taxonomy:

1. Existing analysis outputs are in: `rock-skills/analysis/outputs/`
2. Launch the UI: `cd rock-skills/poc && streamlit run skill_bridge_app.py`
3. Explore without needing source data

## Troubleshooting

### File Not Found Errors

If you see: `FileNotFoundError: rock_schemas/SKILLS.csv not found`

**Solution**: The file should be in `rock-skills/rock_data/SKILLS.csv` (note: `rock_data` not `rock_schemas`)

Some older scripts may reference `rock_schemas/` - update them to use `rock_data/`

### Column Missing Errors

If you see: `KeyError: 'SKILL_NAME' not found`

**Solution**: Verify CSV export includes headers and all required columns

### Encoding Issues

If you see garbled text or special characters:

**Solution**: Ensure CSV is UTF-8 encoded, re-export if needed

## Contact

For data access questions:
- **Internal**: Contact ROCK Skills Analysis Team
- **External**: Open an issue in the repository

---

**Note**: This system is designed to work with the specific ROCK database schema. If you're adapting this for other educational taxonomies, you'll need to modify the data loading logic in `rock-skills/poc/data_loader.py`.

