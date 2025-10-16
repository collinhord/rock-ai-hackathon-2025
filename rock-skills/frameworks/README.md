# Framework Input Directory

This directory is for storing academic frameworks, pedagogical documents, and scientific literature that you want to analyze and compare against the Science of Reading taxonomy.

## Directory Structure

```
frameworks/
├── input/               # Place your framework documents here
│   ├── ela/            # English Language Arts frameworks
│   ├── math/           # Mathematics frameworks
│   ├── science/        # Science frameworks
│   └── general/        # Cross-disciplinary or general frameworks
└── output/             # Analysis reports will be saved here
```

## Supported File Formats

The framework analyzer supports:
- **PDF** (`.pdf`) - Most academic papers and official frameworks
- **Word** (`.docx`) - Editable documents and drafts
- **Text** (`.txt`, `.md`) - Plain text and markdown documents

## How to Use

### 1. Add Your Frameworks

Place framework documents in the appropriate subject directory:

```bash
# Example: Add Common Core ELA standards
cp ~/Downloads/common_core_ela.pdf frameworks/input/ela/

# Example: Add Scarborough's Reading Rope
cp ~/Downloads/scarborough_rope.pdf frameworks/input/ela/

# Example: Add Math frameworks
cp ~/Downloads/nctm_standards.pdf frameworks/input/math/
```

### 2. Analyze a Single Framework

```bash
cd ../taxonomy_builder

# Analyze and compare with our taxonomy
python3 cli.py compare ../frameworks/input/ela/scarborough_rope.pdf \
    --output ../frameworks/output/scarborough_analysis.md
```

### 3. Batch Analyze Multiple Frameworks

You can create a simple script to process all frameworks in a directory:

```bash
# Analyze all ELA frameworks
for file in ../frameworks/input/ela/*.pdf; do
    basename=$(basename "$file" .pdf)
    python3 cli.py compare "$file" \
        --output "../frameworks/output/${basename}_analysis.md"
done
```

Or use Python:

```python
from pathlib import Path
from taxonomy_builder import TaxonomyAccess, LLMInterface, FrameworkAnalyzer

frameworks = list(Path('../frameworks/input/ela').glob('*.pdf'))

with TaxonomyAccess() as tax:
    llm = LLMInterface(provider='bedrock')
    analyzer = FrameworkAnalyzer(tax, llm)
    
    # Batch analyze
    results = analyzer.batch_analyze(frameworks)
    
    # Generate combined report
    report = analyzer.generate_report(
        results, 
        Path('../frameworks/output/ela_batch_analysis.md')
    )
```

## Framework Examples by Category

### English Language Arts (ELA)

Recommended frameworks to analyze:
- **Scarborough's Reading Rope** - Core reading comprehension framework
- **Common Core State Standards** - ELA standards
- **National Reading Panel** - Evidence-based reading instruction
- **Simple View of Reading** - Decoding × Comprehension model
- **DIBELS** - Dynamic Indicators of Basic Early Literacy Skills
- **Fountas & Pinnell** - Literacy Continuum
- **Wilson Reading System** - Structured literacy approach

### Mathematics

Recommended frameworks:
- **NCTM Standards** - National Council of Teachers of Mathematics
- **Common Core Math Standards** - CCSS Mathematics
- **Mathematical Practices** - Standards for Mathematical Practice
- **Number Sense Frameworks** - Early numeracy development

### Science

Recommended frameworks:
- **Next Generation Science Standards (NGSS)**
- **Science Practices and Crosscutting Concepts**
- **STEM Integration Frameworks**

### General/Cross-Disciplinary

Recommended frameworks:
- **Bloom's Taxonomy** - Cognitive domain classification
- **Webb's Depth of Knowledge** - Cognitive complexity
- **21st Century Skills Frameworks**
- **Universal Design for Learning (UDL)**
- **Social-Emotional Learning (SEL) Frameworks**

## Analysis Output

Analysis reports will be saved to `frameworks/output/` and include:

1. **Extracted Taxonomy** - Structure pulled from the framework
2. **Alignment Score** - Overall compatibility with our taxonomy
3. **Missing Concepts** - What the framework has that we don't
4. **Unique Concepts** - What we have that the framework doesn't
5. **Recommendations** - Actionable suggestions for improvement

### Example Output Structure

```
frameworks/output/
├── scarborough_analysis.md          # Individual framework analysis
├── scarborough_analysis.json        # Machine-readable format
├── ela_batch_analysis.md            # Combined analysis of all ELA
└── comparison_summary.md            # High-level summary
```

## Organizing Your Frameworks

### Naming Convention

Use descriptive filenames:
```
✅ Good:
- scarborough_reading_rope_2001.pdf
- common_core_ela_standards_k5.pdf
- nrp_report_2000.pdf

❌ Avoid:
- framework.pdf
- document1.pdf
- untitled.pdf
```

### Metadata File (Optional)

You can create a `metadata.json` in each directory to track framework information:

```json
{
  "frameworks": [
    {
      "filename": "scarborough_reading_rope_2001.pdf",
      "title": "Scarborough's Reading Rope",
      "author": "Hollis Scarborough",
      "year": 2001,
      "type": "theoretical_framework",
      "focus": "reading_comprehension",
      "status": "analyzed",
      "analysis_date": "2025-10-15"
    }
  ]
}
```

## Best Practices

### 1. Version Control
Keep original versions and note any modifications:
```
frameworks/input/ela/
├── common_core_ela_2010_original.pdf
└── common_core_ela_2023_revised.pdf
```

### 2. Source Documentation
Create a `sources.md` file in each directory:
```markdown
# ELA Framework Sources

## Scarborough's Reading Rope
- **Source:** Scarborough, H. S. (2001)
- **URL:** https://...
- **Retrieved:** 2025-10-15
- **Notes:** Seminal framework for reading comprehension

## Common Core ELA
- **Source:** Common Core State Standards Initiative
- **URL:** http://www.corestandards.org/
- **Retrieved:** 2025-10-15
```

### 3. Batch Processing
Process frameworks in logical groups:
```bash
# Process all foundational reading frameworks
python3 cli.py compare ../frameworks/input/ela/scarborough*.pdf
python3 cli.py compare ../frameworks/input/ela/simple_view*.pdf
python3 cli.py compare ../frameworks/input/ela/nrp*.pdf
```

## Integration with Taxonomy Builder

The framework analyzer automatically:

1. **Extracts** - Pulls out the taxonomy structure using LLM
2. **Compares** - Compares against our Science of Reading taxonomy
3. **Identifies** - Finds gaps and overlaps
4. **Recommends** - Suggests specific additions or modifications
5. **Reports** - Generates actionable markdown reports

## Cost Considerations

LLM analysis costs vary by framework size:
- **Small framework** (10-20 pages): ~$0.50-1.00
- **Medium framework** (50-100 pages): ~$1.00-3.00
- **Large framework** (200+ pages): ~$3.00-10.00

**Tip:** Process first 50 pages for large documents:
```python
# Extract first N pages from PDF before analysis
# See framework_analyzer.py for details
```

## Example Workflow

### Week 1: Core Reading Frameworks
```bash
# Add frameworks
cp ~/reading_frameworks/*.pdf frameworks/input/ela/

# Analyze
python3 cli.py compare frameworks/input/ela/scarborough_rope.pdf
python3 cli.py compare frameworks/input/ela/simple_view_reading.pdf
python3 cli.py compare frameworks/input/ela/nrp_report.pdf

# Review outputs
ls frameworks/output/
```

### Week 2: Standards Alignment
```bash
# Add state/national standards
cp ~/standards/*.pdf frameworks/input/ela/

# Batch analyze
python3 batch_analyze.py --input frameworks/input/ela/ \
                         --output frameworks/output/standards_report.md
```

### Week 3: Cross-Disciplinary
```bash
# Compare with general learning frameworks
python3 cli.py compare frameworks/input/general/blooms_taxonomy.pdf
python3 cli.py compare frameworks/input/general/webb_dok.pdf
```

## Getting Started

1. **Download frameworks** you want to analyze
2. **Place them** in the appropriate `input/` subdirectory
3. **Run analysis** using the CLI tool
4. **Review reports** in `output/` directory
5. **Iterate** on taxonomy improvements

## Questions?

See the main taxonomy builder documentation:
- `../taxonomy_builder/README.md` - Full CLI documentation
- `../IMPLEMENTATION_COMPLETE.md` - System overview

## Contributing New Frameworks

If you find frameworks that should be in this collection:

1. Add them to the appropriate directory
2. Document the source in `sources.md`
3. Run the analysis
4. Share findings with the team

Happy analyzing! 🔍📚

