#!/bin/bash
# ============================================================
# ROCK Skills Taxonomy - Validation & Quality Checks
# ============================================================
# Script Name: validate_taxonomy.sh
# Purpose: Run comprehensive quality checks on taxonomy
# Tier: 1 (Master Orchestration)
#
# This script validates:
# 1. MECE score (Mutually Exclusive, Collectively Exhaustive)
# 2. Coverage metrics (% of ROCK skills mapped)
# 3. Specification completeness
# 4. Data integrity checks
# 5. Conflict detection
#
# Usage:
#   ./scripts/validate_taxonomy.sh              # Full validation
#   ./scripts/validate_taxonomy.sh --quick      # Skip LLM analysis
#
# Estimated Time: 10-15 minutes
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
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick]"
            exit 1
            ;;
    esac
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ROCK Skills Taxonomy - Validation                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if database exists
if [ ! -f "taxonomy.db" ]; then
    echo "${RED}✗ Database not found${NC}"
    echo "  Run: ./scripts/refresh_taxonomy.sh"
    exit 1
fi

# 1. Run MECE Validation
echo "${BLUE}[1/5] Running MECE validation...${NC}"
if [ "$QUICK_MODE" = true ]; then
    python3 analysis/pipelines/validate_mece.py --no-llm
else
    python3 analysis/pipelines/validate_mece.py
fi

if [ $? -eq 0 ]; then
    echo "${GREEN}   ✓ MECE validation complete${NC}"
else
    echo "${RED}   ✗ MECE validation failed${NC}"
    exit 1
fi

# 2. Check Coverage
echo ""
echo "${BLUE}[2/5] Checking coverage...${NC}"
python3 -c "
import sqlite3
import sys

try:
    conn = sqlite3.connect('taxonomy.db')
    cursor = conn.cursor()
    
    # Total ROCK skills
    cursor.execute('SELECT COUNT(*) FROM rock_skill_mappings')
    total_rock = cursor.fetchone()[0]
    
    # Mapped skills
    cursor.execute('SELECT COUNT(DISTINCT rock_skill_id) FROM rock_skill_mappings WHERE base_skill_id IS NOT NULL')
    mapped_rock = cursor.fetchone()[0]
    
    # Base skills
    cursor.execute('SELECT COUNT(*) FROM base_skills')
    total_base = cursor.fetchone()[0]
    
    coverage = (mapped_rock / total_rock * 100) if total_rock > 0 else 0
    
    print(f'   • Total ROCK Skills: {total_rock}')
    print(f'   • Mapped ROCK Skills: {mapped_rock}')
    print(f'   • Base Skills: {total_base}')
    print(f'   • Coverage: {coverage:.1f}%')
    
    if coverage < 80:
        print(f'   ⚠️  Coverage below 80%')
        sys.exit(1)
    
    conn.close()
except Exception as e:
    print(f'   ✗ Error checking coverage: {e}')
    sys.exit(1)
" || {
    echo "${YELLOW}   ⚠️  Coverage check issues detected${NC}"
}

echo "${GREEN}   ✓ Coverage check complete${NC}"

# 3. Data Integrity
echo ""
echo "${BLUE}[3/5] Checking data integrity...${NC}"
python3 -c "
import sqlite3
import json

conn = sqlite3.connect('taxonomy.db')
cursor = conn.cursor()

issues = []

# Check for orphaned mappings
cursor.execute('''
    SELECT COUNT(*) FROM rock_skill_mappings 
    WHERE base_skill_id NOT IN (SELECT id FROM base_skills)
''')
orphaned = cursor.fetchone()[0]
if orphaned > 0:
    issues.append(f'Orphaned mappings: {orphaned}')

# Check for base skills with no mappings
cursor.execute('''
    SELECT COUNT(*) FROM base_skills 
    WHERE id NOT IN (SELECT base_skill_id FROM rock_skill_mappings WHERE base_skill_id IS NOT NULL)
''')
unused_base = cursor.fetchone()[0]
if unused_base > 0:
    issues.append(f'Unused base skills: {unused_base}')

# Check for missing required fields
cursor.execute('SELECT COUNT(*) FROM base_skills WHERE name IS NULL OR name = \"\"')
missing_names = cursor.fetchone()[0]
if missing_names > 0:
    issues.append(f'Base skills missing names: {missing_names}')

conn.close()

if issues:
    print('   ⚠️  Issues found:')
    for issue in issues:
        print(f'      • {issue}')
else:
    print('   ✓ No integrity issues')
" || {
    echo "${YELLOW}   ⚠️  Data integrity check could not complete${NC}"
}

echo "${GREEN}   ✓ Data integrity check complete${NC}"

# 4. Specification Completeness
echo ""
echo "${BLUE}[4/5] Checking specification completeness...${NC}"
python3 -c "
import sqlite3

conn = sqlite3.connect('taxonomy.db')
cursor = conn.cursor()

# Check how many base skills have specifications
cursor.execute('''
    SELECT 
        COUNT(DISTINCT base_skill_id) as with_specs,
        (SELECT COUNT(*) FROM base_skills) as total
    FROM specifications
''')
row = cursor.fetchone()
with_specs = row[0] if row else 0
total = row[1] if row else 0

spec_coverage = (with_specs / total * 100) if total > 0 else 0

print(f'   • Base Skills with Specifications: {with_specs}/{total}')
print(f'   • Specification Coverage: {spec_coverage:.1f}%')

if spec_coverage < 50:
    print('   ⚠️  Low specification coverage')

conn.close()
" || {
    echo "${YELLOW}   ⚠️  Specification check could not complete${NC}"
}

echo "${GREEN}   ✓ Specification check complete${NC}"

# 5. Generate Quality Report
echo ""
echo "${BLUE}[5/5] Generating quality report...${NC}"
REPORT_FILE="analysis/reports/quality_report_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p analysis/reports

cat > "$REPORT_FILE" << EOF
═══════════════════════════════════════════════════════════
ROCK Skills Taxonomy - Quality Report
Generated: $(date '+%Y-%m-%d %H:%M:%S')
═══════════════════════════════════════════════════════════

EOF

# Add validation results
if [ -f "taxonomy/validation_report.json" ]; then
    python3 -c "
import json
with open('taxonomy/validation_report.json') as f:
    report = json.load(f)
    print('MECE VALIDATION')
    print('─────────────────────────────────────────────────────────')
    print(f\"MECE Score: {report.get('mece_score', 'N/A')}\")
    print(f\"Base Skills: {report.get('base_skills_count', 'N/A')}\")
    print(f\"Conflicts: {report.get('conflicts_count', 'N/A')}\")
    print()
" >> "$REPORT_FILE" 2>/dev/null || echo "Unable to parse validation report" >> "$REPORT_FILE"
fi

echo "Report saved: $REPORT_FILE"
echo "${GREEN}   ✓ Quality report generated${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  VALIDATION COMPLETE                                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Show summary
if [ -f "taxonomy/validation_report.json" ]; then
    python3 -c "
import json
with open('taxonomy/validation_report.json') as f:
    report = json.load(f)
    mece = report.get('mece_score', 0)
    conflicts = report.get('conflicts_count', 0)
    
    print('📊 Summary:')
    print(f\"   • MECE Score: {mece}\")
    
    if mece >= 0.90:
        print('   ✓ MECE score meets threshold')
    else:
        print('   ⚠️  MECE score below threshold (0.90)')
    
    if conflicts > 0:
        print(f\"   ⚠️  {conflicts} conflicts need resolution\")
        print()
        print('Next Steps:')
        print('  • Resolve conflicts: cd poc && streamlit run skill_bridge_app.py')
    else:
        print('   ✓ No conflicts detected')
" 2>/dev/null
fi

echo ""
echo "Full report: $REPORT_FILE"
echo ""

