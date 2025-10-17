#!/bin/bash
# ============================================================
# ROCK Skills Taxonomy - Full Refresh Workflow
# ============================================================
# Script Name: refresh_taxonomy.sh
# Purpose: Complete regeneration of taxonomy database
# Tier: 1 (Master Orchestration)
#
# This script runs the complete pipeline:
# 1. Extract base skills from ROCK skills
# 2. Extract specifications from mappings
# 3. Validate MECE and detect conflicts
# 4. Populate database
# 5. Generate summary reports
#
# Usage:
#   ./scripts/refresh_taxonomy.sh              # Full refresh with LLM
#   ./scripts/refresh_taxonomy.sh --no-llm     # Faster, lower quality
#   ./scripts/refresh_taxonomy.sh --test       # Test mode (100 skills)
#
# Estimated Time: 3-5 hours (with LLM)
# Estimated Cost: $40-60 (with LLM) or Free (without)
# ============================================================

set -e  # Exit on error

cd "$(dirname "$0")/.." || exit 1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
USE_LLM=true
TEST_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-llm)
            USE_LLM=false
            shift
            ;;
        --test)
            TEST_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-llm] [--test]"
            exit 1
            ;;
    esac
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ROCK Skills Taxonomy - Full Refresh                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$TEST_MODE" = true ]; then
    echo "${YELLOW}⚠️  TEST MODE: Processing limited dataset${NC}"
    LIMIT_ARG="--limit 100"
    USE_LLM=false
else
    echo "${BLUE}ℹ️  FULL MODE: Processing all skills${NC}"
    LIMIT_ARG=""
fi

if [ "$USE_LLM" = true ]; then
    echo "${GREEN}✓ Using LLM for high-quality extraction${NC}"
    LLM_ARG=""
else
    echo "${YELLOW}⚠️  Skipping LLM (faster but lower quality)${NC}"
    LLM_ARG="--no-llm"
fi

echo ""
echo "────────────────────────────────────────────────────────────"
START_TIME=$(date +%s)

# Create backup if database exists
if [ -f "taxonomy.db" ]; then
    echo "${BLUE}[1/5] Creating backup...${NC}"
    BACKUP_DIR="backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp taxonomy.db "$BACKUP_DIR/taxonomy_backup_$TIMESTAMP.db"
    echo "   ✓ Backup saved: $BACKUP_DIR/taxonomy_backup_$TIMESTAMP.db"
else
    echo "${BLUE}[1/5] No existing database, skipping backup${NC}"
fi

echo ""
echo "${BLUE}[2/5] Extracting base skills...${NC}"
echo "   This may take 2-3 hours with LLM..."
python3 analysis/pipelines/extract_base_skills.py $LLM_ARG $LIMIT_ARG
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ Base skills extraction complete${NC}"
else
    echo "${RED}   ✗ Base skills extraction failed${NC}"
    exit 1
fi

echo ""
echo "${BLUE}[3/5] Extracting specifications...${NC}"
python3 analysis/pipelines/extract_specifications.py $LLM_ARG $LIMIT_ARG
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ Specifications extraction complete${NC}"
else
    echo "${RED}   ✗ Specifications extraction failed${NC}"
    exit 1
fi

echo ""
echo "${BLUE}[4/5] Validating MECE and detecting conflicts...${NC}"
python3 analysis/pipelines/validate_mece.py
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ MECE validation complete${NC}"
else
    echo "${RED}   ✗ MECE validation failed${NC}"
    exit 1
fi

echo ""
echo "${BLUE}[5/5] Generating summary reports...${NC}"
if [ -f "scripts/utils/generate_reports.py" ]; then
    python3 scripts/utils/generate_reports.py
    echo "${GREEN}   ✓ Reports generated${NC}"
else
    echo "${YELLOW}   ⚠️  Report generator not yet implemented${NC}"
fi

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  REFRESH COMPLETE                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  Total Time: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo ""

# Show summary
if [ -f "taxonomy/validation_report.json" ]; then
    echo "📊 Validation Summary:"
    python3 -c "
import json
with open('taxonomy/validation_report.json') as f:
    report = json.load(f)
    print(f\"   • MECE Score: {report.get('mece_score', 'N/A')}\")
    print(f\"   • Base Skills: {report.get('base_skills_count', 'N/A')}\")
    print(f\"   • ROCK Skills Mapped: {report.get('rock_skills_mapped', 'N/A')}\")
    print(f\"   • Conflicts Detected: {report.get('conflicts_count', 'N/A')}\")
" 2>/dev/null || echo "   (Unable to parse report)"
fi

echo ""
echo "Next Steps:"
echo "  1️⃣  Review conflicts: cd poc && streamlit run skill_bridge_app.py"
echo "  2️⃣  Check status: ./scripts/status.sh"
echo "  3️⃣  Validate quality: ./scripts/validate_taxonomy.sh"
echo ""

