# Project 2: Skill Redundancy and Relationships - Project Goals

**Owner**: ROCK Skills Analysis Team  
**Status**: In Development  
**Last Updated**: October 17, 2025

## Mission Statement

Identify redundant and related ROCK skills across states and grade levels, create master concepts to group variants, and establish relationship types (duplicate, variant, prerequisite) to reduce apparent skill count by 60-75% and enable cross-state content scaling.

## Business Value

**Problem**: The same learning concept appears 6-8 times across state standards with no metadata connecting them, causing:
- Content duplication (70-80% redundancy)
- Invisible cross-state content (teacher in Texas can't find Illinois content)
- Inefficient skill discovery (search 8,000 skills instead of 1,200 unique concepts)
- Wasted curriculum development effort

**Impact**: 
- 60-75% reduction in apparent skill count (8,354 → ~2,500 master concepts)
- Cross-state content visibility and reuse
- 80-90% faster skill discovery
- Foundation for learning progressions and prerequisite chains

**Users**: 
- Curriculum designers seeking cross-state content
- Content platform (eliminate duplication)
- Product teams building adaptive learning (need skill relationships)
- Research teams studying skill progressions

## Objectives

### Primary Objectives (Must Have)

1. **Detect redundant skills** using semantic similarity and clustering
   - Cross-state variants (same skill, different states)
   - Grade-level progressions (same skill, increasing complexity)
   - True duplicates (identical skills)
   - Success criteria: Identify 60-75% redundancy

2. **Generate master concepts** to group related skills
   - One master concept per unique learning objective
   - Link 4-8 variant skills to each master concept
   - Include taxonomy mapping (Science of Reading)
   - Success criteria: Create ~2,500 master concepts from 8,354 skills

3. **Classify relationship types** between skills
   - Duplicate: Identical or near-identical
   - Variant: Same concept, different context/complexity
   - Prerequisite: Skill A required before Skill B
   - Related: Share common elements but distinct
   - Success criteria: Classify 80% of skill pairs with high confidence

### Secondary Objectives (Nice to Have)

1. Learning progression chains (K → 12 for each concept)
2. Cross-domain relationships (Math ↔ ELA)
3. Confidence scoring for relationships
4. Human-in-the-loop validation interface

## Scope

### In Scope

- Redundancy detection across all 8,354 ROCK skills
- Master concept generation (~2,500 concepts)
- Relationship classification (duplicate, variant, prerequisite)
- Semantic similarity using embeddings
- Clustering algorithms (hierarchical, adaptive)
- Integration with Project 1 metadata (optional enrichment)

### Out of Scope (Explicitly)

- Modifying ROCK database (read-only access)
- Deleting redundant skills (preserve for Star Assessment)
- Content alignment (separate system)
- Real-time similarity API (batch only)
- Skills outside core content areas (ELA, Math)

## Technical Approach

### Architecture

**Multi-Stage Pipeline**:

1. **Semantic Similarity** (Embeddings)
   - Generate embeddings for skill descriptions
   - Compute cosine similarity matrix
   - Identify candidate groups (similarity > 0.75)
   - Technology: sentence-transformers, scikit-learn

2. **Variant Classification** (Rule-Based + ML)
   - **State A**: Cross-state variants (same skill, different authorities)
   - **State B**: Grade progressions (same skill, different grades)
   - **Unique**: No variants found
   - Uses: string similarity, metadata comparison, LLM validation

3. **Master Concept Generation** (Hybrid)
   - Group State A variants → one master concept per group
   - Extract concept name from taxonomy (Skill Area or Skill Subset)
   - Calculate metrics: skill_count, authority_count, grade_range
   - Link State B skills via taxonomy similarity

4. **Relationship Classification** (Graph Analysis)
   - Build skill relationship graph
   - Classify edges: duplicate, variant, prerequisite, related
   - Use grade level, cognitive level, action verbs as signals

### Data Flow

```
ROCK Skills + Project 1 Metadata
    ↓
Embedding Generation (sentence-transformers)
    ↓
Semantic Similarity Matrix
    ↓
Variant Classification (State A, State B, Unique)
    ↓
Master Concept Generation
    ↓
Relationship Classification
    ↓
Outputs:
- master_concepts.csv
- skill_master_concept_mapping.csv
- skill_relationships.csv
```

### Key Technologies

- **Python 3.9+**: Core language
- **sentence-transformers**: Embedding generation
- **scikit-learn**: Clustering, similarity
- **NetworkX**: Graph analysis for relationships
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

## Dependencies

### Upstream Dependencies (Inputs)

- **Snowflake ROCK_DB.SKILLS**: Source data (8,354 skills)
- **Project 1 metadata** (optional): Enriches similarity with structured data
- **Science of Reading taxonomy**: Provides master concept names
- **Shared data access layer**: `shared/data_access/snowflake_connector.py`

### Downstream Dependencies (Who Uses This)

- **Project 3** (Base Taxonomy): Uses master concepts as input
- **Product Features**: Cross-state content discovery, prerequisite chains
- **Content Platform**: Eliminate duplicate content recommendations

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Redundancy Detected | 60-75% | 23.7% (filtered) | 🟡 In Progress |
| Master Concepts Created | ~2,500 | 254 (filtered) | 🟡 In Progress |
| Skills Mapped | 100% | ~5% | 🟡 In Progress |
| Relationship Accuracy | ≥80% | TBD | 🟡 In Progress |
| Processing Time | <4 hrs | TBD | 🟡 In Progress |
| Cross-State Variants | ~1,200 groups | 13 (filtered) | 🟡 In Progress |

## Deliverables

### Code Artifacts

- [x] Variant classifier (fast and standard versions)
- [x] Semantic similarity engine
- [x] Master concept generator
- [x] Adaptive clustering algorithm
- [ ] Relationship classifier
- [ ] Validation dashboard

### Documentation

- [x] Base skill integration guide
- [ ] Redundancy detection methodology
- [ ] Master concepts specification
- [ ] Relationship types reference
- [ ] API documentation

### Data Outputs

- [ ] `master_concepts.csv` (~2,500 rows)
- [ ] `skill_master_concept_mapping.csv` (8,354 rows)
- [ ] `skill_relationships.csv` (20,000+ relationships)
- [ ] `redundancy_report.json`
- [ ] `variant_groups_summary.csv`

## Timeline

| Phase | Deliverable | Target Date | Status |
|-------|-------------|-------------|--------|
| **Phase 1** | Similarity engine | Q4 2025 | ✅ Complete |
| **Phase 2** | Variant classification | Q4 2025 | ✅ Complete |
| **Phase 3** | Master concept generation | Q4 2025 | 🟡 In Progress |
| **Phase 4** | Full production run | Q1 2026 | 🔵 Planned |
| **Phase 5** | Relationship classification | Q1 2026 | 🔵 Planned |
| **Phase 6** | Validation & refinement | Q1 2026 | 🔵 Planned |

## Known Issues & Limitations

### Current Limitations

1. **Similarity Threshold Sensitivity**: Results vary significantly with threshold (0.75 vs 0.80)
2. **Cross-Domain Relationships**: Hard to detect Math ↔ ELA connections
3. **Grade Progression Ambiguity**: Same skill at different grades may not be true progression
4. **Computational Cost**: Full similarity matrix is O(n²) for 8,354 skills
5. **Taxonomy Dependency**: Master concept names depend on Science of Reading taxonomy

### Mitigation Strategies

1. **Threshold**: Use adaptive thresholds based on skill area
2. **Cross-Domain**: Future enhancement with domain-aware embeddings
3. **Progression**: Use metadata (cognitive level, complexity) to validate progressions
4. **Performance**: Use approximate nearest neighbors for large-scale processing
5. **Taxonomy**: Support multiple taxonomies (future)

## Future Enhancements

### Short-Term (Q1 2026)

- [ ] Prerequisite chain detection (grade-level progressions)
- [ ] Human-in-the-loop validation interface
- [ ] Confidence scoring for all relationships
- [ ] Integration with standards alignment

### Long-Term (Q2+ 2026)

- [ ] Real-time similarity API for new skills
- [ ] Cross-domain relationship detection
- [ ] Learning progression visualization
- [ ] Automated master concept naming (LLM-based)

## References

- **Problem Analysis**: Original redundancy analysis notebook
- **Variant Classification**: `docs/BASE_SKILL_INTEGRATION.md`
- **Science of Reading Taxonomy**: `../../data/reference/frameworks/science_of_reading.csv`
- **ROCK Schema**: `../../docs/reference/rock-schema-overview.md`

---

**Questions or Issues?** Contact ROCK Skills Analysis Team

