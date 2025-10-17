#!/bin/bash
# Quick Start Script for Base Skill + Specification Pipelines

set -e  # Exit on error

echo "================================"
echo "BASE SKILL EXTRACTION - QUICK START"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "extract_base_skills.py" ]; then
    echo "❌ Error: Please run this script from rock-skills/analysis/pipelines/"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# Check for dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import spacy" 2>/dev/null; then
    echo "⚠️  spaCy not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check for spaCy model
echo "📚 Checking spaCy model..."
if ! python3 -c "import spacy; spacy.load('en_core_web_lg')" 2>/dev/null; then
    echo "⚠️  Downloading spaCy model (this may take a few minutes)..."
    python3 -m spacy download en_core_web_lg
fi

echo "✓ Dependencies ready"
echo ""

# Run POC test
echo "================================"
echo "RUNNING POC TEST"
echo "================================"
echo "Testing extraction on 20 sample skills..."
echo ""

python3 test_extraction_poc.py

echo ""
echo "================================"
echo "POC TEST COMPLETE"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Extract base skills from full dataset:"
echo "   python3 extract_base_skills.py --input ../../rock_schemas/SKILLS.csv --output ../../taxonomy/base_skills --limit 100"
echo ""
echo "2. Validate MECE and detect redundancies:"
echo "   python3 validate_mece.py --base-skills ../../taxonomy/base_skills --mappings ../../taxonomy/mappings/rock_to_base_mappings.csv --skills ../../rock_schemas/SKILLS.csv"
echo ""
echo "3. View in frontend:"
echo "   cd ../../poc && streamlit run skill_bridge_app.py"
echo ""
echo "4. Navigate to 'Redundancy Grooming' page to review conflicts"
echo ""

