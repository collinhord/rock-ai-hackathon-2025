# ROCK Skills Bridge: Next Steps Roadmap

**Following Successful POC Demonstration**

---

## Immediate Actions (1-2 Weeks)

### 1. Stakeholder Validation
**Goal**: Confirm problem resonates and solution is viable

**Actions**:
- [ ] Present POC to ROCK Skills List Advancement Team
- [ ] Demo for curriculum designers and gather pain point validation
- [ ] Show product managers to confirm feature enablement value
- [ ] Brief research team on data aggregation potential

**Deliverables**:
- Stakeholder feedback summary
- Prioritized use cases by team
- Buy-in level assessment

**Success Criteria**:
- 3+ stakeholder groups confirm problem is top-5 priority
- At least one product team commits to pilot integration

---

### 2. Learning Science Validation
**Goal**: Ensure mapping methodology is sound

**Actions**:
- [ ] Share mapping examples with Renaissance literacy experts
- [ ] Validate Science of Reading taxonomy as appropriate framework
- [ ] Review confidence scoring approach
- [ ] Discuss edge cases (skills that don't map cleanly)

**Deliverables**:
- Mapping methodology documentation (peer-reviewed)
- Confidence criteria definition (High/Medium/Low guidelines)
- Edge case handling protocols

**Success Criteria**:
- Learning science team endorses approach
- Methodology documented and approved

---

### 3. Effort Estimation
**Goal**: Accurately scope pilot and full implementation

**Actions**:
- [ ] Benchmark mapping time per skill (use POC data)
- [ ] Estimate total K-2 foundational literacy skills (~500 skills)
- [ ] Calculate effort with vs. without AI assistance
- [ ] Identify required team roles and FTE commitment

**Deliverables**:
- Detailed work breakdown structure
- Resource plan with FTE requirements
- Timeline with milestones

**Success Criteria**:
- Confident estimate for pilot phase
- Executive-ready resourcing proposal

---

## Pilot Phase (3-6 Months)

### Goal: Production-Ready Taxonomy Layer for K-2 Foundational Literacy

### Scope
**Skills**: K-2 Foundational Literacy (~500 skills)
- Alphabetic Knowledge
- Phonological/Phonemic Awareness  
- Phonics and Decoding
- Early Fluency

**Deliverables**:
1. Complete taxonomy mappings for 500 skills
2. Production schema (SKILL_TAXONOMY_MAPPINGS table)
3. API endpoints for taxonomy queries
4. Integration with Star Early Literacy (pilot product)
5. User documentation for curriculum designers

### Phase 1: Infrastructure (Weeks 1-4)

**Data Engineering**:
- [ ] Design SKILL_TAXONOMY_MAPPINGS table schema
- [ ] Implement in test database environment
- [ ] Create data migration scripts
- [ ] Build ETL pipeline for mapping updates

**API Development**:
- [ ] Design RESTful API endpoints
  - `GET /skills/{skill_id}/taxonomy` - Get taxonomy for skill
  - `GET /taxonomy/{concept_id}/skills` - Get skills for concept
  - `GET /taxonomy/search?q={query}` - Search master concepts
  - `GET /skills/equivalents/{skill_id}` - Get equivalent skills
- [ ] Implement with caching layer
- [ ] Write automated tests
- [ ] Deploy to test environment

**Deliverables**:
- Production-ready database schema
- API documentation (Swagger/OpenAPI)
- Test suite with >90% coverage

---

### Phase 2: Mapping (Weeks 3-12, overlaps with Phase 1)

**Curriculum Team**:
- [ ] Finalize mapping methodology guide
- [ ] Train curriculum specialists on process
- [ ] Set up mapping workflow (tools, review cycles)

**Mapping Work**:
- [ ] Use AI-assisted semantic similarity tool for initial suggestions
- [ ] Curriculum specialists review and validate top suggestions
- [ ] Subject matter experts spot-check high-confidence mappings
- [ ] Flag low-confidence mappings for deep review

**Quality Assurance**:
- [ ] Peer review sample (10% of mappings)
- [ ] External expert review (literacy research partner)
- [ ] Inter-rater reliability check

**Deliverables**:
- 500 K-2 foundational literacy skills mapped
- Confidence score for each mapping
- Mapping rationale documentation
- Quality metrics report

---

### Phase 3: Integration (Weeks 10-16)

**Product Integration** (Star Early Literacy):
- [ ] Integrate API into Star Early Literacy backend
- [ ] Enable master concept filtering in skill selection UI
- [ ] Add "conceptually similar skills" recommendation feature
- [ ] Update reporting to show Science of Reading alignment

**Testing**:
- [ ] Internal QA testing
- [ ] Beta testing with curriculum designers
- [ ] Gather user feedback on taxonomy features

**Documentation**:
- [ ] User guide for educators
- [ ] Technical documentation for engineers
- [ ] Training materials for support team

**Deliverables**:
- Live integration in Star Early Literacy (beta)
- User feedback report
- Iterative improvements plan

---

### Phase 4: Evaluation (Weeks 14-18)

**Metrics to Track**:
- **Efficiency**: Time to find skills (with vs. without taxonomy)
- **Coverage**: % of use cases supported vs. not supported
- **Accuracy**: User validation of mapping quality
- **Adoption**: % of users using taxonomy features

**Evaluation Activities**:
- [ ] Conduct user interviews (5-10 curriculum designers)
- [ ] A/B testing (if feasible) on search/discovery tasks
- [ ] Analyze feature usage analytics
- [ ] Calculate ROI (time saved × user count)

**Deliverables**:
- Pilot evaluation report
- ROI analysis
- Go/no-go recommendation for full rollout

---

## Full Implementation (6-18 Months)

### Assuming Successful Pilot

### Scope
**ELA**: All ~2,000 ELA skills (Grades K-12)  
**Math**: All ~2,000 Math skills (Grades K-12)

### Phases

#### Phase 1: Complete ELA Mapping (Months 1-9)
- Grades 3-5 (Months 1-4)
- Grades 6-8 (Months 4-7)
- Grades 9-12 (Months 7-9)
- Parallel quality assurance

#### Phase 2: Math Taxonomy Selection (Months 6-9)
- Evaluate existing math learning progression frameworks
- Select or create Renaissance Math taxonomy
- Gain learning science validation
- Pilot map 100 math skills for proof

#### Phase 3: Math Mapping (Months 9-15)
- K-5 elementary math
- 6-8 middle school math
- 9-12 high school math
- Parallel quality assurance

#### Phase 4: Platform Integration (Months 12-18)
- Star Assessments (all levels)
- myON (literacy)
- Freckle (math)
- Schoolzilla (analytics/reporting)
- Public API for partners

#### Phase 5: Advanced Features (Months 15-18)
- Learning progression visualizations
- Curriculum gap analysis tools
- Cross-product skill recommendation
- Research data aggregation by master concept

---

## Organizational Structure

### Pilot Phase Team (3-6 months)
- **1 Product Manager** (50% allocation)
- **2 Curriculum Specialists** (full-time)
- **1 Data Engineer** (full-time)
- **1 Backend Engineer** (full-time)
- **0.5 Learning Science Advisor** (part-time)

### Full Implementation Team (6-18 months)
- **1 Product Manager** (75% allocation)
- **4 Curriculum Specialists** (full-time)
- **2 Data Engineers** (full-time)
- **2 Backend Engineers** (full-time)
- **1 Frontend Engineer** (full-time, for advanced features)
- **1 Learning Science Advisor** (50% allocation)
- **1 QA Engineer** (50% allocation)

---

## Governance Model

### Mapping Governance
- **Owners**: Curriculum Specialists (create/update mappings)
- **Reviewers**: Subject Matter Experts (validate accuracy)
- **Approvers**: Learning Science Advisors (final sign-off)

### Change Management
- **New Skills**: Trigger mapping workflow within 2 weeks
- **Taxonomy Updates**: Version control, backward compatibility
- **Quality Issues**: Bug report system, prioritized fixes

### Review Cycles
- **Quarterly**: Spot-check sample of mappings (5-10%)
- **Annual**: Comprehensive review of all mappings
- **Ad-Hoc**: When taxonomy framework updates

---

## Risk Management

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema changes break existing systems | High | Non-invasive bridge layer, no ROCK modifications |
| API performance degrades at scale | Medium | Caching layer, database indexing, load testing |
| Data migration fails | Medium | Thorough testing, rollback plan, staged deployment |

### Organizational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Team capacity insufficient | High | Prioritize pilot, defer nice-to-haves, use AI assistance |
| Stakeholder priorities shift | High | Secure executive sponsorship, demonstrate early wins |
| Cross-team coordination delays | Medium | Clear governance, dedicated PM, regular sync meetings |

### Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mapping subjectivity undermines trust | High | Clear methodology, peer review, confidence scoring |
| Edge cases not handled | Medium | Document protocols, flag for expert review |
| Taxonomy framework changes | Low | Version control, backward compatibility |

---

## Success Metrics

### Pilot Phase Success
- ✅ 500 K-2 skills mapped with >90% high/medium confidence
- ✅ API endpoints deployed and performant (<100ms response)
- ✅ Star Early Literacy integration live in beta
- ✅ User feedback >4/5 on taxonomy features
- ✅ Demonstrated 50%+ efficiency gain in skill discovery

### Full Implementation Success
- ✅ 100% of ELA and Math skills mapped
- ✅ Integrated across all major Renaissance products
- ✅ Curriculum development time reduced by 30-50%
- ✅ Research publications cite taxonomy as alignment proof
- ✅ Competitive differentiation recognized in market

---

## Budget Estimate

### Pilot Phase (6 months)
- **Personnel**: $300K-400K (6 FTE blended rate)
- **Infrastructure**: $10K-20K (test environments, API hosting)
- **Tools/Licenses**: $5K (Confluence, Jira, semantic similarity models)
- **Total**: ~$320K-420K

### Full Implementation (12 months)
- **Personnel**: $800K-1.2M (9 FTE blended rate)
- **Infrastructure**: $30K-50K (production environments, scaling)
- **Tools/Licenses**: $10K-20K
- **External Consulting**: $50K (learning science validation)
- **Total**: ~$900K-1.3M

### 3-Year TCO (Maintenance)
- **Personnel**: $200K-300K/year (2 FTE maintenance)
- **Infrastructure**: $20K-30K/year
- **Total**: ~$220K-330K/year ongoing

---

## Decision Points

### Go/No-Go #1: After Stakeholder Validation (Week 2)
**Criteria**: 3+ stakeholder groups confirm top-5 priority  
**Decision**: Proceed to effort estimation or revisit problem framing

### Go/No-Go #2: After Effort Estimation (Week 3)
**Criteria**: ROI justifies pilot investment (~$350K)  
**Decision**: Greenlight pilot or table for future budget cycle

### Go/No-Go #3: After Pilot Evaluation (Month 6)
**Criteria**: >50% efficiency gain, >80% user satisfaction  
**Decision**: Proceed to full implementation or iterate pilot

---

## Communication Plan

### Internal Updates
- **Weekly**: Team standup (pilot phase)
- **Bi-weekly**: Stakeholder update (slide deck)
- **Monthly**: Executive summary (metrics dashboard)
- **Quarterly**: All-hands presentation (wins and learnings)

### External Communication
- **Post-Pilot**: Internal blog post, product release notes
- **Post-Launch**: Customer webinar, documentation
- **Annual**: Conference presentation (learning science community)

---

## Recommended Decision

**Proceed to Pilot Phase with K-2 Foundational Literacy**

**Rationale**:
1. Problem is quantified and stakeholder-validated
2. Solution is technically feasible and non-invasive
3. POC demonstrates clear value proposition
4. Risk is manageable with phased approach
5. Strategic alignment with Science of Reading emphasis

**Ask**:
- **Approval**: $350K pilot budget, 6-month timeline
- **Resources**: 3.5 FTE commitment (PM, curriculum, engineering)
- **Sponsorship**: Executive sponsor for cross-team coordination

---

**Next Immediate Action**: Schedule stakeholder validation meetings (within 2 weeks)

---

**Document Owner**: ROCK Skills Analysis Team  
**Last Updated**: October 2025  
**Version**: 1.0

