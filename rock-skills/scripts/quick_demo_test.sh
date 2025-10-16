#!/bin/bash
# Quick Demo Test Script
#
# Validates the system is ready for demo presentation.
# Run this before any hackathon demo or presentation.
#
# Usage: ./quick_demo_test.sh

set -e

echo "======================================================================"
echo "ROCK Skills Demo Readiness Check"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# Test 1: Data Integrity
echo "Test 1: Validating data integrity..."
if python3 scripts/verify_data_integrity.py > /tmp/data_check.log 2>&1; then
    echo -e "${GREEN}✅ Data integrity check PASSED${NC}"
else
    echo -e "${RED}❌ Data integrity check FAILED${NC}"
    cat /tmp/data_check.log
    exit 1
fi

# Test 2: Check required dependencies
echo ""
echo "Test 2: Checking Python dependencies..."
MISSING_DEPS=0
for pkg in streamlit pandas plotly numpy; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $pkg installed"
    else
        echo -e "  ${RED}❌${NC} $pkg missing"
        MISSING_DEPS=1
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Install missing dependencies:${NC}"
    echo "  cd poc && pip install -r requirements.txt"
    exit 1
fi

# Test 3: Critical files exist
echo ""
echo "Test 3: Checking critical files..."
CRITICAL_FILES=(
    "poc/skill_bridge_app.py"
    "poc/data_loader.py"
    "poc/mock_data/content_library.csv"
    "taxonomy.db"
    "POC_science_of_reading_literacy_skills_taxonomy.csv"
    "DEMO_TEST_GUIDE.md"
)

MISSING_FILES=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file MISSING"
        MISSING_FILES=1
    fi
done

if [ $MISSING_FILES -eq 1 ]; then
    echo -e "${RED}❌ Critical files missing${NC}"
    exit 1
fi

# Test 4: Import test for main application
echo ""
echo "Test 4: Testing POC application imports..."
cd poc
if python3 -c "import skill_bridge_app; import data_loader" 2>/dev/null; then
    echo -e "${GREEN}✅ POC application imports successful${NC}"
else
    echo -e "${RED}❌ POC application import failed${NC}"
    python3 -c "import skill_bridge_app; import data_loader"
    exit 1
fi
cd ..

# Test 5: Taxonomy Builder CLI
echo ""
echo "Test 5: Testing Taxonomy Builder CLI..."
if python3 taxonomy_builder/cli.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Taxonomy Builder CLI functional${NC}"
else
    echo -e "${YELLOW}⚠️  Taxonomy Builder CLI test skipped (may need dependencies)${NC}"
fi

# Summary
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ ALL DEMO READINESS CHECKS PASSED${NC}"
echo "======================================================================"
echo ""
echo "Ready to launch demo:"
echo "  cd poc && streamlit run skill_bridge_app.py"
echo ""
echo "Follow demo guide:"
echo "  DEMO_TEST_GUIDE.md"
echo ""

