#!/bin/bash
# ============================================================
# ROCK Skills Taxonomy - Apply Conflict Resolution Decisions
# ============================================================
# Script Name: apply_decisions.sh
# Purpose: Apply human decisions from Redundancy Grooming UI
# Tier: 1 (Master Orchestration)
#
# This script applies conflict resolution decisions:
# 1. Read decisions from taxonomy/decisions.json
# 2. Merge redundant base skills
# 3. Add new specifications
# 4. Update clarifications
# 5. Regenerate validation report
#
# Usage:
#   ./scripts/apply_decisions.sh                    # Apply all pending
#   ./scripts/apply_decisions.sh --dry-run          # Preview changes
#   ./scripts/apply_decisions.sh --file custom.json # Custom file
#
# Prerequisites:
#   - Make decisions in Streamlit UI (Redundancy Grooming page)
#   - Export decisions to taxonomy/decisions.json
#
# Estimated Time: 5-10 minutes
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
DRY_RUN=false
DECISIONS_FILE="taxonomy/decisions.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --file)
            DECISIONS_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--file FILE]"
            exit 1
            ;;
    esac
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ROCK Skills Taxonomy - Apply Decisions                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if decisions file exists
if [ ! -f "$DECISIONS_FILE" ]; then
    echo "${RED}✗ Decisions file not found: $DECISIONS_FILE${NC}"
    echo ""
    echo "To create decisions:"
    echo "  1. cd poc && streamlit run skill_bridge_app.py"
    echo "  2. Navigate to 'Redundancy Grooming' page"
    echo "  3. Review conflicts and make decisions"
    echo "  4. Export decisions"
    exit 1
fi

# Check if database exists
if [ ! -f "taxonomy.db" ]; then
    echo "${RED}✗ Database not found${NC}"
    echo "  Run: ./scripts/refresh_taxonomy.sh"
    exit 1
fi

# Preview decisions
echo "${BLUE}Preview of decisions to apply:${NC}"
python3 -c "
import json
with open('$DECISIONS_FILE') as f:
    decisions = json.load(f)
    
print(f\"📋 Total Decisions: {len(decisions)}\")
print()

decision_types = {}
for decision in decisions:
    dtype = decision.get('action', 'unknown')
    decision_types[dtype] = decision_types.get(dtype, 0) + 1

for dtype, count in decision_types.items():
    print(f\"   • {dtype}: {count}\")
" 2>/dev/null || {
    echo "${RED}✗ Unable to parse decisions file${NC}"
    exit 1
}

echo ""

if [ "$DRY_RUN" = true ]; then
    echo "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Create backup
echo "${BLUE}[1/4] Creating backup...${NC}"
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp taxonomy.db "$BACKUP_DIR/taxonomy_backup_$TIMESTAMP.db"
echo "   ✓ Backup saved"

# Apply decisions
echo ""
echo "${BLUE}[2/4] Applying decisions...${NC}"

if [ "$DRY_RUN" = true ]; then
    DRY_RUN_ARG="--dry-run"
else
    DRY_RUN_ARG=""
fi

# Check if utility script exists
if [ -f "scripts/utils/apply_decisions.py" ]; then
    python3 scripts/utils/apply_decisions.py --file "$DECISIONS_FILE" $DRY_RUN_ARG
    if [ $? -eq 0 ]; then
        echo "${GREEN}   ✓ Decisions applied${NC}"
    else
        echo "${RED}   ✗ Failed to apply decisions${NC}"
        exit 1
    fi
else
    echo "${YELLOW}   ⚠️  Decision application script not yet implemented${NC}"
    echo "   Creating stub..."
    
    # Create a basic implementation
    mkdir -p scripts/utils
    cat > scripts/utils/apply_decisions.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Apply conflict resolution decisions to taxonomy database.
"""
import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Decisions JSON file')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    args = parser.parse_args()
    
    with open(args.file) as f:
        decisions = json.load(f)
    
    print(f"Loaded {len(decisions)} decisions")
    
    if args.dry_run:
        print("DRY RUN - Would apply:")
        for i, decision in enumerate(decisions, 1):
            action = decision.get('action', 'unknown')
            print(f"  {i}. {action}: {decision.get('description', 'N/A')}")
    else:
        print("Applying decisions...")
        # TODO: Implement actual application logic
        print("⚠️  Decision application not yet fully implemented")
        print("   This requires database schema and merge logic")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
PYTHON_SCRIPT
    
    chmod +x scripts/utils/apply_decisions.py
    python3 scripts/utils/apply_decisions.py --file "$DECISIONS_FILE" $DRY_RUN_ARG
fi

# Regenerate validation
if [ "$DRY_RUN" = false ]; then
    echo ""
    echo "${BLUE}[3/4] Regenerating validation report...${NC}"
    python3 analysis/pipelines/validate_mece.py
    echo "${GREEN}   ✓ Validation complete${NC}"
    
    # Update summary
    echo ""
    echo "${BLUE}[4/4] Generating summary...${NC}"
    if [ -f "scripts/utils/generate_reports.py" ]; then
        python3 scripts/utils/generate_reports.py
        echo "${GREEN}   ✓ Summary generated${NC}"
    else
        echo "${YELLOW}   ⚠️  Report generator not yet implemented${NC}"
    fi
else
    echo ""
    echo "${BLUE}[3/4] Skipping validation (dry run)${NC}"
    echo "${BLUE}[4/4] Skipping summary (dry run)${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
if [ "$DRY_RUN" = true ]; then
    echo "║  DRY RUN COMPLETE                                          ║"
else
    echo "║  DECISIONS APPLIED                                         ║"
fi
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo "Next Steps:"
    echo "  • Check status: ./scripts/status.sh"
    echo "  • View changes: cd poc && streamlit run skill_bridge_app.py"
    echo "  • Archive decisions: mv $DECISIONS_FILE taxonomy/decisions_applied_$TIMESTAMP.json"
fi
echo ""

