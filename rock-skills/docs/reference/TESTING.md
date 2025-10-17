# Testing & Validation Guide

Comprehensive testing procedures for ROCK Skills Taxonomy Bridge project.

## Quick Reference

```bash
# Pre-demo validation (run before presentations)
bash scripts/quick_demo_test.sh

# Data integrity only
python3 scripts/verify_data_integrity.py

# Full test suite (when available)
python3 -m pytest tests/
```

---

## Automated Testing

### 1. Quick Demo Test (Comprehensive)

**Purpose**: Validates system readiness before demos  
**Runtime**: ~10 seconds  
**Usage**: `bash scripts/quick_demo_test.sh`

**Checks**:
- ✅ Data integrity (7 critical CSV files)
- ✅ Python dependencies (streamlit, pandas, plotly, numpy)
- ✅ Critical files exist (6 files)
- ✅ POC application imports
- ✅ Taxonomy Builder CLI functional

**Exit Codes**:
- `0` - All checks passed, ready for demo
- `1` - One or more checks failed, review output

### 2. Data Integrity Validation

**Purpose**: Verifies all data files load correctly  
**Runtime**: ~3 seconds  
**Usage**: `python3 scripts/verify_data_integrity.py`

**Validates**:
- ROCK Skills (8,224 rows expected)
- Standard-Skill Relationships (949K rows expected)
- Science of Reading Taxonomy (1,139 rows expected)
- LLM Skill Mappings (1,270 rows expected)
- Master Concepts (15 concepts expected)
- Content Library mock data (15 items expected)
- Tagging Scenarios mock data (15 scenarios expected)

**Output**: Per-file validation with ✅/❌ status

---

## Manual Testing

### Content Scaling Simulator (Primary Demo)

#### Pre-Test Setup
```bash
cd poc
streamlit run skill_bridge_app.py
# Wait for "You can now view your Streamlit app..."
# Open browser to http://localhost:8501
```

#### Test Procedure

**1. Home Page**
- [ ] Page loads without errors
- [ ] 4 metric columns display
- [ ] Problem 1 and Problem 2 tabs switch correctly
- [ ] Problem 2 describes content scaling blocked

**2. Content Scaling Simulator** ⭐ (Primary Feature)
- [ ] Page loads without errors
- [ ] Content selector shows 15 items
- [ ] Select "Blend 2-Phoneme CVC Words"
- [ ] Content details expand
- [ ] Three tabs display (Option A, B, C)
- [ ] Option A shows 8% coverage, 1 ROCK skill tagged
- [ ] Option B shows 60 min tagging time, 12 skills
- [ ] Option C shows "bypass ROCK" warning
- [ ] Toggle "Show With Bridge" works
- [ ] Metrics update: 5 min, 1 tag, 100% coverage
- [ ] Bar chart displays correctly
- [ ] 12 states list expands

**3. Cross-State Discovery**
- [ ] Page loads without errors
- [ ] State selector shows 16+ states
- [ ] Select "CA" (California)
- [ ] Select "Phoneme Blending" concept
- [ ] WITHOUT BRIDGE shows 1-2 content found
- [ ] Hidden content expander works
- [ ] Toggle "Show With Bridge" works
- [ ] WITH BRIDGE shows 3/3 content found
- [ ] Bar chart displays

**4. Scaling Impact Dashboard**
- [ ] Page loads without errors
- [ ] Overview metrics display
- [ ] WITHOUT BRIDGE section shows inefficiency
- [ ] WITH BRIDGE section shows efficiency
- [ ] ROI sliders work and update metrics in real-time
- [ ] Break-even calculation displays
- [ ] Timeline chart renders
- [ ] Key Insights section comprehensive

**5. Navigation & Performance**
- [ ] All sidebar links work
- [ ] No 404 errors
- [ ] Pages load in < 2 seconds
- [ ] No console errors (F12 → Console)
- [ ] No Python errors in terminal

### Taxonomy Builder System

#### CLI Commands Test

```bash
cd taxonomy_builder

# Test 1: Help command
python3 cli.py --help
# Expected: Help menu displays

# Test 2: Validation (no LLM needed)
python3 cli.py validate --output ../test_validation.md
# Expected: Report generated, no errors

# Test 3: Check database
cd ..
sqlite3 taxonomy.db "SELECT COUNT(*) FROM taxonomy_nodes;"
# Expected: 2070

# Test 4: Check UUID map
python3 -c "import json; data = json.load(open('taxonomy_uuid_map.json')); print(f'UUIDs: {len(data)}')"
# Expected: UUIDs: 2070 (or 4140 for bidirectional)
```

### Analysis Pipeline

#### Notebook Test
```bash
cd analysis
jupyter notebook redundancy-analysis.ipynb

# In notebook:
# 1. Kernel → Restart & Run All
# 2. Wait for completion (~2-3 minutes)
# 3. Check outputs created:
#    - fragmentation-examples.csv
#    - fragmented_skill_patterns.csv
#    - PNG chart files
```

#### Batch Mapping Test (Optional - Requires AWS)
```bash
cd analysis

# Create test file with 2 skill IDs
echo "skill-id-1" > test_skills.txt
echo "skill-id-2" >> test_skills.txt

# Run small test batch
python scripts/batch_map_skills.py \
    --skill-ids-file test_skills.txt \
    --content-area "English Language Arts" \
    --output-dir ./outputs/test_batch \
    --checkpoint-interval 1

# Expected: Mappings created in outputs/test_batch/
```

---

## Environment Testing

### Python Dependencies Check

```bash
# Test all core dependencies
python3 << 'EOF'
import sys
missing = []
for pkg in ['streamlit', 'pandas', 'numpy', 'plotly', 'boto3']:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg} - MISSING")
        missing.append(pkg)

if missing:
    print(f"\nInstall missing: pip install {' '.join(missing)}")
    sys.exit(1)
EOF
```

### AWS Credentials (Optional - for LLM features)

```bash
# Test AWS Bedrock access
aws bedrock list-foundation-models --region us-west-2 | head -20

# Expected: JSON list of models including Claude
```

---

## Performance Testing

### Load Time Tests

```bash
# Time to load main application
time python3 -c "import sys; sys.path.insert(0, 'poc'); import skill_bridge_app"
# Target: < 5 seconds

# Time to load data
time python3 -c "import sys; sys.path.insert(0, 'poc'); from data_loader import ROCKDataLoader; loader = ROCKDataLoader()"
# Target: < 10 seconds (includes loading large CSVs)
```

### Data Loading Performance

```bash
cd poc
python3 << 'EOF'
import time
from data_loader import ROCKDataLoader

start = time.time()
loader = ROCKDataLoader()
load_time = time.time() - start

print(f"Data load time: {load_time:.2f}s")
print(f"Skills loaded: {len(loader.get_all_skills())}")
print(f"Taxonomy entries: {len(loader.get_taxonomy_df())}")

if load_time > 15:
    print("⚠️  Slow load time")
else:
    print("✅ Performance OK")
EOF
```

---

## Regression Testing

### After Code Changes

1. **Run Quick Demo Test**
   ```bash
   bash scripts/quick_demo_test.sh
   ```

2. **Manual Smoke Test**
   - Launch Streamlit app
   - Click through all 6 pages
   - Test one feature per page
   - Verify no errors

3. **Data Integrity Check**
   ```bash
   python3 scripts/verify_data_integrity.py
   ```

### After Data Updates

1. **Validate New Data**
   ```bash
   python3 scripts/verify_data_integrity.py
   ```

2. **Regenerate Database** (if taxonomy changed)
   ```bash
   python3 scripts/csv_to_db.py
   ```

3. **Test Applications**
   - POC app loads new data
   - Taxonomy builder reflects changes

---

## Troubleshooting Tests

### Issue: Streamlit Won't Start

```bash
# Check if already running
ps aux | grep streamlit

# Kill if needed
pkill -f streamlit

# Restart
cd poc && streamlit run skill_bridge_app.py
```

### Issue: Data Not Loading

```bash
# Check file exists
ls -lh poc/mock_data/*.csv

# Test manual load
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('poc/mock_data/content_library.csv')
print(f"Loaded {len(df)} rows")
EOF
```

### Issue: Import Errors

```bash
# Reinstall dependencies
cd poc
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

---

## Test Coverage

### Current Test Status

| Component | Automated | Manual | Coverage |
|-----------|-----------|--------|----------|
| Data Integrity | ✅ Script | ✅ Visual | 100% |
| POC App | ⚠️ Imports only | ✅ Full | 80% |
| Taxonomy Builder | ✅ CLI test | ✅ Commands | 70% |
| Analysis Pipeline | ❌ None | ✅ Notebook | 50% |
| Scripts | ✅ Demo test | ❌ None | 60% |

### Recommended Additions

**High Priority**:
- [ ] Unit tests for data_loader.py functions
- [ ] Integration tests for POC app pages
- [ ] Taxonomy Builder validation tests

**Medium Priority**:
- [ ] Analysis pipeline output validation
- [ ] Mock data generation tests
- [ ] Database integrity tests

**Low Priority**:
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] UI screenshot tests

---

## Continuous Integration (Future)

### Recommended CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r poc/requirements.txt
          pip install pytest
      - name: Data integrity check
        run: python3 scripts/verify_data_integrity.py
      - name: Quick demo test
        run: bash scripts/quick_demo_test.sh
```

---

## Test Data Management

### Mock Data Files

Located in `poc/mock_data/`:
- `content_library.csv` - 15 realistic content items
- `tagging_scenarios.csv` - 15 tagging scenarios

**Updating Mock Data**:
1. Edit CSV files directly
2. Maintain column structure
3. Run data integrity check
4. Test in POC app

### Test Fixtures (Future)

Create `tests/fixtures/` with:
- Minimal taxonomy sample (10 rows)
- Sample skills (50 rows)
- Sample mappings (20 rows)

---

## Reporting Issues

### Bug Report Template

```markdown
**Component**: (POC App / Taxonomy Builder / Analysis / Scripts)
**Severity**: (Critical / Major / Minor)
**Description**: What went wrong?
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected**: What should happen?
**Actual**: What actually happened?
**Environment**: (OS, Python version, dependencies)
**Logs/Screenshots**: Attach if applicable
```

---

## Best Practices

1. **Before every demo**: Run `scripts/quick_demo_test.sh`
2. **After code changes**: Manual smoke test all pages
3. **After data updates**: Run `verify_data_integrity.py`
4. **Weekly**: Full manual test of all features
5. **Before releases**: Complete regression testing

---

**Project**: ROCK Skills Taxonomy Bridge  
**Hackathon**: Renaissance Learning AI Hackathon 2025  
**Testing Status**: ✅ Core validation automated, comprehensive manual procedures

