# Testing Checklist - Taxonomy Viewer & Base Skills Demo

**Complete this checklist 15 minutes before your demo to ensure everything works smoothly.**

---

## Pre-Demo Setup (5 minutes)

### Environment Setup

- [ ] Navigate to project directory:
  ```bash
  cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/poc
  ```

- [ ] Check that all required data files exist:
  ```bash
  ls ../taxonomy/base_skills/base_skills_summary.json
  ls ../analysis/outputs/filtered_enhanced_metadata/skill_metadata_enhanced_*.csv
  ls ../analysis/master-concepts.csv
  ls ../analysis/skill_master_concept_mapping.csv
  ```

- [ ] Start the Streamlit app:
  ```bash
  streamlit run skill_bridge_app.py
  ```

- [ ] Verify app opens in browser (should auto-open to http://localhost:8501)

---

## Page-by-Page Testing

### 1. Executive View (Default Landing Page)

**Expected Load Time:** < 3 seconds

- [ ] Page loads without errors
- [ ] Quick stats in sidebar display:
  - Total ROCK Skills: [number]
  - Master Concepts: [number]
  - Redundancy Ratio: [X.X]x
- [ ] "The Problem" section displays with metrics
- [ ] Phoneme blending visualization renders correctly
- [ ] "The Solution" section displays with three columns
- [ ] Before/After comparison table renders
- [ ] Stakeholder impact matrix displays

**If Issues:**
- Check console for error messages
- Verify data_loader.py has no import errors
- Check that all CSV files are accessible

---

### 2. Three-Level Deep Dive

**Expected Load Time:** < 3 seconds per tab

#### MACRO Tab

- [ ] Tab switches successfully
- [ ] Framework convergence dashboard loads (or shows "not available" message)
- [ ] Taxonomy browser displays SoR hierarchy
- [ ] Strand selector works
- [ ] Hierarchy counts display correctly
- [ ] Semantic similarity network section displays

#### MID Tab

- [ ] Tab switches successfully
- [ ] Redundancy overview metrics display
- [ ] Interactive grooming interface loads (or shows "not available" message)
- [ ] Variant cluster explorer displays
- [ ] Equivalence groups statistics show

#### MICRO Tab

- [ ] Tab switches successfully
- [ ] Metadata dashboard loads
- [ ] Metadata coverage table displays
- [ ] Metadata enrichment pipeline info shows
- [ ] Skill quality inspector search box works
- [ ] Search returns results when typing

**If Issues:**
- Some sections may show "not available" if validation suite hasn't run—this is expected
- Key sections are MACRO taxonomy browser and MICRO metadata dashboard

---

### 3. Base Skills Explorer ⭐ **CRITICAL FOR DEMO**

**Expected Load Time:** < 4 seconds

#### Overview Metrics

- [ ] Page loads successfully
- [ ] Four metrics display at top:
  - Total Base Skills: 59
  - Total ROCK Skills Collapsed: ~337
  - Average Redundancy Ratio: ~5.7x
  - Taxonomy Coverage: [percentage]
- [ ] Callout box with explanation displays

#### Visualizations

- [ ] Bar chart "Top 15 Base Skills by ROCK Skill Count" renders
- [ ] Chart is interactive (hover shows details)
- [ ] Pie chart "By Cognitive Category" renders
- [ ] Histogram "Redundancy Distribution" renders

#### Interactive Browser

- [ ] Search box works (try typing "phoneme")
- [ ] Cognitive category filter populates with options
- [ ] Min ROCK Skills number input works
- [ ] Filtered results display correctly
- [ ] Expandable base skill cards work:
  - [ ] Base skill name and description show
  - [ ] Metrics display (ROCK skills count, confidence)
  - [ ] Sample ROCK skills list (if available)

#### Specifications Showcase

- [ ] Section displays below browser
- [ ] Example skills load (3 skills with specifications)
- [ ] Expandable skill cards show:
  - [ ] Structural specifications (actions, targets, qualifiers)
  - [ ] Educational specifications (text type, cognitive demand, etc.)
- [ ] "Key Insight" callout box displays
- [ ] Specification Coverage Statistics table renders

**Critical Test Flows:**

1. **Search for "phoneme"** → Should return phoneme-related base skills
2. **Expand any base skill** → Should show details and sample ROCK skills
3. **Scroll to specifications** → Should show example skills with metadata

**If Issues:**
- If "Base skills data not loaded" warning appears, check `/taxonomy/base_skills/` directory
- If specifications section says "not available", specifications data hasn't been generated yet—this is OK, the section will show instructions instead

---

### 4. Demo Scenarios ⭐ **CRITICAL FOR DEMO**

**Expected Load Time:** < 2 seconds

#### Page Load

- [ ] Page loads successfully
- [ ] Welcome text displays
- [ ] Scenario selector dropdown populates with 3 options

#### Scenario A: Phonological Awareness for K-2

- [ ] Select scenario from dropdown
- [ ] Use case description displays
- [ ] Before/After columns render
- [ ] "Try It Live" button displays
- [ ] **Click button** → Should show filtered results
- [ ] Results count displays ("Found X skills")
- [ ] Results table renders with columns

#### Scenario B: Analysis-Level Comprehension

- [ ] Select scenario from dropdown
- [ ] Description displays
- [ ] Before/After comparison shows
- [ ] **Click "Run Scenario B" button**
- [ ] Results display with filtered skills

#### Scenario C: Cross-State Discovery

- [ ] Select scenario from dropdown
- [ ] Example base skill info box displays
- [ ] Impact bullets show
- [ ] Efficiency gain metric displays

**Critical Test Flows:**

1. **Run Scenario A** → Should return 10-20 skills (K-2 phonological awareness)
2. **Run Scenario B** → Should return 5-15 skills (analysis-level fiction)
3. **View Scenario C** → Should show base skill with high ROCK skill count

**If Issues:**
- If "Specifications data not available" appears, scenarios won't run—you'll need to generate specifications first OR demo without live scenarios (show static example in Scenario C)

---

### 5. Interactive Explorer

**Expected Load Time:** < 3 seconds

#### Concept Browser Tab

- [ ] Tab loads successfully
- [ ] Search box displays
- [ ] Search for "phoneme" returns results
- [ ] Expandable concept cards work
- [ ] Mapped ROCK skills display in cards
- [ ] Popular concepts table displays when no search

#### Skill Search & Inspector Tab ⭐ **CRITICAL FOR DEMO**

- [ ] Tab switches successfully
- [ ] "Why Taxonomy-Powered Discovery?" expander works
- [ ] Filter interface displays with multiple rows:
  - [ ] Row 1: Search box, Taxonomy Strand, Taxonomy Pillar
  - [ ] Row 2 (if specs available): Text Type, Cognitive Demand, Task Complexity, Grade Band
  - [ ] Row 3: State/Authority, Specific Grade
- [ ] Success message shows skill count being filtered
- [ ] Apply filters and verify results update dynamically
- [ ] Results section shows:
  - [ ] "Results: X skills found" header
  - [ ] Three metrics: Filtered Results, From Total, Noise Reduction
  - [ ] Results table with skills
  - [ ] Download CSV button

**Critical Test Flows:**

1. **Select Grade Band: K-2, Type "phoneme" in search** → Should filter to K-2 phoneme skills
2. **Select Cognitive Demand: comprehension, Text Type: fictional** → Should show comprehension skills for fiction
3. **Download CSV** → Should trigger download

#### Taxonomy Navigator Tab

- [ ] Tab loads
- [ ] Strand selector populates
- [ ] Select a strand → Pillars display
- [ ] Select a pillar → Domains display
- [ ] Hierarchy drill-down works

**If Issues:**
- If no filters appear in Skill Search tab, check that specifications or skill_mapping data loaded successfully
- If "No skill data available" warning, verify data files exist

---

### 6. Validation Dashboard

**Expected Load Time:** < 3 seconds

- [ ] Page loads
- [ ] If validation results not found, instructional message displays
- [ ] If validation results exist:
  - [ ] Master validation report displays
  - [ ] Three tabs render: Semantic Validation, Framework Convergence, Summary Metrics
  - [ ] Charts and tables display in each tab

**Note:** This page is optional for demo—OK if validation results don't exist

---

### 7. Technical Reference

**Expected Load Time:** < 2 seconds

- [ ] Page loads
- [ ] Section selector dropdown works
- [ ] Each section displays markdown content correctly:
  - [ ] Overview
  - [ ] Schema Reference
  - [ ] Script Reference
  - [ ] Validation Suite
  - [ ] API Examples
  - [ ] Contributing

---

## Performance Testing

### Load Time Benchmarks

**Target:** All pages should load in < 5 seconds

Test each page and record load time:

- [ ] Executive View: _____ seconds
- [ ] Three-Level Deep Dive (MACRO): _____ seconds
- [ ] Base Skills Explorer: _____ seconds
- [ ] Demo Scenarios: _____ seconds
- [ ] Interactive Explorer: _____ seconds
- [ ] Validation Dashboard: _____ seconds
- [ ] Technical Reference: _____ seconds

**If > 5 seconds:** Check that `@st.cache_data` decorators are working in data_loader.py

### Data Loading

- [ ] First page load caches data (may be slower)
- [ ] Subsequent page navigation is fast (uses cached data)
- [ ] No console errors about failed data loads
- [ ] All visualizations render without lag

---

## UI/UX Polish

### Visual Consistency

- [ ] All headers use consistent styling
- [ ] Metrics cards display properly (not cut off)
- [ ] Visualizations fit within container width
- [ ] Tables are readable (not too wide or narrow)
- [ ] Expandable sections work smoothly
- [ ] Colors are consistent (blues for base skills, etc.)

### Responsive Design

- [ ] App looks good at default browser width
- [ ] Sidebar is fully visible
- [ ] No horizontal scrolling required
- [ ] Tables don't overflow containers

### Error Handling

- [ ] Graceful error messages display when data missing
- [ ] No raw error tracebacks shown to user
- [ ] Helpful instructions provided when data not available

---

## Demo-Specific Testing

### Key Demo Flow (15-minute version)

**Run through this exact flow:**

1. [ ] Start on Executive View
   - Show problem metrics
   - Show phoneme blending example
   - Explain solution

2. [ ] Navigate to Base Skills Explorer
   - Show overview metrics (redundancy ratio)
   - Show bar chart visualization
   - Search for "phoneme"
   - Expand one base skill
   - Scroll to specifications showcase
   - Expand one specification example

3. [ ] Navigate to Demo Scenarios
   - Select Scenario A
   - Run Scenario A (phonological awareness K-2)
   - Show results count and table
   - Quickly show Scenario C (cross-state discovery)

4. [ ] Navigate to Interactive Explorer → Skill Search tab
   - Show before/after expander
   - Apply filters: Grade Band K-2, search "phoneme"
   - Show filtered results and metrics
   - Optionally add Cognitive Demand filter
   - Show download CSV button

5. [ ] Return to Executive View for closing

**Time this flow:** Target 12-15 minutes

Total time for demo practice run: _____ minutes

---

## Browser Compatibility

Test in your presentation browser:

- [ ] Chrome: Works
- [ ] Firefox: Works
- [ ] Safari: Works
- [ ] Edge: Works

---

## Backup Planning

### If App Crashes During Demo

**Backup Options:**

1. [ ] Screenshots folder prepared with key screens
2. [ ] Demo script (DEMO_SCRIPT.md) available for narration
3. [ ] Alternative: Show Jupyter notebook (`analysis/hackathon_demo.ipynb`)
4. [ ] Alternative: Show raw data files and explain pipeline

### Practice Narration

- [ ] Practice demo script out loud at least once
- [ ] Memorize key talking points
- [ ] Prepare for Q&A (see DEMO_SCRIPT.md for anticipated questions)
- [ ] Have backup stats ready:
  - 59 base skills
  - 337 ROCK skills collapsed
  - 5.7x average redundancy ratio
  - 90%+ extraction accuracy
  - $9-12 cost for 3,000 skills

---

## Final Pre-Demo Checklist (1 minute before)

- [ ] App is running at http://localhost:8501
- [ ] Browser is full-screen (no distracting tabs)
- [ ] Demo script is open in separate window
- [ ] Phone on silent
- [ ] Clock visible to track time
- [ ] Water available
- [ ] Deep breath—you've got this! 🚀

---

## Post-Demo Debrief

**After demo, record:**

- What worked well: ___________________________
- What had issues: ___________________________
- Questions asked: ___________________________
- Features that resonated: ___________________________
- Suggested improvements: ___________________________

---

## Troubleshooting Guide

### "Base skills data not loaded"

**Fix:** Check that `/taxonomy/base_skills/base_skills_summary.json` exists
```bash
ls ../taxonomy/base_skills/base_skills_summary.json
```

### "Specifications data not available"

**Fix:** Run metadata extraction (or demo without live scenarios)
```bash
cd ../analysis/scripts
python3 enhanced_metadata_extractor.py
```

### Charts not rendering

**Fix:** Check that plotly is installed
```bash
pip install plotly
```

### "Module not found" errors

**Fix:** Install missing dependencies
```bash
cd ..
pip install -r requirements.txt
```

### App won't start

**Fix:** Check for syntax errors
```bash
python3 -m py_compile skill_bridge_app.py
```

### Slow performance

**Fix:** Clear Streamlit cache and restart
```bash
streamlit cache clear
streamlit run skill_bridge_app.py
```

---

**Good luck! 🎯**

