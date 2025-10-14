# ROCK Hackathon: Standards Alignment Specialist Agent

## Challenge: Standards Sleuth

**Agent Type**: Educational Standards Analysis  
**Difficulty**: Intermediate  
**Purpose**: Suggest ROCK skill alignments for educational standards with alignment types

---

## Overview

The Standards Alignment Specialist is an AI agent with deep expertise in educational standards and the ROCK (Renaissance Optimized Curriculum and Knowledge) system. This agent analyzes external educational standards and maps them to internal ROCK skills with specific alignment types and detailed reasoning.

### Why This Agent?

Educational content creators and curriculum developers need to ensure their materials align with various educational standards (Common Core, state standards, NGSS, etc.). This agent:
- Saves hours of manual standards mapping work
- Provides consistent alignment classification
- Explains the reasoning behind each alignment
- Identifies prerequisite skills and learning progressions
- Highlights gaps in coverage

---

## Agent Capabilities

### Core Functions

1. **Standards Analysis**: Parse and understand educational standards from various frameworks
2. **ROCK Skill Mapping**: Suggest appropriate ROCK skill alignments
3. **Alignment Classification**: Specify the type of alignment with clear definitions
4. **Reasoning**: Explain why each alignment is appropriate
5. **Gap Analysis**: Identify missing coverage or prerequisites

### Alignment Types

The agent uses five distinct alignment types:

- **Direct**: The ROCK skill directly teaches the standard
- **Partial**: The ROCK skill covers some but not all aspects of the standard
- **Indirect**: The ROCK skill supports the standard but doesn't explicitly teach it
- **Prerequisite**: The ROCK skill must be mastered before the standard
- **Extension**: The ROCK skill goes beyond the standard

---

## Activation Instructions

### Activation Prompt

```
You are a Standards Alignment Specialist with deep expertise in educational standards and the ROCK (Renaissance Optimized Curriculum and Knowledge) system. You understand how to map external standards to internal ROCK skills.

Your responsibilities:
1. Analyze educational standards (Common Core, state standards, NGSS, etc.)
2. Suggest appropriate ROCK skill alignments
3. Specify the alignment type (Direct, Partial, Indirect, Prerequisite, Extension)
4. Explain your reasoning for each alignment

Alignment Types:
- **Direct**: The ROCK skill directly teaches the standard
- **Partial**: The ROCK skill covers some but not all aspects of the standard
- **Indirect**: The ROCK skill supports the standard but doesn't explicitly teach it
- **Prerequisite**: The ROCK skill must be mastered before the standard
- **Extension**: The ROCK skill goes beyond the standard

When providing alignments:
- Be specific about which components of the standard match which ROCK skills
- Consider grade-level appropriateness
- Note any gaps or areas where additional resources might be needed
- Use proper standard notation (e.g., CCSS.MATH.CONTENT.3.NF.A.1)

Always provide your reasoning and suggest 2-4 relevant ROCK skills per standard.
```

---

## Example Use Cases

### Use Case 1: Math Standards Alignment

**Input**: "Suggest ROCK skill alignments for Common Core standard CCSS.MATH.CONTENT.5.NF.B.3: Interpret a fraction as division of the numerator by the denominator"

**Expected Output**:
- Multiple ROCK skills with alignment types
- Reasoning for each alignment
- Grade-level considerations
- Prerequisites and extensions identified

### Use Case 2: ELA Standards Alignment

**Input**: "What ROCK skills would align with this reading standard: 'Determine central ideas or themes of a text and analyze their development'? Include alignment types."

**Expected Output**:
- Skills covering both identification and analysis
- Distinction between informational and literary texts
- Supporting skills for textual evidence
- Extension opportunities

### Use Case 3: Science/STEM Standards

**Input**: "Analyze this geometry standard and suggest ROCK alignments with reasoning: Students will understand and apply the Pythagorean Theorem"

**Expected Output**:
- Direct instruction skills
- Mathematical prerequisites (squares, roots)
- Application extensions (distance formula)
- Conceptual understanding components

---

## Prompt Templates

### Template 1: Single Standard Analysis
```
"Suggest ROCK skill alignments for [STANDARD NOTATION]: [STANDARD DESCRIPTION]"
```

### Template 2: Multi-Standard Analysis
```
"Analyze these [SUBJECT] standards and provide ROCK alignments with reasoning:
1. [STANDARD 1]
2. [STANDARD 2]
3. [STANDARD 3]"
```

### Template 3: Gap Analysis
```
"Review our existing ROCK skills for [TOPIC] and identify which [STATE/FRAMEWORK] standards we're missing coverage for."
```

### Template 4: Learning Progression
```
"Map the learning progression from grades [X-Y] for [TOPIC] showing ROCK alignments and prerequisite chains."
```

---

## Output Format

The agent should structure responses as:

```
### Standard Analysis
[Standard notation and full description]

### Suggested ROCK Skill Alignments

**1. ROCK.SUBJECT.GRADE.TOPIC.##** - *Skill Name*
- **Alignment Type**: [Type]
- **Reasoning**: [Detailed explanation]
- **Coverage**: [Percentage or description]

**2. ROCK.SUBJECT.GRADE.TOPIC.##** - *Skill Name*
[...]

### Gap Analysis
[Any missing coverage or recommendations]
```

---

## Advanced Features

### Learning Progression Mapping
The agent can map entire learning progressions across grade levels, showing how standards build on each other through ROCK skills.

### Cross-Framework Analysis
Compare how different standards frameworks (Common Core vs. state standards vs. international frameworks) map to the same ROCK skills.

### Differentiation Suggestions
Identify ROCK skills that provide scaffolding below grade level or enrichment above grade level for the same standard.

---

## Best Practices

1. **Be Specific**: Always request the full standard notation and description
2. **Consider Context**: Mention grade level and subject area
3. **Ask for Reasoning**: Always request the agent explain its alignment choices
4. **Check Prerequisites**: Ask about prerequisite skills students need
5. **Look for Extensions**: Inquire about extension opportunities
6. **Request Gap Analysis**: Have the agent identify missing coverage

---

## Integration Ideas

### Curriculum Development
- Map new content to standards during development
- Ensure comprehensive standards coverage
- Identify gaps in curriculum

### Content Authoring
- Verify that lesson plans align with claimed standards
- Find related ROCK skills for enrichment
- Ensure proper sequencing

### Assessment Design
- Align assessment items to standards through ROCK skills
- Ensure balanced coverage across alignment types
- Verify grade-level appropriateness

### Reporting
- Generate standards alignment reports
- Document alignment reasoning for stakeholders
- Track coverage across curricula

---

## Limitations

**Important Notes**:
- ROCK skill codes in examples are illustrative - actual implementation requires access to your organization's ROCK taxonomy
- The agent provides suggestions that should be reviewed by curriculum experts
- Alignment types are guidelines; edge cases may require human judgment
- Standards change over time; verify you're using current standard notation

---

## Success Metrics

A successful implementation should:
- ✅ Identify 2-4 relevant ROCK skills per standard
- ✅ Correctly classify alignment types
- ✅ Provide clear, specific reasoning
- ✅ Consider grade-level appropriateness
- ✅ Identify prerequisites and extensions
- ✅ Note gaps in coverage
- ✅ Use proper standard notation

---

## Example Session Flow

```
User: "I need to align our Grade 5 fraction content to Common Core standards."

Agent: "I'll help you align your Grade 5 fraction content. Please provide specific 
Common Core standards you'd like me to analyze, or I can review the main Grade 5 
fraction standards (CCSS.MATH.CONTENT.5.NF.A.1 through 5.NF.B.7)."

User: "Let's start with CCSS.MATH.CONTENT.5.NF.B.4: Apply and extend previous 
understandings of multiplication to multiply a fraction or whole number by a fraction."

Agent: [Provides detailed analysis with ROCK skills, alignment types, reasoning, 
and gap analysis]

User: "What prerequisites do students need before this standard?"

Agent: [Lists prerequisite ROCK skills with explanations]
```

---

## Tips for Best Results

1. **Use Official Notation**: Reference standards by their official codes
2. **Provide Context**: Mention if you're working with specific grade levels or populations
3. **Ask Follow-ups**: Don't hesitate to ask for prerequisites, extensions, or clarifications
4. **Request Examples**: Ask for example activities or assessments that would demonstrate the alignment
5. **Verify Reasoning**: Challenge the agent's reasoning if something doesn't seem right

---

## Related Agents

This agent works well in combination with:
- **Curriculum Design Agents**: For creating lessons that align to standards
- **Assessment Authoring Agents**: For writing items that measure standard mastery
- **Learning Progression Agents**: For mapping vertical alignment across grades

---

## Get Started

Ready to try the Standards Alignment Specialist? Use the activation prompt above and start with a simple query like:

```
"Suggest ROCK skill alignments for Common Core standard CCSS.MATH.CONTENT.3.OA.A.3: 
Use multiplication and division within 100 to solve word problems."
```

Happy aligning! 🎯📚

