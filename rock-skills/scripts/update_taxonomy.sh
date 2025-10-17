#!/bin/bash
# ============================================================
# ROCK Skills Taxonomy - Incremental Update Workflow
# ============================================================
# Script Name: update_taxonomy.sh
# Purpose: Add new ROCK skills without regenerating everything
# Tier: 1 (Master Orchestration)
#
# This script processes only new or changed skills:
# 1. Identify new skills since last update
# 2. Extract base skills (incremental)
# 3. Extract specifications (new only)
# 4. Validate conflicts with existing taxonomy
# 5. Merge into database
#
# Usage:
#   ./scripts/update_taxonomy.sh                          # Auto-detect new skills
#   ./scripts/update_taxonomy.sh --since 2025-10-15       # Skills added after date
#   ./scripts/update_taxonomy.sh --new-skills data.csv    # Specific file
#
# Estimated Time: 30-60 minutes
# Estimated Cost: $5-10 (proportional to new skills)
# ============================================================

set -e

cd "$(dirname "$0")/.." || exit 1

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
SINCE_DATE=""
NEW_SKILLS_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --since)
            SINCE_DATE="$2"
            shift 2
            ;;
        --new-skills)
            NEW_SKILLS_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--since YYYY-MM-DD] [--new-skills FILE]"
            exit 1
            ;;
    esac
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ROCK Skills Taxonomy - Incremental Update                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if database exists
if [ ! -f "taxonomy.db" ]; then
    echo "${RED}✗ Database not found. Run full refresh first:${NC}"
    echo "  ./scripts/refresh_taxonomy.sh"
    exit 1
fi

# Create backup
echo "${BLUE}[1/5] Creating backup...${NC}"
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp taxonomy.db "$BACKUP_DIR/taxonomy_backup_$TIMESTAMP.db"
echo "   ✓ Backup saved"

# Identify new skills
echo ""
echo "${BLUE}[2/5] Identifying new skills...${NC}"

if [ -n "$NEW_SKILLS_FILE" ]; then
    echo "   Using provided file: $NEW_SKILLS_FILE"
    NEW_SKILLS_ARG="--input $NEW_SKILLS_FILE"
elif [ -n "$SINCE_DATE" ]; then
    echo "   Finding skills added since: $SINCE_DATE"
    NEW_SKILLS_ARG="--since $SINCE_DATE"
else
    echo "   Auto-detecting new skills..."
    NEW_SKILLS_ARG="--incremental"
fi

# Extract base skills (incremental)
echo ""
echo "${BLUE}[3/5] Extracting base skills (incremental)...${NC}"
python3 analysis/pipelines/extract_base_skills.py $NEW_SKILLS_ARG --incremental
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ Base skills extraction complete${NC}"
else
    echo "${RED}   ✗ Extraction failed${NC}"
    exit 1
fi

# Extract specifications
echo ""
echo "${BLUE}[4/5] Extracting specifications...${NC}"
python3 analysis/pipelines/extract_specifications.py $NEW_SKILLS_ARG --new-only
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ Specifications extraction complete${NC}"
else
    echo "${RED}   ✗ Extraction failed${NC}"
    exit 1
fi

# Validate for conflicts
echo ""
echo "${BLUE}[5/5] Validating for conflicts...${NC}"
python3 analysis/pipelines/validate_mece.py --check-new-conflicts
if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ Validation complete${NC}"
else
    echo "${YELLOW}   ⚠️  Conflicts detected - review needed${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  UPDATE COMPLETE                                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Show what was added
if [ -f "taxonomy/update_summary.json" ]; then
    python3 -c "
import json
with open('taxonomy/update_summary.json') as f:
    summary = json.load(f)
    print('📊 Update Summary:')
    print(f\"   • New ROCK Skills: {summary.get('new_skills', 0)}\")
    print(f\"   • New Base Skills: {summary.get('new_base_skills', 0)}\")
    print(f\"   • New Conflicts: {summary.get('new_conflicts', 0)}\")
" 2>/dev/null || echo "   (Summary not available)"
fi

echo ""
echo "Next Steps:"
echo "  • Review changes: ./scripts/status.sh"
if [ -f "taxonomy/conflicts.json" ]; then
    CONFLICTS=$(python3 -c "import json; print(len(json.load(open('taxonomy/conflicts.json'))))" 2>/dev/null || echo "0")
    if [ "$CONFLICTS" != "0" ]; then
        echo "  • Resolve conflicts: cd poc && streamlit run skill_bridge_app.py"
    fi
fi
echo ""

