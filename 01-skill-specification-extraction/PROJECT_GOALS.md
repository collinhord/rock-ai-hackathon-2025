# Project 1: Skill Specification Extraction - Project Goals

**Owner**: ROCK Skills Analysis Team  
**Status**: In Development  
**Last Updated**: October 17, 2025

## Mission Statement

Extract comprehensive metadata and specifications from 8,354 ROCK skill descriptions using hybrid NLP + LLM + rule-based inference to enable semantic search, redundancy detection, and intelligent content alignment.

## Business Value

**Problem**: Skills in ROCK are human-readable but lack machine-readable metadata, limiting search effectiveness, preventing redundancy detection, and blocking intelligent content alignment features.

**Impact**: 
- 80-90% efficiency gain in content alignment and discovery
- Enables semantic search across 8,000+ skills
- Foundation for redundancy detection (Project 2) and base taxonomy (Project 3)
- Supports adaptive learning and cross-state content scaling

**Users**: 
- Curriculum designers seeking specific skills
- Content developers aligning materials to skills
- Product teams building adaptive learning features
- Data analysts studying skill relationships

## Objectives

### Primary Objectives (Must Have)

1. **Extract 23 metadata fields** from skill descriptions using spaCy NLP
   - Actions (verbs): identify, analyze, solve
   - Targets (objects): words, sentences, problems
   - Qualifiers (modifiers): simple, complex, multistep
   - Cognitive level: remember, understand, apply, analyze
   - Success criteria: ≥90% extraction accuracy

2. **Infer 6 specification fields** using deterministic rules
   - Text-dependent: requires reading passage vs. standalone
   - Complexity band: foundational, grade-level, advanced
   - Support level: scaffolded, independent, transfer
   - Context type: fictional, informational, mixed
   - Success criteria: ≥85% inference accuracy

3. **Process all 8,354 skills** in production pipeline
   - Batch processing with checkpointing
   - Cost-effective (LLM usage minimized)
   - Resilient to failures (resume capability)
   - Target: Complete in <8 hours, <$50 LLM cost

### Secondary Objectives (Nice to Have)

1. Active learning loop for continuous improvement
2. Confidence scoring for extracted metadata
3. Multi-language skill support (future)
4. Real-time extraction API

## Scope

### In Scope

- Metadata extraction from SKILL_NAME field
- 23 structured metadata fields (actions, targets, qualifiers, etc.)
- 6 inferred specification fields (text_dependent, complexity_band, etc.)
- English Language Arts (ELA) skills (priority)
- Mathematics skills (secondary)
- Batch processing pipeline
- Quality validation and reporting

### Out of Scope (Explicitly)

- Modifying ROCK schema or database
- Aligning skills to standards (separate system)
- Content recommendation (product feature)
- Real-time extraction (batch only)
- Non-English skills (future enhancement)
- Skills outside core content areas

## Technical Approach

### Architecture

**Hybrid 3-Layer Approach**:

1. **Rule-Based Layer** (spaCy NLP)
   - Extract actions (verbs), targets (nouns), qualifiers (adjectives/adverbs)
   - Part-of-speech tagging, dependency parsing
   - Fast, deterministic, cost-free
   - Accuracy: 90-95% for syntactic features

2. **LLM-Assisted Layer** (AWS Bedrock Claude)
   - Extract cognitive level, domain, context
   - Handle ambiguous or complex skills
   - Used selectively (10-20% of skills)
   - Cost-optimized with caching

3. **Inference Layer** (Deterministic Rules)
   - Infer text_dependent from extracted metadata
   - Infer complexity_band from grade level + qualifiers
   - Infer support_level from action complexity
   - 100% deterministic, explainable

### Data Flow

```
ROCK Skills (Snowflake)
    ↓
spaCy NLP Extraction (actions, targets, qualifiers)
    ↓
LLM Enrichment (cognitive level, domain) [optional]
    ↓
Rule-Based Inference (specifications)
    ↓
skill_metadata_enhanced.csv (23 fields)
skill_specifications_inferred.csv (6 fields)
```

### Key Technologies

- **Python 3.9+**: Core language
- **spaCy 3.x** (en_core_web_lg): NLP extraction
- **AWS Bedrock** (Claude 3.5): LLM assistance
- **Pandas**: Data manipulation
- **PyYAML**: Configuration management

## Dependencies

### Upstream Dependencies (Inputs)

- **Snowflake ROCK_DB.SKILLS**: Source data (8,354 skills)
  - SKILL_ID, SKILL_NAME, SKILL_AREA_NAME, CONTENT_AREA_NAME, GRADE_LEVEL_NAME
- **Shared data access layer**: `shared/data_access/snowflake_connector.py`
- **Shared LLM client**: `shared/llm/bedrock_client.py`

### Downstream Dependencies (Who Uses This)

- **Project 2** (Redundancy Detection): Uses metadata to improve similarity matching
- **Project 3** (Base Taxonomy): Uses specifications to inform taxonomy structure
- **Product Features**: Semantic search, adaptive learning, content alignment

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Extraction Accuracy | ≥90% | TBD | 🟡 In Progress |
| Inference Accuracy | ≥85% | TBD | 🟡 In Progress |
| Processing Time | <8 hrs | TBD | 🟡 In Progress |
| LLM Cost | <$50 | TBD | 🟡 In Progress |
| Skills Processed | 8,354 | 0 | 🟡 In Progress |
| Output Completeness | 100% | TBD | 🟡 In Progress |

## Deliverables

### Code Artifacts

- [x] spaCy NLP processor
- [x] Enhanced metadata extractor
- [x] Specification inference engine
- [ ] Batch processing pipeline
- [ ] Quality validation suite
- [ ] Cost tracking dashboard

### Documentation

- [x] Metadata field reference (29 fields)
- [x] Specification inference framework
- [ ] API documentation
- [ ] Quality validation guide
- [ ] Deployment guide

### Data Outputs

- [ ] `skill_metadata_enhanced.csv` (8,354 rows × 23 fields)
- [ ] `skill_specifications_inferred.csv` (8,354 rows × 6 fields)
- [ ] `extraction_quality_report.json`
- [ ] `extraction_summary.txt`

## Timeline

| Phase | Deliverable | Target Date | Status |
|-------|-------------|-------------|--------|
| **Phase 1** | spaCy extraction pipeline | Q4 2025 | ✅ Complete |
| **Phase 2** | LLM enrichment (sample) | Q4 2025 | 🟡 In Progress |
| **Phase 3** | Inference rules | Q4 2025 | 🟡 In Progress |
| **Phase 4** | Full production run | Q4 2025 | 🔵 Planned |
| **Phase 5** | Quality validation | Q1 2026 | 🔵 Planned |

## Known Issues & Limitations

### Current Limitations

1. **Grade-Level Ambiguity**: Skills like "K-2" span multiple grades, complicating complexity inference
2. **LLM Cost**: Full LLM extraction would cost $500+; hybrid approach reduces to <$50
3. **Context Dependency**: Some skills require standards context for accurate extraction
4. **Polysemy**: Same word can have different meanings (e.g., "bank" financial vs. riverbank)

### Mitigation Strategies

1. **Grade-Level**: Use midpoint for ranges, flag ambiguous cases
2. **Cost**: LLM only for ambiguous/complex skills (10-20%)
3. **Context**: Future enhancement to join with standards data
4. **Polysemy**: Use domain-specific dictionaries and context

## Future Enhancements

### Short-Term (Q1 2026)

- [ ] Active learning loop (human validation → model improvement)
- [ ] Confidence scoring for each extracted field
- [ ] Multi-pass extraction for complex skills
- [ ] Integration with standards alignment

### Long-Term (Q2+ 2026)

- [ ] Real-time extraction API for new skills
- [ ] Multi-language support (Spanish, French)
- [ ] Fine-tuned extraction models (reduce LLM dependency)
- [ ] Extraction from non-textual skill representations

## References

- **Metadata Schema**: `docs/METADATA_FIELD_REFERENCE.md`
- **Inference Framework**: `docs/SPECIFICATION_INFERENCE_FRAMEWORK.md`
- **spaCy Documentation**: https://spacy.io/
- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **ROCK Schema Overview**: `../../docs/reference/rock-schema-overview.md`

---

**Questions or Issues?** Contact ROCK Skills Analysis Team

