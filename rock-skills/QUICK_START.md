# ROCK Skills Bridge - Quick Start Guide

**Get up and running in 5 minutes**

---

## Option 1: Run the Interactive Demo (Recommended)

### 1. Install dependencies
```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/poc
pip install -r requirements.txt
```

### 2. Launch the app
```bash
streamlit run skill_bridge_app.py
```

### 3. Open browser
The app opens automatically at `http://localhost:8501`

### 4. Explore features
- 🏠 **Home**: See problem and solution overview
- 🔍 **Master Concept Browser**: Search "blend" or "context" - the "wow" demo
- 🔎 **Skill Inspector**: Search ROCK skills, see taxonomy mappings
- 📊 **Redundancy Visualizer**: Charts proving fragmentation
- 📚 **Taxonomy Browser**: Explore Science of Reading hierarchy

**Demo Time**: 5 minutes using `/hackathon/demo-script.md`

---

## Option 2: Run the Analysis Notebook

### 1. Install dependencies
```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/analysis
pip install -r requirements.txt
```

### 2. Launch Jupyter
```bash
jupyter notebook redundancy-analysis.ipynb
```

### 3. Run all cells
- Kernel → Restart & Run All
- Wait 2-3 minutes for analysis to complete

### 4. Review outputs
- `fragmentation-examples.csv` - 100+ skill variants
- `fragmented_skill_patterns.csv` - All patterns
- PNG charts in `/analysis/` directory
- Summary report printed in notebook

**Analysis Time**: 3-5 minutes to run

---

## Option 3: Review Presentation Materials

### For Leadership
Read: `/hackathon/executive-summary.md`
- 1-page problem + solution overview
- Quantified results
- Next steps and budget

### For Demo Preparation
Read: `/hackathon/demo-script.md`
- 5-minute walkthrough script
- Key talking points
- Backup Q&A answers

### For Planning
Read: `/hackathon/next-steps.md`
- Pilot phase plan (3-6 months)
- Full implementation roadmap
- Team structure and budget

---

## Option 4: Explore the Data

### View Pilot Mappings
```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/analysis
open skill-taxonomy-mapping.csv
```

50 ROCK skills mapped to Science of Reading taxonomy

### View Master Concepts
```bash
open master-concepts.csv
```

15 master concepts with skill counts and redundancy metrics

### Check ROCK Schemas
```bash
cd ../rock_schemas
ls -lh *.csv
head -n 5 SKILLS.csv
```

8,355 ROCK skills and relationships to standards

---

## What You'll See

### In the Interactive Demo:
- **Master Concept Browser**: Type "blend" → see 12 phoneme blending skills across 8 states
- **Redundancy Visualizer**: Bar charts showing 15+ skills for "Main Idea Identification"
- **Skill Inspector**: Search skills, see which have taxonomy mappings

### In the Analysis:
- **6.8x average redundancy** (6-8 skills per master concept)
- **60-75% conceptual redundancy** across ROCK inventory
- **15 concrete examples** with 100+ skill variants

### In the Presentation:
- Clear problem articulation with quantitative proof
- Working POC demonstrating solution value
- Roadmap from pilot to production

---

## Common Tasks

### Customize the demo
Edit `/poc/skill_bridge_app.py` to change:
- Colors and styling (CSS in lines 20-40)
- Metrics displayed (lines 100-120)
- Chart types (Plotly code in redundancy visualizer)

### Add more mappings
Edit `/analysis/skill-taxonomy-mapping.csv`:
- Add rows with SKILL_ID, SKILL_NAME, SOR taxonomy path
- Reload the Streamlit app (it caches data)

### Re-run analysis with different filters
Edit `/analysis/redundancy-analysis.ipynb`:
- Change content area filter (line in "Load Skills" cell)
- Adjust redundancy thresholds (3+ skills, 3+ authorities)
- Add new keywords for example extraction

---

## Troubleshooting

### Streamlit won't start
```bash
# Check if already running
ps aux | grep streamlit
# Kill if needed
pkill -f streamlit
# Restart
streamlit run skill_bridge_app.py
```

### Jupyter kernel issues
```bash
python -m ipykernel install --user --name rock-skills
# Then select "rock-skills" kernel in Jupyter
```

### Missing dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Data not loading in app
- Check file paths in `/poc/data_loader.py`
- Confirm CSVs exist in `/rock_schemas/` and `/analysis/`
- Clear Streamlit cache: Menu → Clear Cache

---

## For Presentation

### Before Demo
- [ ] Test app loads completely
- [ ] Practice 5-minute script
- [ ] Take backup screenshots
- [ ] Close distracting apps

### During Demo
1. Start at Home page - show metrics
2. Navigate to Master Concept Browser
3. Search "blend" - expand Phoneme Blending
4. Show Redundancy Visualizer charts
5. Close with next steps

### After Demo
- Share executive summary
- Schedule follow-up
- Gather feedback

---

## Key Files at a Glance

```
rock-skills/
├── poc/skill_bridge_app.py          # Run this for demo ⭐
├── analysis/redundancy-analysis.ipynb  # Run this for analysis
├── hackathon/demo-script.md         # Read this before demo
├── hackathon/executive-summary.md   # Share this with leadership
├── README.md                        # Complete project overview
└── IMPLEMENTATION_SUMMARY.md        # Everything accomplished
```

---

## Next Steps

1. **Test the demo**: Run Streamlit app, explore all pages
2. **Read demo script**: Familiarize with 5-minute walkthrough
3. **Review executive summary**: Understand value proposition
4. **Schedule presentation**: Book time with stakeholders

---

**Need help?** See `/poc/README.md` for detailed setup or `/rock-skills/README.md` for complete documentation.

**Ready to demo?** Follow `/hackathon/demo-script.md` for step-by-step walkthrough.

---

**Built in Renaissance Learning AI Hackathon 2025**

