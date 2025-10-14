# ROCK Skills Analysis: Source Documents

**Purpose**: Single Source of Truth for ROCK skills analysis documentation

**Status**: Development/Active Editing

---

## About These Documents

These are the **authoritative source documents** for ROCK skills analysis. All edits, updates, and improvements should be made here. The Confluence exports (in `../confluence/`) are generated from these sources.

---

## Documents

### 1. Schema Overview (`1-schema-overview.md`)
**Lines**: 479 | **Purpose**: Technical reference

Detailed documentation of the ROCK schema structure:
- 7 CSV files (SKILLS, SKILL_AREAS, STANDARDS, STANDARD_SKILLS, STANDARD_SET_DOMAINS, STANDARD_SET_DOMAIN_GROUPS, STANDARD_SETS)
- Field-by-field descriptions with actual schema from production data
- Entity relationships and data flow
- Current metadata capabilities vs. gaps
- Examples of skill redundancy across states

**Use for**: Schema design, technical planning, database queries

---

### 2. Problem Statement (`2-problem-statement.md`)
**Lines**: 646 | **Purpose**: Comprehensive analytical documentation

Deep analysis of the compound ROCK skills problem:
- Executive summary
- Problem in detail (horizontal fragmentation + vertical granularity mismatch)
- Quantification with specific examples
- Architectural analysis
- Impact analysis by stakeholder
- Root cause analysis
- Science of Reading taxonomy comparison
- Next steps

**Use for**: Business cases, proposals, stakeholder presentations, planning

---

### 3. Visual Diagrams (`3-visual-diagrams.md`)
**Lines**: 522 | **Purpose**: Mermaid diagram source

Contains 6 Mermaid diagrams illustrating:
1. Horizontal Fragmentation - Context Clues
2. Horizontal Fragmentation - Phonemic Blending
3. Horizontal Fragmentation - Text Structure
4. Vertical Granularity Mismatch
5. Compound Effect (Both Problems)
6. Solution Architecture (Three-Layer Bridge)

**Use for**: Generating diagram images, presentations, visual references

---

## Relationship to Confluence Exports

The `../confluence/` directory contains **5 formatted documents** exported from these sources:

| Source Document | Confluence Export(s) | Notes |
|-----------------|---------------------|-------|
| `1-schema-overview.md` | `04-schema-reference.md` | Confluence formatting, table of contents macro |
| `2-problem-statement.md` | `03-comprehensive-problem-statement.md` | Confluence panels, tips, warnings |
| `3-visual-diagrams.md` | `02-visual-diagrams.md` | Diagram descriptions (images inserted in Confluence) |
| *(combined)* | `01-landing-page.md` | Navigation hub combining all sources |
| *(new)* | `05-discussion-next-steps.md` | Collaboration page (Confluence-specific) |

---

## Editing Guidelines

### When Making Changes:

1. **Edit source documents here** (not Confluence exports)
2. **Maintain consistency** across all three documents
3. **Update cross-references** if restructuring
4. **Regenerate Confluence exports** when ready to publish
5. **Document changes** in git commit messages

### Cross-References:

Source documents reference each other:
- Schema Overview → Problem Statement (for impact analysis)
- Problem Statement → Visual Diagrams (for flowcharts)
- Visual Diagrams → Schema Overview (for technical details)

When editing, ensure these references remain valid.

---

## Export Process

To generate Confluence-ready documents:

1. **Update source documents** with latest information
2. **Add Confluence-specific formatting**:
   - Table of contents macros: `{toc:minLevel=2|maxLevel=3}`
   - Info panels: `{info:title=...}`
   - Warning panels: `{warning:title=...}`
   - Tip panels: `{tip:title=...}`
   - Expand macros: `{expand:title=...}`
3. **Update hyperlinks** to Confluence URLs
4. **Add navigation** (parent page links, related pages)
5. **Save to** `../confluence/` directory

---

## Related Resources

- **ROCK Schemas**: `../rock_schemas/*.csv` - Actual production data
- **Science of Reading Taxonomy**: `../POC_science_of_reading_literacy_skills_taxonomy.csv`
- **ROCK Skills Agent**: `../../agents/work-agents/rock-skills-agent.txt` - AI consultant
- **Confluence Pages**: `../confluence/` - Published documentation

---

## Document History

| Date | Change | Files Affected |
|------|--------|----------------|
| Oct 2025 | Initial creation from schema analysis | All |
| Oct 2025 | Added vertical granularity problem | 2-problem-statement, 3-visual-diagrams |
| Oct 2025 | Updated with actual schema structure | 1-schema-overview |
| Oct 2025 | Reorganized into source/confluence structure | All |

