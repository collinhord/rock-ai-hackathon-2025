# Get Started with PDF Taxonomy Processor

**Status**: ✅ Ready to use  
**Last Updated**: October 16, 2025

---

## 🎯 What You Can Do Now

Your PDF Taxonomy Processor is fully implemented and ready to:

1. **Extract taxonomic structures** from PDFs (math, ELA, science)
2. **Generate master concepts** in proper format
3. **Validate against existing taxonomies** with gap analysis
4. **Integrate with batch mapping pipeline** automatically

---

## 🚀 Quick Start (3 Minutes)

### Step 1: Verify Installation

```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/frameworks
python3 process_framework_pdfs.py --help
```

If you see the help message, you're ready! ✅

### Step 2: Process Your First PDF

#### Option A: Extract Math Taxonomy

```bash
python3 process_framework_pdfs.py \
  --input input/math/cambridge_mathematics_ontology.pdf \
  --subject math \
  --mode full \
  --output output/cambridge
```

**What happens**: Extracts taxonomy structure, generates master concepts, prepares batch mapping files

**Time**: 2-3 minutes  
**Cost**: ~$2-4

#### Option B: Validate ELA Taxonomy

```bash
python3 process_framework_pdfs.py \
  --input input/ela/Reading_Research_Quarterly_2021_Duke.pdf \
  --subject ela \
  --mode validate \
  --output output/duke_validation
```

**What happens**: Compares framework with your existing ELA taxonomy, generates gap report

**Time**: 2-3 minutes  
**Cost**: ~$2-3

### Step 3: Review Results

```bash
# See summary
cat output/*/SUMMARY.md

# Check master concepts (if generated)
cat output/*/concepts/*_master_concepts.csv

# Read gap report (if validated)
cat output/*/validation/*_gap_report.md
```

---

## 📚 Your PDFs Ready to Process

You already have these PDFs in `input/`:

### ELA
- `Reading_Research_Quarterly_2021_Duke.pdf` - Active View of Reading
- `Scarborough-Reading-Rope.pdf` - Classic reading framework

### Math
- `cambridge_mathematics_ontology.pdf` - Comprehensive math ontology

---

## 🎓 Recommended First Steps

### For ELA Enhancement

**Goal**: Validate your existing ELA taxonomy and identify gaps

```bash
# 1. Validate against Duke framework
python3 process_framework_pdfs.py \
  --input input/ela/Reading_Research_Quarterly_2021_Duke.pdf \
  --subject ela \
  --mode validate \
  --output output/duke_validation

# 2. Review gap report
cat output/duke_validation/*/gap_report.md

# 3. Generate concepts from Scarborough
python3 process_framework_pdfs.py \
  --input input/ela/Scarborough-Reading-Rope.pdf \
  --subject ela \
  --mode generate_concepts \
  --prepare-batch-mapping \
  --output output/scarborough_concepts

# 4. Review generated concepts
cat output/scarborough_concepts/ela_master_concepts.csv | head -20
```

**Expected outcome**: 
- Gap analysis showing 60-85% alignment
- 30-50 new concepts identified from frameworks
- Ready-to-use master concepts for integration

### For Math Taxonomy Creation

**Goal**: Build initial math taxonomy from Cambridge Ontology

```bash
# 1. Full extraction and concept generation
python3 process_framework_pdfs.py \
  --input input/math/cambridge_mathematics_ontology.pdf \
  --subject math \
  --mode full \
  --output output/cambridge_full

# 2. Review proposed structure
cat output/cambridge_full/extraction/*_structure.json

# 3. Check generated concepts
wc -l output/cambridge_full/concepts/math_master_concepts.csv
head -20 output/cambridge_full/concepts/math_master_concepts.csv

# 4. Review summary
cat output/cambridge_full/SUMMARY.md
```

**Expected outcome**:
- 200-500 initial math concepts
- Proposed 3-4 level hierarchy
- Batch mapping files ready
- Foundation for comprehensive math taxonomy

---

## 🔄 Batch Processing

Process all PDFs at once:

```bash
# Process all ELA PDFs
./pipeline_integration.sh \
  --subject ela \
  --process-all "input/ela/*.pdf" \
  --mode full

# Process all math PDFs with batch mapping
./pipeline_integration.sh \
  --subject math \
  --process-all "input/math/*.pdf" \
  --batch-mapping
```

---

## 📖 Processing Modes

| Mode | Use Case | Outputs |
|------|----------|---------|
| `extract` | Explore framework structure | JSON extraction + hierarchy proposal |
| `validate` | Check alignment with existing | Gap analysis + recommendations |
| `generate_concepts` | Create master concepts | CSV + batch mapping files |
| `full` | Complete analysis | All of the above |

---

## 💡 Common Use Cases

### "I want to see what's in the Cambridge Ontology"
```bash
python3 process_framework_pdfs.py \
  --input input/math/cambridge_mathematics_ontology.pdf \
  --subject math \
  --mode extract
```

### "I want to validate my ELA taxonomy"
```bash
./pipeline_integration.sh \
  --subject ela \
  --process-all "input/ela/*.pdf" \
  --mode validate
```

### "I want to add concepts from Scarborough's Rope"
```bash
python3 process_framework_pdfs.py \
  --input input/ela/Scarborough-Reading-Rope.pdf \
  --subject ela \
  --mode generate_concepts \
  --prepare-batch-mapping
```

### "I want to build a math taxonomy from scratch"
```bash
python3 process_framework_pdfs.py \
  --input input/math/cambridge_mathematics_ontology.pdf \
  --subject math \
  --mode full
```

---

## 🔗 Next: Batch Mapping Integration

After generating concepts, integrate with your batch mapping pipeline:

```bash
# 1. Navigate to analysis scripts
cd ../analysis/scripts

# 2. Run batch mapping on generated concepts
python3 batch_map_skills_enhanced.py \
  --concept-ids-file ../../frameworks/output/{your_output}/concepts/batch_input/concept_ids.txt \
  --content-area "Mathematics" \
  --checkpoint-interval 10 \
  --output-dir ./outputs/framework_mapping

# 3. Review mappings
cat ./outputs/framework_mapping/*.csv
```

---

## 📊 Cost Tracking

Each run prints:
```
COST SUMMARY
============================================
Total tokens: 45,234
Estimated cost: $0.5234
```

Typical costs (AWS Bedrock):
- Extract mode: $0.50 - $2.00
- Validate mode: $1.00 - $3.00
- Generate concepts: $0.50 - $2.00
- Full pipeline: $2.00 - $6.00

---

## 📚 Documentation

- **Quick Commands**: [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
- **Complete Guide**: [`README_PROCESSOR.md`](README_PROCESSOR.md)
- **Technical Details**: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)
- **Executive Summary**: `/PDF_PROCESSOR_COMPLETE.md` (in root)

---

## ✅ Verify Everything Works

Run this test:

```bash
# Should show help (no errors)
python3 process_framework_pdfs.py --help

# Should show usage (no errors)
./pipeline_integration.sh --help

# Check PDFs are present
ls -lh input/ela/*.pdf
ls -lh input/math/*.pdf
```

If all commands work, you're ready to go! 🎉

---

## 🆘 Troubleshooting

**"AWS credentials not configured"**
```bash
aws configure
# Set region to us-west-2 or us-east-1
```

**"PyPDF2 not available"**
```bash
cd ../taxonomy_builder
pip install -r requirements.txt
```

**"No such file or directory"**
```bash
# Make sure you're in the frameworks directory
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/frameworks
```

---

## 🎯 Your First Task

**Recommended**: Start with ELA validation to understand the system

```bash
# This will take ~2-3 minutes and cost ~$2
python3 process_framework_pdfs.py \
  --input input/ela/Reading_Research_Quarterly_2021_Duke.pdf \
  --subject ela \
  --mode validate \
  --output output/my_first_run

# Then review the results
cat output/my_first_run/SUMMARY.md
```

---

## 📞 Support

- Issues? Check [`README_PROCESSOR.md`](README_PROCESSOR.md) troubleshooting section
- Questions? Review [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
- Technical details? See [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)

---

**Ready?** Pick a command above and start processing! 🚀

The system is fully tested and ready for production use.

