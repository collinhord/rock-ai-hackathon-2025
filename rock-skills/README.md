# ROCK Skills Analysis Documentation

**Purpose**: Comprehensive analysis of the ROCK Skills master skill fragmentation problem

**Team**: ROCK Skills List Advancement

**Status**: Problem Definition Complete (October 2025)

---

## 📋 Overview

This directory contains analysis and documentation of a critical architectural challenge facing the ROCK Skills List:

**The Problem**: Skills are derived from state-specific standards rather than science-based master competencies, resulting in:
- **Horizontal Fragmentation**: One science-based concept → 8-15 redundant ROCK skills (one per state)
- **Vertical Granularity Mismatch**: ROCK skills too broad for daily instruction (P&I bypass)
- **Business Lock-In**: Cannot modify ROCK due to Star Assessment dependency
- **Result**: 80-90% efficiency loss, complete ecosystem fragmentation

---

## 📁 Directory Structure

```
/docs/rock/
├── README.md (this file)
├── POC_science_of_reading_literacy_skills_taxonomy.csv (1,141 rows)
├── rock_schemas/ (7 CSV files - production ROCK data)
│
├── source/ (Single Source of Truth - Edit Here)
│   ├── README.md
│   ├── 1-schema-overview.md (479 lines)
│   ├── 2-problem-statement.md (646 lines)
│   └── 3-visual-diagrams.md (522 lines)
│
└── confluence/ (Export-Ready - Published to Confluence)
    ├── README.md
    ├── 01-landing-page.md (199 lines)
    ├── 02-visual-diagrams.md (202 lines)
    ├── 03-comprehensive-problem-statement.md (575 lines)
    ├── 04-schema-reference.md (369 lines)
    └── 05-discussion-next-steps.md (287 lines)
```

---

## 🎯 Key Documents

### For Development & Editing: `/source/`

**1. Schema Overview** (`source/1-schema-overview.md`)
- Technical reference for ROCK schema structure
- Field-by-field documentation of 7 CSV files
- Entity relationships and data flow
- Current metadata capabilities vs. gaps

**2. Problem Statement** (`source/2-problem-statement.md`)
- Comprehensive analytical documentation
- 9 major sections with quantified analysis
- Impact analysis by stakeholder
- Root cause analysis

**3. Visual Diagrams** (`source/3-visual-diagrams.md`)
- 6 Mermaid diagrams (source code)
- Illustrates horizontal, vertical, and compound problems
- Solution architecture diagram

### For Publishing: `/confluence/`

**Published to Confluence** (October 2025):
- **Parent Page**: https://illuminate.atlassian.net/wiki/spaces/CUR/pages/18543444546/
- 5 child pages formatted with Confluence macros and navigation
- See `confluence/README.md` for URLs and details

---

## 🔍 Data Sources

### ROCK Schemas (`rock_schemas/`)

Production data exported from ROCK database:

| File | Rows | Purpose |
|------|------|---------|
| `SKILLS.csv` | ~12,000 | Core ROCK skills with metadata |
| `SKILL_AREAS.csv` | 90 | Skill area categories |
| `STANDARDS.csv` | ~400,000 | State/national standards |
| `STANDARD_SKILLS.csv` | ~600,000 | Many-to-many relationships |
| `STANDARD_SET_DOMAINS.csv` | ~8,000 | Domain classifications |
| `STANDARD_SET_DOMAIN_GROUPS.csv` | ~900 | Domain group classifications |
| `STANDARD_SETS.csv` | ~300 | Standard set collections |

### Science of Reading Taxonomy

`POC_science_of_reading_literacy_skills_taxonomy.csv` (1,141 rows)

**Structure**: 6-level hierarchy
- Strand → Pillar → Domain → Skill Area → Skill Set → Skill Subset
- Evidence-based literacy competencies
- Grade-independent cognitive/linguistic constructs
- Example of what ROCK lacks (master skill taxonomy)

---

## 🚀 Quick Start

### For Developers:

```bash
# View schema documentation
cat source/1-schema-overview.md

# View problem analysis
cat source/2-problem-statement.md

# View diagram source
cat source/3-visual-diagrams.md
```

### For Stakeholders:

**Read Confluence Pages**:
1. Start with Landing Page (TL;DR + navigation)
2. Visual Diagrams (see the problem graphically)
3. Comprehensive Problem Statement (detailed analysis)
4. Discussion & Next Steps (collaboration)

### For Technical Teams:

1. Review `source/1-schema-overview.md` for schema structure
2. Examine actual data in `rock_schemas/*.csv`
3. Query ROCK database using field documentation
4. See `source/2-problem-statement.md` Section 3 for architectural analysis

---

## 🔧 Workflow

### Making Changes:

1. **Edit source documents** in `source/` directory
2. **Maintain consistency** across all documents
3. **Commit changes** to git
4. **Regenerate Confluence exports** when ready to publish
5. **Update Confluence** with new content

### Publishing to Confluence:

1. Edit `source/` documents
2. Apply Confluence-specific formatting (macros, panels)
3. Update hyperlinks to Confluence URLs
4. Save to `confluence/` directory
5. Copy-paste or import to Confluence
6. Publish

**See**: `confluence/README.md` for detailed publishing instructions

---

## 📊 Key Findings

### Quantified Impact:

| Metric | Value |
|--------|-------|
| **Conceptual redundancy** | 60-75% |
| **Skills per master concept** | 8-15 average |
| **Efficiency loss (compound)** | 80-90% |
| **P&I decomposition ratio** | 5-10 objectives per ROCK skill |

### Affected Stakeholders:

- **Curriculum Developers**: Cannot discover all skills teaching a concept
- **Product Teams**: Adaptive features blocked, P&I builds parallel infrastructure
- **Researchers**: Cannot aggregate by master constructs
- **Educators**: Search incomplete, unclear skill relationships

---

## 🎓 Related Resources

### ROCK Skills Agent

**Location**: `../../agents/work-agents/rock-skills-agent.txt`

AI expert consultant with dual capabilities:
- Programmatic schema analysis (identify redundancy patterns)
- Expert consultation (explain problems, guide discussions)

**Use for**: Schema queries, problem explanation, stakeholder communication

### Master Agent Guide

**Location**: `../../agents/master-guide.txt`

Overview of all hackathon analysis tools and agents.

---

## 📖 Next Steps

### Immediate Actions:
1. **Validate problem quantification** - Run queries on production schemas
2. **Engage stakeholders** - Share analysis with leadership
3. **Assess Science of Reading integration** - Evaluate taxonomy as solution bridge
4. **Pilot mapping** - Map 50-100 skills to Science of Reading taxonomy
5. **Design dual-track architecture** - Plan without modifying ROCK

### Future Exploration:
1. **Pilot mapping** (50-skill proof of concept)
2. **Schema design** (taxonomic metadata layer)
3. **Tooling** (AI/NLP for semi-automated mapping)
4. **Governance** (taxonomy maintenance process)

**See**: `confluence/05-discussion-next-steps.md` for detailed action planning

---

## 📝 Document History

| Date | Change | Impact |
|------|--------|--------|
| Oct 2025 | Initial schema analysis and documentation | Created source documents |
| Oct 2025 | Added vertical granularity problem (P&I) | Expanded to compound problem |
| Oct 2025 | Updated with actual schema structure from CSVs | Accurate field documentation |
| Oct 2025 | Generated Confluence exports | Published to Confluence |
| Oct 2025 | Reorganized into source/confluence structure | Clean separation of concerns |

---

## 👥 Team

**ROCK Skills List Advancement Team**
- Document Owner: [Your Name]
- Last Updated: October 2025
- Confluence Space: CUR (Curriculum)

---

## 🔗 External Links

- **Confluence Parent Page**: https://illuminate.atlassian.net/wiki/spaces/CUR/pages/18543444546/
- **GitHub Repository**: [Current repository]
- **ROCK Skills Agent**: Available in agents/work-agents/

---

For questions or contributions, see `confluence/05-discussion-next-steps.md` or contact the Skills List Advancement Team.

