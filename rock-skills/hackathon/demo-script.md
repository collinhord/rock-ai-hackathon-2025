# ROCK Skills Bridge Explorer - Demo Script

**Duration**: 5 minutes  
**Audience**: ROCK Skills List Advancement Team, Product Leaders, Curriculum Directors  
**Goal**: Demonstrate how taxonomy bridging solves the fragmentation problem

---

## Setup (Before Demo)

- [ ] Open Skills Bridge Explorer: `streamlit run skill_bridge_app.py`
- [ ] Confirm app loads at http://localhost:8501
- [ ] Test all navigation pages work
- [ ] Have backup screenshots ready
- [ ] Close distracting browser tabs/apps

---

## Opening (30 seconds)

**SAY:**  
> "I'm going to show you a solution to ROCK's master skill fragmentation problem—the fact that the same learning concept appears 6-8 times across different state standards, with no way to connect them. This 5-minute demo will show you what's possible when we bridge ROCK skills to Science of Reading taxonomy."

**DO:**
- Display Home page of Skills Bridge Explorer
- Point to key metrics at top

---

## Part 1: The Problem (1 minute)

**Screen**: Home page

**SAY:**  
> "Here's the problem in numbers: 8,300+ ROCK skills, but only about 1,200 unique master concepts. That means 6-8x redundancy—the same thing taught 6-8 different ways because each state expresses it differently in their standards."

**DO:**
- Point to "Avg Redundancy: 6.8x" metric
- Scroll to "The Problem" section

**SAY:**  
> "Look at Context Clues for Word Meaning as an example—15 different ROCK skills, across 9 states, teaching the exact same concept. Curriculum developers can't find these connections today because there's no metadata linking them."

**PAUSE**: Let the redundancy sink in (2 seconds)

---

## Part 2: The Solution Concept (30 seconds)

**Screen**: Home page, scroll to "The Solution"

**SAY:**  
> "The solution is adding a taxonomy bridge layer—connecting ROCK skills to Science of Reading, which is evidence-based and consistent. This doesn't require changing ROCK at all, which is critical because Star Assessment depends on current structure."

**DO:**
- Quickly highlight the "Without Bridge" vs. "With Bridge" comparison

**SAY:**  
> "Without the bridge, you search 'phoneme blending' and miss 7 out of 12 skills. With the bridge, you find all 12 instantly, grouped by state. Let me show you."

---

## Part 3: Master Concept Browser - The "Wow" Moment (1.5 minutes)

**Screen**: Navigate to "Master Concept Browser"

**SAY:**  
> "This is the Master Concept Browser. Watch what happens when I search for 'blend'..."

**DO:**
- Type "blend" in search box
- Show "Phoneme Blending" concept card appears

**SAY:**  
> "Phoneme Blending—a Science of Reading master concept. It says 12 skills, across 8 authorities. Let me expand this..."

**DO:**
- Click to expand "Phoneme Blending" concept
- Let them see the taxonomy path: "Decoding and Word Recognition > Phonological Awareness > Phoneme Awareness"

**SAY:**  
> "Here's the Science of Reading taxonomy path that grounds this concept. And below—all 12 ROCK skills mapped to it."

**DO:**
- Scroll through the table of mapped skills
- Point out different grade levels and skill area names

**SAY:**  
> "Notice they're all teaching the same thing but with different wording: 'Blend phonemes to form words,' 'Blend spoken phonemes into one-syllable words,' 'Orally blend 2-3 phonemes...' Same concept, fragmented across states."

**PAUSE**: "This is the discovery problem solved." (2 seconds)

**DO:**
- Quickly collapse and search for "context"
- Show "Context Clues for Word Meaning" with 15 skills

**SAY:**  
> "Same story with context clues—15 skills, all teaching contextual vocabulary. Without this bridge, you'd never find them all."

---

## Part 4: Redundancy Visualizer - Proof (1 minute)

**Screen**: Navigate to "Redundancy Visualizer"

**SAY:**  
> "Let me show you the quantitative proof this is a real problem."

**DO:**
- Display bar chart "Skills per Master Concept"
- Point to tallest bars

**SAY:**  
> "These are the most fragmented concepts. Main Idea Identification—18 skills. Making Inferences—16 skills. Author's Purpose—14 skills. All teaching the same learning objective, just filtered through different state standards."

**DO:**
- Scroll to distribution histogram
- Point to red mean line

**SAY:**  
> "The average is 6.8 skills per concept. Some concepts have as many as 18 state variants. This is why curriculum developers struggle—they're searching in a fragmented space with no connective tissue."

---

## Part 5: Skill Inspector - Individual Skill View (30 seconds)

**Screen**: Navigate to "Skill Inspector"

**SAY:**  
> "From the other direction, you can search individual ROCK skills and see their taxonomy mappings."

**DO:**
- Search "letter sound"
- Expand one skill
- Point to "✅ Mapped" indicator and master concept

**SAY:**  
> "Green checkmark means it's mapped to a master concept—Letter-Sound Recognition in this case. The skills without checkmarks aren't mapped yet, which is expected in a pilot, but shows the path to full coverage."

---

## Closing: Next Steps (30 seconds)

**Screen**: Return to Home or display executive summary

**SAY:**  
> "So what did we accomplish in this hackathon? Four things:
> 1. **Quantified the problem**—redundancy analysis with real data
> 2. **Mapped 50 skills**—proof of concept for taxonomy bridging
> 3. **Built this working POC**—you just saw it in action
> 4. **Defined next steps**—pilot with K-2 foundational literacy"

**PAUSE** (1 second)

**SAY:**  
> "This is non-invasive—no ROCK changes required. It's extensible—can add Math Learning Progressions next. And it's strategic—positions Renaissance as learning science leaders. The question is: do we move to pilot?"

**DO:**
- Stop screen share or close with final slide

---

## Backup Talking Points (If Questions Arise)

### "How much effort to map all skills?"
> "We mapped 50 skills in ~20 hours as proof-of-concept. At that rate, 2,000 ELA skills would take ~800 hours, or about 4-6 months with a dedicated team. But we'd use AI-assisted mapping to accelerate—the semantic similarity tool can suggest top-5 matches per skill, and humans validate."

### "What if Science of Reading changes?"
> "That's why we use a versioned mapping table—skills link to SoR v1.0 or v2.0. Old mappings preserved for historical data, new mappings added as taxonomy evolves. It's the same challenge as when states update standards, which we already handle."

### "Will this work for Math?"
> "Yes. Math needs a learning progressions taxonomy like Science of Reading. Options: NCTM frameworks, CCSS Math progressions, or cognitive learning trajectories research. Same approach—map ROCK Math skills to progression nodes."

### "How do we maintain mappings?"
> "Governance process: curriculum specialists own mappings, subject matter experts review, data engineers implement. Quarterly review cycles. New skills trigger mapping workflow. It's similar to how we maintain standards alignments today."

### "What about P&I's granularity problem?"
> "This solves horizontal fragmentation first. For vertical granularity (P&I needing finer skills), the same Science of Reading taxonomy provides decomposition structure—master concept breaks into instructional sub-objectives. One bridge layer serves both problems."

---

## Troubleshooting

### If app won't load:
- Have screenshots of each page ready
- Walk through static images instead
- Explain "Here's what you'd see if we had the app running..."

### If data seems sparse:
- Acknowledge: "This is a pilot with 50 mapped skills to prove the concept"
- Emphasize: "Full implementation would map all 2,000+ ELA skills"

### If questions go too deep:
- Redirect: "Great question—let's capture that for the pilot design phase"
- Offer: "I have detailed documentation we can review after the demo"

---

## Post-Demo Actions

- [ ] Share link to GitHub repo or documentation
- [ ] Send executive summary PDF
- [ ] Schedule follow-up discussion if interest is high
- [ ] Gather feedback on POC features
- [ ] Note feature requests for future enhancements

---

## Key Phrases to Memorize

1. "6-8x redundancy—same concept, 6-8 state variants"
2. "Non-invasive solution—no ROCK changes required"
3. "Science of Reading provides the master taxonomy"
4. "Curriculum developers can't find connections today"
5. "Discovery problem solved"

---

## Success Indicators

✅ **Excellent Demo**:
- Audience asks "When can we pilot this?"
- Multiple stakeholders express excitement
- Requests for detailed roadmap and resourcing

✅ **Good Demo**:
- Clear understanding of problem and solution
- Interest in seeing more detailed analysis
- Questions about implementation feasibility

✅ **Needs Follow-Up**:
- Questions about problem magnitude (need more data)
- Concerns about effort/cost (need detailed estimates)
- Unclear value proposition (need stakeholder-specific benefits)

---

**Good luck! You've got a solid POC that speaks for itself. Keep energy high, pace brisk, and focus on the "wow" moments.**

