# Agent Prompts

Copy-paste ready agent prompts for quick setup in Cursor.

---

## 🤖 How to Use These Files

Each `.txt` file contains the complete prompt for one agent. To set up an agent:

1. **Open Cursor Settings** (`Cmd + ,` on Mac)
2. **Navigate to Agents**
3. **Create New Agent**
4. **Name**: Use the format `ROCK-Hackathon: [Agent Name]`
5. **Copy**: Open the corresponding `.txt` file and copy its entire contents
6. **Paste**: Into the "Instructions" field
7. **Model**: Select Claude Sonnet 4.5 (recommended)
8. **Save**

---

## 📁 Available Agent Prompts

### Master Agent
- **`master-guide.txt`** - Master Agent that orchestrates everything ⭐ START HERE

### Work-Related Agents (`work-agents/`)
1. `metadata-expert.txt` - Educational metadata specialist
2. `standards-alignment.txt` - Maps standards to ROCK skills
3. `document-summarizer.txt` - Prompt engineering for summarization
4. `data-visualization.txt` - Visualization strategy consultant
5. `executive-proposal.txt` - Business proposal writer

### Creative Agents (`creative-agents/`)
6. `recipe-chef.txt` - Creative culinary innovator
7. `comedy-writer.txt` - Puns, jokes, and song parodies
8. `letter-writer.txt` - Professional correspondence
9. `shakespeare-response.txt` - Shakespearean poetry response

---

## 🎯 Setup Recommendations

### Minimum Setup (Start Here)
1. **Master Guide** - Your strategic coordinator

### Add As Needed During Hackathon
Set up specialized agents when you reach their challenges:
- The Master Agent will tell you which one to create next
- Follow its setup guidance

### Full Setup (Optional)
If you have time before the hackathon, set up all 10 agents:
- Takes ~30 minutes total
- Means you're ready for any challenge
- Demonstrates thorough preparation

---

## 📋 Setup Checklist

- [ ] Master Guide (required)
- [ ] Metadata Expert
- [ ] Standards Alignment Specialist
- [ ] Document Summarizer
- [ ] Data Visualization Consultant
- [ ] Executive Proposal Writer
- [ ] Creative Recipe Chef
- [ ] Comedy Writer
- [ ] Professional Letter Writer
- [ ] Shakespeare Poetry Response

---

## 💡 Pro Tips

1. **Name Consistently**: Always use `ROCK-Hackathon:` prefix so all agents group together
2. **Test Each Agent**: After setup, ask it a simple question to verify it works
3. **Document Setup Time**: Track how long this takes for your demo/reflection
4. **Version Control**: If you customize agent prompts, save versions here

---

## 🔄 Updating Agent Prompts

If you refine an agent during the hackathon:

```bash
# Save your improved version
# Edit the .txt file with your refined prompt
# Commit the change
git add agents/
git commit -m "Refined [Agent Name] prompt based on testing"
```

This tracks your learning and prompt engineering evolution!

---

**[← Back to Main README](../README.md)** | **[→ Full Agent Documentation](../docs/agents/)**

