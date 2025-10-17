# ROCK Skills Taxonomy - Workflow Guide

## Quick Reference Card

| Workflow | Script | Time | Cost | Use When |
|----------|--------|------|------|----------|
| **Status Check** | `./scripts/status.sh` | < 1 min | Free | Check system state anytime |
| **First Setup** | `analysis/pipelines/quick_start.sh` | 5-10 min | Free | Initial setup & testing |
| **Full Refresh** | `./scripts/refresh_taxonomy.sh` | 3-5 hrs | $40-60 | Major updates, complete rebuild |
| **Incremental Update** | `./scripts/update_taxonomy.sh` | 30-60 min | $5-10 | Add new ROCK skills only |
| **Conflict Resolution** | `./scripts/apply_decisions.sh` | 5-10 min | Free | After UI conflict grooming |
| **Quality Check** | `./scripts/validate_taxonomy.sh` | 10-15 min | Free | Before deploy/commit |

---

## Detailed Workflows

### 1. First Time Setup

**Goal**: Validate system works with sample data

**Who**: New developers, testers, or first-time users

**Steps**:

```bash
cd rock-skills/analysis/pipelines

# Install all dependencies and run test
./quick_start.sh
```

This will:
- Install Python dependencies (spaCy, sentence-transformers, etc.)
- Download spaCy language model (en_core_web_lg)
- Run POC test on 20 sample skills
- Validate all imports work
- Create sample outputs

**Expected Output**:
```
✓ Dependencies installed
✓ spaCy model downloaded
✓ Test extraction complete (20 skills)
✓ Sample base skills generated
✓ Sample specifications created
```

**Next Step**: Launch UI to explore
```bash
cd ../../poc
streamlit run skill_bridge_app.py
```

---

### 2. System Status Check

**Goal**: See current state and what needs attention

**Who**: Anyone, anytime

**Steps**:

```bash
cd rock-skills
./scripts/status.sh
```

**Reads**:
- Database existence and stats
- Pending conflicts count
- MECE validation score
- Running background processes

**Example Output**:
```
╔════════════════════════════════════════════════════════════╗
║  ROCK Skills Taxonomy - System Status                     ║
╚════════════════════════════════════════════════════════════╝

📊 Database: ✓ Exists
   - Base Skills: 847
   - ROCK Skills Mapped: 2,900
   - Last Updated: 2025-10-16 14:23:15

✓ Conflicts: None pending

📈 MECE Score: 0.92

Next Actions:
  • View UI? Run: cd poc && streamlit run skill_bridge_app.py
```

---

### 3. Full Taxonomy Refresh

**Goal**: Regenerate entire taxonomy from scratch with latest ROCK data

**Who**: After major ROCK schema updates, or for clean rebuild

**When**:
- ROCK adds hundreds of new skills
- Scientific framework updated
- Major algorithm changes
- Starting fresh after experimental changes

**Steps**:

```bash
cd rock-skills

# Full refresh with LLM (best quality, costly)
./scripts/refresh_taxonomy.sh

# OR without LLM (faster, free, lower quality)
./scripts/refresh_taxonomy.sh --no-llm

# OR test mode (100 skills only, no LLM)
./scripts/refresh_taxonomy.sh --test
```

**What It Does**:
1. **Backup**: Creates timestamped backup of existing `taxonomy.db`
2. **Extract Base Skills**: Processes all ROCK skills → base skills (2-3 hours)
3. **Extract Specifications**: Derives hierarchical specs from mappings (30-60 min)
4. **Validate MECE**: Detects conflicts and redundancies (10-15 min)
5. **Generate Reports**: Creates summary analytics

**Expected Output**:
```
╔════════════════════════════════════════════════════════════╗
║  REFRESH COMPLETE                                          ║
╚════════════════════════════════════════════════════════════╝

⏱️  Total Time: 3h 24m 15s

📊 Validation Summary:
   • MECE Score: 0.89
   • Base Skills: 1,243
   • ROCK Skills Mapped: 8,355
   • Conflicts Detected: 47

Next Steps:
  1️⃣  Review conflicts: cd poc && streamlit run skill_bridge_app.py
  2️⃣  Check status: ./scripts/status.sh
  3️⃣  Validate quality: ./scripts/validate_taxonomy.sh
```

**Cost Estimate**:
- With LLM: ~$40-60 (8,000 skills × 200 tokens avg)
- Without LLM: Free (spaCy + clustering only)

**Files Modified**:
- `taxonomy.db` (regenerated)
- `taxonomy/base_skills/*.json` (regenerated)
- `taxonomy/validation_report.json` (updated)
- `backups/taxonomy_backup_TIMESTAMP.db` (created)

---

### 4. Incremental Update

**Goal**: Add only new ROCK skills without regenerating everything

**Who**: After ROCK adds small batches of new skills

**When**:
- ROCK adds 10-100 new skills
- Monthly updates
- Don't want to wait 3-5 hours for full refresh

**Steps**:

```bash
cd rock-skills

# Auto-detect new skills
./scripts/update_taxonomy.sh

# OR specify date
./scripts/update_taxonomy.sh --since 2025-10-15

# OR provide file
./scripts/update_taxonomy.sh --new-skills data/october_skills.csv
```

**What It Does**:
1. **Identify New**: Finds skills not in current taxonomy
2. **Extract**: Processes only new skills → base skills
3. **Merge**: Attempts to map to existing base skills first
4. **Validate**: Checks for conflicts with existing taxonomy
5. **Update DB**: Incrementally adds to taxonomy.db

**Expected Output**:
```
╔════════════════════════════════════════════════════════════╗
║  UPDATE COMPLETE                                           ║
╚════════════════════════════════════════════════════════════╝

📊 Update Summary:
   • New ROCK Skills: 42
   • New Base Skills: 7
   • New Conflicts: 3

Next Steps:
  • Review changes: ./scripts/status.sh
  • Resolve conflicts: cd poc && streamlit run skill_bridge_app.py
```

**Time**: 30-60 minutes (proportional to new skills count)

**Cost**: ~$5-10 per 100 new skills

---

### 5. Conflict Resolution (Human-in-the-Loop)

**Goal**: Review and resolve flagged conflicts interactively

**Who**: Curriculum experts, data quality team

**When**:
- After full refresh or incremental update
- MECE score < 0.90
- Conflicts count > 0

**Steps**:

**Part A: Review Conflicts in UI**

```bash
cd rock-skills/poc
streamlit run skill_bridge_app.py
```

1. Navigate to **"Redundancy Grooming"** page
2. Review flagged conflicts:
   - Potential duplicates (e.g., "narrative perspective" vs "narrator perspective")
   - Ambiguous phrasings
   - Overlapping base skills
3. For each conflict, choose action:
   - **Merge**: Combine into single base skill
   - **Specify**: Keep both, add specification to differentiate
   - **Clarify**: Update description to distinguish
   - **Keep**: No conflict, false positive
4. **Export Decisions**: Saves to `taxonomy/decisions.json`

**Part B: Apply Decisions**

```bash
cd rock-skills/scripts
./apply_decisions.sh

# OR preview first
./apply_decisions.sh --dry-run
```

**What It Does**:
1. Reads `taxonomy/decisions.json`
2. Merges redundant base skills
3. Adds new specifications
4. Updates clarifications
5. Regenerates validation report

**Expected Output**:
```
╔════════════════════════════════════════════════════════════╗
║  DECISIONS APPLIED                                         ║
╚════════════════════════════════════════════════════════════╝

Applied 23 decisions:
   • Merged: 8 base skills
   • Added specifications: 12
   • Clarified: 3

Next Steps:
  • Check status: ./scripts/status.sh
  • View changes: cd poc && streamlit run skill_bridge_app.py
```

---

### 6. Quality Validation

**Goal**: Comprehensive quality checks before committing/deploying

**Who**: Before git commits, before production deploy

**When**:
- After resolving conflicts
- Before presenting to stakeholders
- Regular quality audits

**Steps**:

```bash
cd rock-skills

# Full validation
./scripts/validate_taxonomy.sh

# OR quick mode (skip LLM analysis)
./scripts/validate_taxonomy.sh --quick
```

**What It Checks**:
1. **MECE Score**: Ensures > 0.90 threshold
2. **Coverage**: % of ROCK skills mapped
3. **Data Integrity**: Orphaned records, missing fields
4. **Specification Completeness**: Base skills with specs
5. **Conflict Detection**: Any remaining issues

**Expected Output**:
```
╔════════════════════════════════════════════════════════════╗
║  VALIDATION COMPLETE                                       ║
╚════════════════════════════════════════════════════════════╝

📊 Summary:
   • MECE Score: 0.93
   ✓ MECE score meets threshold
   ✓ No conflicts detected
   • Coverage: 97.2%
   ✓ No integrity issues
   • Specification Coverage: 84.3%

Full report: analysis/reports/quality_report_20251016_143052.txt
```

**Fails If**:
- MECE score < 0.90
- Coverage < 80%
- Data integrity errors found

---

## When to Use Which Workflow

### Decision Tree

```
START: What do you want to do?
│
├─ I'm new / first time
│  └─ Run: analysis/pipelines/quick_start.sh
│     Then: streamlit run poc/skill_bridge_app.py
│
├─ I want to check current state
│  └─ Run: ./scripts/status.sh
│
├─ I want to rebuild everything
│  └─ Run: ./scripts/refresh_taxonomy.sh
│
├─ I have new ROCK skills to add
│  └─ Run: ./scripts/update_taxonomy.sh
│
├─ I need to fix conflicts
│  └─ 1. UI: Redundancy Grooming page (make decisions)
│     2. Run: ./scripts/apply_decisions.sh
│
└─ I want to validate quality
   └─ Run: ./scripts/validate_taxonomy.sh
```

---

## Configuration

All workflows respect `config.yaml` settings:

```yaml
extraction:
  use_llm: true              # false = free but lower quality
  checkpoint_interval: 50    # Save every N skills

validation:
  mece_threshold: 0.90       # Minimum acceptable score

database:
  auto_backup: true          # Backup before major ops
  max_backups: 10            # Keep last N backups
```

**Edit this file to control**:
- LLM usage (cost vs. quality tradeoff)
- Checkpoint frequency
- Validation thresholds
- Backup retention

---

## Monitoring Long-Running Processes

### Check Progress

If `refresh_taxonomy.sh` is running in background:

```bash
# Check base skill extraction progress
tail -f analysis/pipelines/extraction.log

# Check metadata enrichment
tail -f analysis/outputs/metadata_enrichment_full/progress.log

# View cost estimates
grep "Estimated Cost" analysis/pipelines/extraction.log
```

### Resume After Interruption

All scripts use checkpoints. If interrupted:

```bash
# Extraction will resume from last checkpoint
./scripts/refresh_taxonomy.sh
# Detects existing checkpoint_metadata_TIMESTAMP.csv and resumes
```

---

## Troubleshooting

### Script Fails: "Database not found"

**Solution**: Run full refresh first
```bash
./scripts/refresh_taxonomy.sh
```

### Script Fails: "AWS credentials not configured"

**Solution**: Configure AWS Bedrock access (only if use_llm=true)
```bash
aws configure
# Or set in config.yaml: use_llm: false
```

### Low MECE Score (< 0.90)

**Solution**: Review and resolve conflicts
```bash
# 1. See what conflicts exist
./scripts/status.sh

# 2. Resolve in UI
cd poc && streamlit run skill_bridge_app.py
# Go to Redundancy Grooming page

# 3. Apply decisions
cd ../scripts && ./apply_decisions.sh

# 4. Validate again
./scripts/validate_taxonomy.sh
```

### "Orphaned mappings" or data integrity errors

**Solution**: Run full refresh to rebuild from scratch
```bash
./scripts/refresh_taxonomy.sh
```

---

## Script Hierarchy

### Tier 1: Master Orchestration (Run These)

**Location**: `scripts/`

These handle complete workflows:
- `refresh_taxonomy.sh` - Full rebuild
- `update_taxonomy.sh` - Incremental update
- `apply_decisions.sh` - Apply conflict resolutions
- `validate_taxonomy.sh` - Quality checks
- `status.sh` - System status

### Tier 2: Single-Purpose Pipelines (Called by Tier 1)

**Location**: `analysis/pipelines/`

Specific transformations:
- `extract_base_skills.py` - ROCK → Base skills
- `extract_specifications.py` - Mappings → Specs
- `validate_mece.py` - Conflict detection
- `test_extraction_poc.py` - Quick validation

Can be run directly for development/testing:
```bash
python3 analysis/pipelines/extract_base_skills.py --limit 100 --no-llm
```

### Tier 3: Utilities (Support Functions)

**Location**: `scripts/utils/`

Helper scripts:
- `generate_reports.py` - Analytics
- `export_to_csv.py` - SQLite → CSV
- `apply_decisions.py` - Decision application logic

---

## Best Practices

### Before Making Changes
```bash
./scripts/status.sh                    # Document current state
cp taxonomy.db taxonomy.db.manual      # Manual backup
```

### After Making Changes
```bash
./scripts/validate_taxonomy.sh         # Verify quality
./scripts/status.sh                    # Check new state
git add -A && git commit -m "..."      # Commit if good
```

### Before Presenting/Deploying
```bash
./scripts/validate_taxonomy.sh         # Full validation
./scripts/utils/generate_reports.py    # Generate metrics
cd poc && streamlit run skill_bridge_app.py  # Smoke test UI
```

### Cost Management
```bash
# Test changes without LLM first
./scripts/refresh_taxonomy.sh --test --no-llm

# If results look good, run with LLM
./scripts/refresh_taxonomy.sh
```

---

## Quick Command Reference

```bash
# Status
./scripts/status.sh

# Setup
analysis/pipelines/quick_start.sh

# Full refresh
./scripts/refresh_taxonomy.sh
./scripts/refresh_taxonomy.sh --no-llm          # Free
./scripts/refresh_taxonomy.sh --test           # 100 skills

# Incremental
./scripts/update_taxonomy.sh
./scripts/update_taxonomy.sh --since 2025-10-15
./scripts/update_taxonomy.sh --new-skills file.csv

# Conflicts
# (UI) cd poc && streamlit run skill_bridge_app.py
./scripts/apply_decisions.sh
./scripts/apply_decisions.sh --dry-run

# Validate
./scripts/validate_taxonomy.sh
./scripts/validate_taxonomy.sh --quick

# Utilities
python3 scripts/utils/generate_reports.py
python3 scripts/utils/export_to_csv.py
```

---

## Additional Resources

- **Architecture**: [base-skill-architecture.md](../architecture/base-skill-architecture.md)
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Pipeline Details**: [analysis/pipelines/README.md](analysis/pipelines/README.md)
- **Configuration**: [config.yaml](config.yaml)

---

**Need help? Check system status first:**
```bash
./scripts/status.sh
```

