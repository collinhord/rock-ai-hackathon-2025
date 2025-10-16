# Framework Analysis - Quick Start Guide

## 📁 Directory Structure

```
frameworks/
├── README.md              ← Full documentation
├── QUICK_START.md         ← This file
├── .gitignore             ← Prevents committing large PDFs
│
├── input/                 ← PUT YOUR FRAMEWORKS HERE
│   ├── ela/              ← English Language Arts frameworks
│   │   └── sources.md    ← Document your sources
│   ├── math/             ← Mathematics frameworks
│   │   └── sources.md
│   ├── science/          ← Science frameworks
│   │   └── sources.md
│   └── general/          ← Cross-disciplinary frameworks
│       └── sources.md
│
└── output/               ← Analysis reports saved here
```

## 🚀 Quick Workflow

### 1. Add a Framework

```bash
# Copy your PDF to the appropriate directory
cp ~/Downloads/scarborough_rope.pdf frameworks/input/ela/
```

### 2. Document It (Optional but Recommended)

Edit `frameworks/input/ela/sources.md` to add:
```markdown
### Scarborough's Reading Rope
- **Author:** Hollis Scarborough
- **Year:** 2001
- **Filename:** scarborough_rope.pdf
- **Notes:** Core reading comprehension framework
```

### 3. Analyze It

```bash
cd taxonomy_builder

# Analyze single framework
python3 cli.py compare ../frameworks/input/ela/scarborough_rope.pdf \
    --output ../frameworks/output/scarborough_analysis.md
```

### 4. Review Results

```bash
# View the analysis report
cat ../frameworks/output/scarborough_analysis.md

# Or open in your editor
code ../frameworks/output/scarborough_analysis.md
```

## 📊 What You'll Get

The analysis report includes:

1. **Extracted Taxonomy** - Structure from the framework
2. **Alignment Score** - How well it matches our taxonomy (0-100)
3. **Missing from Ours** - Concepts we should consider adding
4. **Missing from Framework** - Our unique concepts
5. **Recommendations** - Specific actionable suggestions

## 🔄 Batch Processing

Process all frameworks in a directory:

```bash
# Analyze all ELA frameworks
for file in ../frameworks/input/ela/*.pdf; do
    basename=$(basename "$file" .pdf)
    echo "Analyzing: $basename"
    python3 cli.py compare "$file" \
        --output "../frameworks/output/${basename}_analysis.md"
done
```

## 📚 Recommended Starting Frameworks

### For ELA:
1. **Scarborough's Reading Rope** - Core reading framework
2. **Simple View of Reading** - Foundational model
3. **National Reading Panel Report** - Evidence base

### For Math:
1. **Common Core Math Standards**
2. **NCTM Standards**

### For Cross-Disciplinary:
1. **Bloom's Taxonomy**
2. **Webb's Depth of Knowledge**

## 💰 Cost Estimate

- Small framework (10-20 pages): ~$0.50-1.00
- Medium framework (50-100 pages): ~$1.00-3.00
- Large framework (200+ pages): ~$3.00-10.00

## ⚠️ Important Notes

- PDF files are **NOT committed** to git (see `.gitignore`)
- Analysis outputs **ARE committed** (markdown/JSON reports)
- Document your sources in `sources.md` files
- Use descriptive filenames for frameworks

## 🆘 Troubleshooting

**"boto3 not available"** → Install: `pip install boto3`  
**"PyPDF2 not available"** → Install: `pip install PyPDF2`  
**AWS credentials error** → Run: `aws configure`

## 📖 More Information

- Full documentation: `README.md`
- Taxonomy builder docs: `../taxonomy_builder/README.md`
- Implementation summary: `../IMPLEMENTATION_COMPLETE.md`

---

**Ready to start?** Add your first framework to `input/ela/` and run the analyze command! 🎯

