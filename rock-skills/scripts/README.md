# Scripts Directory

Utility scripts for taxonomy management, data validation, and system maintenance.

## Quick Reference

### Pre-Demo Validation
```bash
# Run before any demo or presentation
./quick_demo_test.sh
```

### Data Integrity Check
```bash
# Verify all critical data files load correctly
python3 verify_data_integrity.py
```

---

## Scripts Overview

### Active Utility Scripts

#### `verify_data_integrity.py`
**Purpose**: Validates that all critical CSV data files load correctly and have expected structure  
**Usage**: `python3 verify_data_integrity.py`  
**When to use**: Before demos, after data updates, troubleshooting data issues  
**Output**: Reports on each data file with row/column counts and validation status

#### `quick_demo_test.sh`
**Purpose**: Comprehensive pre-demo validation checklist  
**Usage**: `./quick_demo_test.sh`  
**When to use**: Before any hackathon demo or stakeholder presentation  
**Checks**:
- Data integrity
- Python dependencies
- Critical files existence
- Application imports
- Taxonomy Builder CLI

### One-Time Setup Scripts

These scripts were run during initial setup and typically don't need to be run again:

#### `cleanup_taxonomy.py`
**Purpose**: Normalizes taxonomy CSV (capitalization, punctuation)  
**Status**: ✅ Already run (October 15, 2025)  
**Backup created**: `POC_science_of_reading_literacy_skills_taxonomy_backup_20251015_142236.csv`  
**Output**: Created cleanup reports (now archived)

**Usage** (if needed):
```bash
python3 cleanup_taxonomy.py [--dry-run]
```

#### `generate_uuid_map.py`
**Purpose**: Generates deterministic UUIDs for all taxonomy nodes  
**Status**: ✅ Already run  
**Output**: `taxonomy_uuid_map.json` (2,070 UUIDs)  
**When to rerun**: If taxonomy structure changes significantly

**Usage**:
```bash
python3 generate_uuid_map.py
```

#### `csv_to_db.py`
**Purpose**: Migrates taxonomy from CSV to SQLite database  
**Status**: ✅ Already run  
**Output**: `taxonomy.db` (3.1 MB with full hierarchy)  
**When to rerun**: After taxonomy updates or if database becomes corrupted

**Usage**:
```bash
python3 csv_to_db.py
```

---

## Archived Files

Historical reports and logs are archived in `archive/` subdirectory:
- `cleanup_report.txt` - Initial cleanup report
- `cleanup_report_final.txt` - Final cleanup summary

---

## Dependencies

### Core (Required)
- Python 3.9+
- pandas
- numpy

### For Taxonomy Scripts
- SQLite3 (built-in to Python)

### For Validation
- All packages in `../poc/requirements.txt`

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
cd ../poc
pip install -r requirements.txt
```

### "File not found" errors in verify_data_integrity.py
Check that you're running from the `rock-skills/` directory:
```bash
cd /path/to/rock-skills
python3 scripts/verify_data_integrity.py
```

### Database needs regeneration
```bash
python3 scripts/csv_to_db.py
```

---

## Adding New Scripts

When adding new utility scripts:
1. Add shebang line: `#!/usr/bin/env python3`
2. Include docstring with purpose and usage
3. Make executable: `chmod +x script_name.py`
4. Update this README with description
5. Add to appropriate section (Active vs. One-Time)

---

**Project**: ROCK Skills Taxonomy Bridge  
**Hackathon**: Renaissance Learning AI Hackathon 2025

