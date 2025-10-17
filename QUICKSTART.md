# ROCK AI Hackathon 2025 - Quick Start Guide

**Get up and running in 5-10 minutes**

---

## 🎯 Choose Your Path

### Path 1: Explore the Demo UI (Recommended for First-Time Users)

**Best for**: Understanding the system, exploring features, stakeholder demos

```bash
cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025
pip install -r requirements.txt
cd rock-skills/poc
streamlit run skill_bridge_app.py
```

**Opens at**: `http://localhost:8501`

**Key Features**:
- 🏠 Home: Problem and solution overview
- 🔍 Master Concept Browser: Search skills, see groupings
- 📊 Redundancy Visualizer: Fragmentation charts
- 📚 Taxonomy Explorer: Science of Reading hierarchy
- ⚙️ Redundancy Grooming: Conflict resolution (advanced)

**Time**: 5 minutes | **Cost**: Free

---

### Path 2: Check System Status

**Best for**: Quick health check, seeing what's already processed

```bash
cd rock-skills
./scripts/status.sh
```

**Shows**:
- Database status and skill counts
- Pending conflicts
- MECE score
- Suggested next actions

**Time**: <1 minute | **Cost**: Free

---

### Path 3: Run First-Time Setup & Test

**Best for**: Developers setting up for the first time

```bash
cd rock-skills/analysis/pipelines
./quick_start.sh
```

**What it does**:
- Installs Python dependencies
- Downloads spaCy models
- Runs POC test on 20 sample skills
- Validates pipeline works

**Time**: 5-10 minutes | **Cost**: Free (no LLM)

---

### Path 4: Process Full Taxonomy

**Best for**: Generating complete base skill taxonomy from ROCK skills

```bash
cd rock-skills
./scripts/refresh_taxonomy.sh          # Full with LLM
# OR
./scripts/refresh_taxonomy.sh --no-llm # Faster, lower quality
```

**What it does**:
1. Extracts base skills from ROCK skills
2. Extracts specifications
3. Validates MECE and detects conflicts
4. Generates reports

**Time**: 3-5 hours (with LLM) or 1-2 hours (without)  
**Cost**: $40-60 (with LLM) or Free (without)

---

## 📁 Project Structure

```
rock-ai-hackathon-2025/
├── agents/                     # 10 AI agent prompts (hackathon deliverable)
├── rock-skills/               # Main educational taxonomy system
│   ├── analysis/             # Data pipelines and processing
│   ├── poc/                  # Streamlit UI application
│   ├── frameworks/           # Framework analysis tools
│   ├── rock_data/            # Source data (excluded from git)
│   ├── docs/                 # All documentation
│   └── scripts/              # Workflow orchestration scripts
├── requirements.txt          # All dependencies
├── DATA_README.md            # How to obtain source data
└── QUICKSTART.md             # This file
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `DATA_README.md` | **How to get ROCK source data** |
| `rock-skills/README.md` | Main system overview |
| `rock-skills/docs/architecture/base-skill-architecture.md` | Complete architecture |
| `rock-skills/scripts/status.sh` | System health check |
| `rock-skills/test_base_skill_system.sh` | End-to-end test |
| `agents/README.md` | Agent system documentation |

---

## 🎪 Hackathon Deliverables

### Agents (10 Specialized Prompts)

```bash
cd agents
ls work-agents/     # 6 professional agents
ls creative-agents/ # 4 creative agents
cat master-guide.txt # Meta-agent for orchestration
```

**Agents include**: ROCK Skills Agent, Metadata Expert, Standards Alignment, Recipe Chef, Comedy Writer, Shakespeare Response, and more.

### ROCK Skills Analysis

```bash
cd rock-skills
# View analysis outputs
ls analysis/outputs/
# View documentation
ls docs/
```

**Analysis includes**: Redundancy detection, master concepts, metadata enrichment, framework alignment.

---

## 🛠️ Common Workflows

### Workflow 1: View System Status
```bash
cd rock-skills
./scripts/status.sh
```

### Workflow 2: Launch UI
```bash
cd rock-skills/poc
streamlit run skill_bridge_app.py
```

### Workflow 3: Add New Skills (Incremental Update)
```bash
cd rock-skills
./scripts/update_taxonomy.sh --new-skills data/new_skills.csv
```

### Workflow 4: Resolve Conflicts
```bash
# Step 1: Review in UI
cd rock-skills/poc
streamlit run skill_bridge_app.py  # Navigate to "Redundancy Grooming"

# Step 2: Apply decisions
cd ../scripts
./apply_decisions.sh
```

### Workflow 5: Validate Taxonomy Quality
```bash
cd rock-skills
./scripts/validate_taxonomy.sh
```

### Workflow 6: Run Full Refresh
```bash
cd rock-skills
./scripts/refresh_taxonomy.sh --no-llm  # Faster, free
# OR with LLM for higher quality
./scripts/refresh_taxonomy.sh
```

---

## 📊 Data Requirements

⚠️ **Important**: The system requires ROCK production data files that are excluded from git.

**See**: `DATA_README.md` for complete instructions on:
- Which files are needed (7 CSVs)
- How to obtain them (for Renaissance employees)
- Where to place them (`rock-skills/rock_data/`)
- How to verify data integrity

**Alternative**: Use existing analysis outputs in `rock-skills/analysis/outputs/` to explore the UI without source data.

---

## 🧪 Testing

### Quick Test (No LLM, Free)
```bash
cd rock-skills
./test_base_skill_system.sh
```

Tests pipeline on 50 sample skills, validates outputs, generates reports.

### Full Validation
```bash
cd rock-skills
./scripts/validate_taxonomy.sh
```

Comprehensive quality checks: MECE score, coverage, conflicts, data integrity.

---

## 🐛 Troubleshooting

### Issue: "spaCy model not found"
```bash
python3 -m spacy download en_core_web_lg
```

### Issue: "ROCK data files not found"
See `DATA_README.md` for data acquisition instructions.

### Issue: "Import errors"
```bash
pip install -r requirements.txt
```

### Issue: "AWS Bedrock credentials"
LLM features require AWS credentials. For free operation, use `--no-llm` flags.

---

## 💰 Cost Estimates

| Task | Time | Cost |
|------|------|------|
| POC Test | 5-10 min | Free |
| UI Exploration | 5-30 min | Free |
| Full Refresh (no LLM) | 1-2 hrs | Free |
| Full Refresh (with LLM) | 3-5 hrs | $40-60 |
| Incremental Update | 30-60 min | $5-10 |
| Validation | 10-15 min | Free |

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| `QUICKSTART.md` | This file - get started fast |
| `DATA_README.md` | Data acquisition instructions |
| `rock-skills/README.md` | Main system documentation |
| `rock-skills/docs/README.md` | Documentation index |
| `rock-skills/docs/architecture/` | System design and architecture |
| `rock-skills/docs/guides/` | Workflow guides and references |
| `agents/README.md` | Agent system documentation |

---

## 🎯 Success Metrics

After setup, you should be able to:
- ✅ Launch the Streamlit UI
- ✅ View system status with `./scripts/status.sh`
- ✅ Run test pipeline successfully
- ✅ Navigate all UI features
- ✅ Understand the problem and solution

---

## 🚀 Next Steps

1. **Choose a path above** and complete setup
2. **Explore the UI** to understand the system
3. **Read architecture docs** for deeper understanding
4. **Run workflows** relevant to your needs
5. **Review agent prompts** in `agents/` directory

---

## 📞 Getting Help

- **Documentation**: Check `rock-skills/docs/` directory
- **Architecture**: Read `rock-skills/docs/architecture/base-skill-architecture.md`
- **Data Issues**: See `DATA_README.md`
- **Scripts**: Run `./scripts/status.sh` for guidance

---

**Ready to start? Pick Path 1 (Demo UI) for the fastest introduction!**

