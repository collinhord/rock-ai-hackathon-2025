# Getting Started with Taxonomy Builder

**Implementation Status:** ✅ **COMPLETE AND READY TO USE**

---

## What You Have Now

Your taxonomy cleanup and builder system is fully implemented and operational. Here's what you can do:

### 1. 📊 Validate Your Taxonomy

Run comprehensive validation to check structure, find duplicates, and identify gaps:

```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/taxonomy_builder

python3 cli.py validate --output validation_report.md
```

**Cost:** FREE (no LLM calls)  
**Time:** ~5-10 seconds  
**Output:** Detailed markdown report with issues and recommendations

### 2. 📚 Analyze Academic Frameworks

Compare your taxonomy against research frameworks:

#### Step 1: Add Framework PDF
```bash
# Example: You already have cambridge_mathematics_ontology.pdf in frameworks/input/math/
# Add more frameworks:
cp ~/Downloads/scarborough_rope.pdf frameworks/input/ela/
cp ~/Downloads/nrp_report.pdf frameworks/input/ela/
```

#### Step 2: Document the Source
Edit `frameworks/input/ela/sources.md` to add framework details

#### Step 3: Run Analysis
```bash
cd taxonomy_builder

python3 cli.py compare ../frameworks/input/ela/scarborough_rope.pdf \
    --output ../frameworks/output/scarborough_analysis.md
```

**Cost:** ~$0.50-3.00 per framework (AWS Bedrock)  
**Time:** 30-60 seconds per framework  
**Output:** Detailed comparison with gaps and recommendations

### 3. 🔍 Get Naming Suggestions

Use LLM to identify naming inconsistencies:

```bash
cd taxonomy_builder

python3 cli.py suggest --aspect naming \
    --output naming_suggestions.json
```

**Cost:** ~$0.10-0.50  
**Time:** 20-30 seconds  
**Output:** JSON with suggested naming improvements

### 4. 📝 Generate Comprehensive Report

Create a full analysis report:

```bash
cd taxonomy_builder

python3 cli.py report --output comprehensive_report.md
```

---

## Quick Reference

### Directory Structure

```
rock-skills/
├── POC_science_of_reading_literacy_skills_taxonomy.csv  ← Your cleaned taxonomy (CSV)
├── taxonomy_uuid_map.json                               ← UUID mappings (2,070 nodes)
├── taxonomy.db                                          ← SQLite database
│
├── frameworks/                                          ← Framework organization
│   ├── README.md                                       ← Full documentation
│   ├── QUICK_START.md                                  ← Quick guide
│   ├── input/                                          ← PUT YOUR PDFs HERE
│   │   ├── ela/        ← ELA frameworks
│   │   ├── math/       ← Math frameworks (cambridge_ontology.pdf already here!)
│   │   ├── science/    ← Science frameworks
│   │   └── general/    ← Cross-disciplinary
│   └── output/                                         ← Analysis reports appear here
│
├── taxonomy_builder/                                    ← Main tool
│   ├── cli.py          ← Command-line interface
│   ├── README.md       ← Full documentation
│   └── ...             ← Supporting modules
│
└── scripts/                                            ← Utility scripts
    ├── cleanup_taxonomy.py      ← Already run ✅
    ├── generate_uuid_map.py     ← Already run ✅
    └── csv_to_db.py             ← Already run ✅
```

### Important Files

- **`PLAN_VERIFICATION.md`** - Proof that everything is implemented ✅
- **`IMPLEMENTATION_COMPLETE.md`** - Detailed implementation summary
- **`frameworks/QUICK_START.md`** - Quick guide for framework analysis
- **`taxonomy_builder/README.md`** - Complete CLI documentation

---

## Recommended Next Steps

### Week 1: Validate and Review
```bash
# 1. Run validation
cd taxonomy_builder
python3 cli.py validate --output ../validation_report.md

# 2. Review the report
open ../validation_report.md

# 3. Address any critical issues identified
```

### Week 2: Framework Analysis - ELA Focus

**Recommended frameworks to analyze:**

1. **Scarborough's Reading Rope** (2001)
   - Core reading comprehension framework
   - Download and add to `frameworks/input/ela/`

2. **Active View of Reading** (Duke & Cartwright, 2021)
   - Already documented in `frameworks/input/ela/sources.md`
   - Modern extension of Simple View of Reading

3. **National Reading Panel Report** (2000)
   - Evidence base for reading instruction

```bash
# After adding PDFs:
cd taxonomy_builder
python3 cli.py compare ../frameworks/input/ela/scarborough_rope.pdf \
    --output ../frameworks/output/scarborough_analysis.md
```

### Week 3: Cross-Framework Comparison

Analyze multiple frameworks and look for patterns:

```bash
# Batch process all ELA frameworks
for file in ../frameworks/input/ela/*.pdf; do
    basename=$(basename "$file" .pdf)
    echo "Analyzing: $basename"
    python3 cli.py compare "$file" \
        --output "../frameworks/output/${basename}_analysis.md"
done
```

Then review all reports in `frameworks/output/` to identify:
- Common concepts missing from your taxonomy
- Inconsistencies in how concepts are organized
- Opportunities for taxonomy reorganization

---

## AWS Bedrock Setup (Required for LLM Features)

If you haven't already configured AWS:

```bash
# Install AWS CLI if needed
brew install awscli  # Mac
# or: pip install awscli

# Configure credentials
aws configure

# Test connection
aws bedrock list-foundation-models --region us-east-1
```

The system uses **Claude Sonnet 4.5** by default (model: `anthropic.claude-3-5-sonnet-20241022-v2:0`)

---

## Cost Estimates

### Validation
- **FREE** - No LLM calls required

### Framework Analysis
- Small (10-20 pages): ~$0.50-1.00
- Medium (50-100 pages): ~$1.00-3.00
- Large (200+ pages): ~$3.00-10.00

### Naming Suggestions
- ~$0.10-0.50 per run

### Batch Processing
- 10 frameworks: ~$5-20 depending on size

---

## Troubleshooting

### "boto3 not available"
```bash
pip install boto3
```

### "PyPDF2 not available"
```bash
pip install PyPDF2 python-docx
```

### "AWS credentials not configured"
```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

### "Cannot find taxonomy.db"
The database should be at: `/Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/taxonomy.db`

If missing, regenerate:
```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills
python3 scripts/csv_to_db.py
```

---

## Your Current Assets

### ✅ Already Created
- **2,070 taxonomy nodes** with UUIDs
- **3.1 MB SQLite database** with full hierarchy
- **Validation report** showing current state
- **Cambridge Mathematics Ontology** framework (already in `frameworks/input/math/`)

### 📋 Frameworks Already Documented
- **ELA:** Active View of Reading (sources documented)
- **Math:** Cambridge Mathematics Ontology (PDF in place!)
- See `frameworks/input/{ela,math}/sources.md` for details

### 🔧 Tools Ready to Use
1. `cli.py validate` - Structure validation
2. `cli.py compare` - Framework comparison
3. `cli.py suggest` - LLM suggestions
4. `cli.py report` - Comprehensive reports

---

## Quick Test

Verify everything works:

```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/taxonomy_builder

# Test 1: CLI help
python3 cli.py --help

# Test 2: Quick validation (no LLM needed)
python3 cli.py validate --output test_validation.md

# Check output
ls -lh ../test_validation.md
```

---

## Questions?

- **Full documentation:** `taxonomy_builder/README.md`
- **Framework guide:** `frameworks/README.md` or `frameworks/QUICK_START.md`
- **Implementation details:** `IMPLEMENTATION_COMPLETE.md`
- **Verification:** `PLAN_VERIFICATION.md`

---

## What Makes This Different

This isn't just a validator - it's a **research-informed taxonomy development system**:

1. **Backward Compatible** - All existing tools still work
2. **Database-Backed** - Fast queries, scalable
3. **LLM-Powered** - Intelligent analysis and suggestions
4. **Framework-Driven** - Compare against academic research
5. **Organized** - Clear structure for inputs/outputs
6. **Documented** - Comprehensive guides and examples

**You're ready to start analyzing frameworks! 🚀**

Start with: `frameworks/input/math/cambridge_mathematics_ontology.pdf` - it's already there!

