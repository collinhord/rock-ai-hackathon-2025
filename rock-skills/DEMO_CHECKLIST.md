# Demo Checklist - ROCK Skills Bridge

Pre-presentation validation checklist for hackathon demos and stakeholder presentations.

## 🎯 Quick Start

**Run automated validation**:
```bash
cd /path/to/rock-skills
bash scripts/quick_demo_test.sh
```

If all checks pass ✅, proceed to Manual Checks section.

---

## 🤖 Automated Validation

- [ ] Run `scripts/quick_demo_test.sh`
- [ ] All 5 tests pass
- [ ] No error messages in output

---

## 🔍 Manual Pre-Demo Checks

### Environment Setup (5 minutes before demo)

- [ ] **Close distracting applications** (Slack, email, notifications)
- [ ] **Full screen browser** ready (Chrome or Firefox recommended)
- [ ] **Terminal window** ready in poc/ directory
- [ ] **Demo script open** (`DEMO_TEST_GUIDE.md`)
- [ ] **Backup screenshots** available (in case app fails)
- [ ] **Network connection** stable (for AWS Bedrock if demoing taxonomy builder)

### Application Pre-Launch (2 minutes before demo)

- [ ] Navigate to poc directory: `cd rock-skills/poc`
- [ ] Launch Streamlit: `streamlit run skill_bridge_app.py`
- [ ] Wait for "You can now view your Streamlit app in your browser"
- [ ] Open browser to `http://localhost:8501`
- [ ] Verify Home page loads without errors

### Quick Page Verification (3 minutes)

Click through each page to verify loading:

- [ ] 📋 **Problem → Solution** (NEW) - Loads, shows 13 concepts, dropdown works, charts render
- [ ] 🏠 **Home** - Metrics display (13 concepts, 212 bridged skills), example concept shows
- [ ] 🎯 **Content Scaling Simulator** - Real concepts section works, mock simulator loads
- [ ] 🔎 **Cross-State Discovery** - Loads, state selector populated
- [ ] 💰 **Scaling Impact Dashboard** - Loads, ROI calculator visible
- [ ] 🔍 **Master Concept Browser** - Shows 13 concepts, filtering works
- [ ] 📊 **Redundancy Visualizer** - Loads, charts render
- [ ] 🔗 **Variant Analysis** - Master Concepts tab shows State A mappings

### Content Scaling Simulator Specific (Primary Demo)

- [ ] Select test content: "Blend 2-Phoneme CVC Words"
- [ ] Content details expand
- [ ] Three tabs visible (Option A, B, C)
- [ ] Toggle "Show With Bridge" works
- [ ] Metrics update correctly
- [ ] Bar chart displays
- [ ] No console errors (F12 → Console tab)

---

## 📋 Demo Execution Checklist

### Opening (30 seconds)

- [ ] Introduce yourself and project name
- [ ] State the core problem: "Content scaling blocked by skill fragmentation"
- [ ] Navigate to **Problem → Solution** page (NEW first page)

### Problem → Solution Walkthrough (1-2 minutes) [RECOMMENDED]

- [ ] Show real example: Select top fragmented concept from dropdown
- [ ] Point out: Same concept, N different state expressions
- [ ] Scroll to Section 2: Show data evidence (13 concepts, 212 skills bridged)
- [ ] Scroll to Section 3: Compare WITHOUT vs WITH bridge side-by-side
- [ ] Emphasize: "This is the scaling problem and the bridge solution"

### Main Demo (2 minutes)

- [ ] Show "impossible dilemma" with 3 bad options
- [ ] Click through Option A, B, C tabs
- [ ] Emphasize pain points (8% coverage, 1 hour, bypass ROCK)
- [ ] Toggle "Show With Bridge" - THIS IS THE "WOW MOMENT"
- [ ] Highlight transformation: 8% → 100%, 60 min → 5 min
- [ ] Show state coverage expansion

### Supporting Features (1 minute)

- [ ] Navigate to Master Concept Browser - Show 13 generated concepts with real data
- [ ] Optional: Show Variant Analysis → Master Concepts tab (State A mappings)
- [ ] Navigate to ROI Dashboard - Show break-even calculation (< 12 months)
- [ ] Briefly mention Cross-State Discovery if time permits

### Closing (30 seconds)

- [ ] Summarize: "Bridge layer solves content scaling + skill discovery"
- [ ] State ROI: "6-12 month break-even, minimal investment"
- [ ] Next steps: "Ready for pilot with K-2 literacy"

---

## 🐛 Troubleshooting During Demo

### If app won't start
1. Check if already running: `ps aux | grep streamlit`
2. Kill if needed: `pkill -f streamlit`
3. Restart: `streamlit run skill_bridge_app.py`
4. **BACKUP**: Use screenshots and talk through functionality

### If page doesn't load
1. Navigate to Home, then back to target page
2. Refresh browser (Cmd+R / Ctrl+R)
3. **BACKUP**: Describe feature verbally, show screenshots

### If toggle doesn't work
1. Refresh page
2. Try different content item
3. **BACKUP**: Show static comparison screenshots

### If audience can't see
1. Zoom in: Cmd/Ctrl + "++" 
2. Full screen browser window
3. Move closer to screen if possible

---

## 📸 Backup Materials

Have these ready in case of technical issues:

- [ ] Screenshots of Content Scaling Simulator (all states)
- [ ] Screenshots of ROI Dashboard with calculations
- [ ] Printed executive summary (`hackathon/executive-summary.md`)
- [ ] Talking points document (`hackathon/demo-script.md`)

---

## ✨ Success Indicators

After demo, verify you communicated:

- [ ] **Problem is clear**: Audience understands content scaling is blocked
- [ ] **Solution is compelling**: Bridge layer makes tagging viable
- [ ] **ROI is obvious**: 6-12 month break-even with clear savings
- [ ] **Next steps are defined**: Pilot phase ready to start
- [ ] **Demo was smooth**: No major technical issues

---

## 📞 Post-Demo Actions

- [ ] Share executive summary (`hackathon/executive-summary.md`)
- [ ] Schedule follow-up meeting
- [ ] Gather feedback and questions
- [ ] Document any technical issues for improvement
- [ ] Update demo materials based on feedback

---

## ⏱️ Timing Guide

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Environment setup | 5 min | -5 min |
| Pre-launch checks | 2 min | -3 min |
| Page verification | 2 min | -1 min |
| **Demo start** | 0 min | **0 min** |
| Opening | 0:30 | 0:30 |
| Main demo | 2:00 | 2:30 |
| Supporting features | 1:00 | 3:30 |
| Closing | 0:30 | 4:00 |
| Q&A | 3:00 | 7:00 |

**Target**: 4-5 minute demo + 3-5 minute Q&A = **7-10 minute total**

---

## 🎓 Presentation Tips

### Do:
- ✅ Speak slowly and clearly
- ✅ Point to specific UI elements
- ✅ Pause after toggling bridge to let impact sink in
- ✅ Use concrete numbers (8% → 100%, 1 hour → 5 min)
- ✅ Relate to business value (ROI, efficiency)

### Don't:
- ❌ Rush through the toggle moment
- ❌ Get distracted by technical details
- ❌ Apologize for UI polish
- ❌ Skip the ROI calculation
- ❌ Forget to close with next steps

---

**Remember**: The toggle switch transformation (8% → 100%) is your "wow moment". Make it count!

**Good luck! 🚀**

---

**Project**: ROCK Skills Taxonomy Bridge  
**Hackathon**: Renaissance Learning AI Hackathon 2025  
**Last Updated**: October 2025

