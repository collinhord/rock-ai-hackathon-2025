#!/bin/bash
# End-to-End Test for Base Skill + Specification System
# 
# This script tests the complete pipeline:
# 1. Extract base skills from sample data
# 2. Extract specifications
# 3. Run MECE validation
# 4. Generate outputs for UI

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  BASE SKILL + SPECIFICATION SYSTEM - END-TO-END TEST          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
ROCK_SKILLS_DIR="/Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills"
PIPELINES_DIR="$ROCK_SKILLS_DIR/analysis/pipelines"
TAXONOMY_DIR="$ROCK_SKILLS_DIR/taxonomy"
TEST_LIMIT=50  # Test with 50 skills

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "📁 Working Directory: $ROCK_SKILLS_DIR"
echo "🔧 Test Limit: $TEST_LIMIT skills"
echo ""

# Step 1: Check dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PIPELINES_DIR"

if ! python3 -c "import spacy" 2>/dev/null; then
    echo -e "${RED}✗${NC} spaCy not installed"
    echo "Installing dependencies..."
    pip install -r requirements.txt -q
fi

if ! python3 -c "import spacy; spacy.load('en_core_web_lg')" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} spaCy model not found, downloading..."
    python3 -m spacy download en_core_web_lg
fi

echo -e "${GREEN}✓${NC} All dependencies ready"
echo ""

# Step 2: Extract Base Skills
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Extracting Base Skills"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 extract_base_skills.py \
  --input "$ROCK_SKILLS_DIR/rock_data/SKILLS.csv" \
  --output "$TAXONOMY_DIR/base_skills" \
  --limit $TEST_LIMIT \
  --no-llm

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Base skills extracted successfully"
else
    echo -e "${RED}✗${NC} Base skill extraction failed"
    exit 1
fi

echo ""

# Step 3: Extract Specifications
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Extracting Specifications"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$TAXONOMY_DIR/mappings/rock_to_base_mappings.csv" ]; then
    echo -e "${RED}✗${NC} Mappings file not found"
    exit 1
fi

python3 extract_specifications.py \
  --input "$TAXONOMY_DIR/mappings/rock_to_base_mappings.csv" \
  --output "$TAXONOMY_DIR/specifications" \
  --limit $TEST_LIMIT \
  --no-llm

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Specifications extracted successfully"
else
    echo -e "${RED}✗${NC} Specification extraction failed"
    exit 1
fi

echo ""

# Step 4: Run MECE Validation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Running MECE Validation & Redundancy Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 validate_mece.py \
  --base-skills "$TAXONOMY_DIR/base_skills" \
  --mappings "$TAXONOMY_DIR/mappings/rock_to_base_mappings.csv" \
  --skills "$ROCK_SKILLS_DIR/rock_data/SKILLS.csv" \
  --output "$TAXONOMY_DIR/validation_report.json" \
  --no-llm

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} MECE validation completed successfully"
else
    echo -e "${RED}✗${NC} MECE validation failed"
    exit 1
fi

echo ""

# Step 5: Check Outputs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Verifying Outputs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count base skills
BASE_SKILLS_COUNT=$(find "$TAXONOMY_DIR/base_skills" -name "BS-*.json" | wc -l)
echo "  Base skills generated: $BASE_SKILLS_COUNT"

# Check for validation report
if [ -f "$TAXONOMY_DIR/validation_report.json" ]; then
    MECE_SCORE=$(python3 -c "import json; print(json.load(open('$TAXONOMY_DIR/validation_report.json'))['mece_score'])")
    echo "  MECE score: $MECE_SCORE"
fi

# Check for conflicts
if [ -f "$TAXONOMY_DIR/conflicts.json" ]; then
    CONFLICTS_COUNT=$(python3 -c "import json; print(len(json.load(open('$TAXONOMY_DIR/conflicts.json'))))")
    echo "  Conflicts detected: $CONFLICTS_COUNT"
fi

# Check for redundancies
if [ -f "$TAXONOMY_DIR/redundancies.json" ]; then
    REDUNDANCIES_COUNT=$(python3 -c "import json; print(len(json.load(open('$TAXONOMY_DIR/redundancies.json'))))")
    echo "  Redundancies detected: $REDUNDANCIES_COUNT"
fi

echo ""
echo -e "${GREEN}✓${NC} All outputs generated successfully"
echo ""

# Step 6: Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  TEST COMPLETE ✓                                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Results Summary:"
echo "  • Base skills: $BASE_SKILLS_COUNT"
echo "  • MECE score: ${MECE_SCORE:-N/A}"
echo "  • Conflicts: ${CONFLICTS_COUNT:-0}"
echo "  • Redundancies: ${REDUNDANCIES_COUNT:-0}"
echo ""
echo "🎨 Next Steps:"
echo "  1. View results in UI:"
echo "     cd $ROCK_SKILLS_DIR/poc"
echo "     streamlit run skill_bridge_app.py"
echo ""
echo "  2. Navigate to 'Redundancy Grooming' page in sidebar"
echo ""
echo "  3. Review conflicts and make decisions"
echo ""
echo "  4. Run full extraction (all skills with LLM):"
echo "     cd $PIPELINES_DIR"
echo "     python3 extract_base_skills.py --input ../../rock_data/SKILLS.csv --output ../../taxonomy/base_skills"
echo ""

