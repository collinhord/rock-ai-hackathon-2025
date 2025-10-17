#!/bin/bash
# ============================================================
# ROCK Skills Taxonomy - System Status Dashboard
# ============================================================
# Shows current taxonomy status and suggests next actions
# Usage: ./scripts/status.sh

cd "$(dirname "$0")/.." || exit 1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ROCK Skills Taxonomy - System Status                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if taxonomy database exists
if [ -f "taxonomy.db" ]; then
    echo "📊 Database: ✓ Exists"
    
    # Count base skills
    if command -v sqlite3 &> /dev/null; then
        BASE_SKILLS=$(sqlite3 taxonomy.db "SELECT COUNT(*) FROM base_skills" 2>/dev/null || echo "N/A")
        ROCK_SKILLS=$(sqlite3 taxonomy.db "SELECT COUNT(*) FROM rock_skill_mappings" 2>/dev/null || echo "N/A")
        echo "   - Base Skills: $BASE_SKILLS"
        echo "   - ROCK Skills Mapped: $ROCK_SKILLS"
        echo "   - Last Updated: $(date -r taxonomy.db '+%Y-%m-%d %H:%M:%S')"
    else
        echo "   - SQLite not available for detailed stats"
    fi
else
    echo "📊 Database: ✗ Not found"
    echo "   → Run: ./scripts/refresh_taxonomy.sh"
fi

echo ""

# Check for conflicts
if [ -f "taxonomy/conflicts.json" ]; then
    CONFLICTS=$(python3 -c "import json; data=json.load(open('taxonomy/conflicts.json')); print(len(data) if isinstance(data, list) else len(data.get('conflicts', [])))" 2>/dev/null || echo "?")
    if [ "$CONFLICTS" != "0" ] && [ "$CONFLICTS" != "?" ]; then
        echo "⚠️  Conflicts: $CONFLICTS pending resolution"
        echo "   → Run: cd poc && streamlit run skill_bridge_app.py"
        echo "   → Navigate to 'Redundancy Grooming' page"
    else
        echo "✓ Conflicts: None pending"
    fi
else
    echo "📋 Conflicts: Not yet analyzed"
    echo "   → Run: python3 analysis/pipelines/validate_mece.py"
fi

echo ""

# Check MECE score
if [ -f "taxonomy/validation_report.json" ]; then
    MECE=$(python3 -c "import json; print(json.load(open('taxonomy/validation_report.json')).get('mece_score', 'N/A'))" 2>/dev/null || echo "N/A")
    echo "📈 MECE Score: $MECE"
    
    if [ "$MECE" != "N/A" ]; then
        # Check if below threshold (using awk for float comparison)
        BELOW_THRESHOLD=$(awk -v mece="$MECE" 'BEGIN { print (mece < 0.90) ? "yes" : "no" }')
        if [ "$BELOW_THRESHOLD" = "yes" ]; then
            echo "   ⚠️  Below threshold (0.90)"
            echo "   → Review conflicts and refine base skills"
        fi
    fi
else
    echo "📈 MECE Score: Not calculated"
    echo "   → Run: python3 analysis/pipelines/validate_mece.py"
fi

echo ""

# Check for running processes
METADATA_PROCESS=$(ps aux | grep "metadata_extractor.py" | grep -v grep | wc -l | tr -d ' ')
if [ "$METADATA_PROCESS" != "0" ]; then
    echo "🔄 Active Process: Metadata extraction running"
    echo "   → Monitor: tail -f analysis/outputs/metadata_enrichment_full/progress.log"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "NEXT ACTIONS"
echo "════════════════════════════════════════════════════════════"

# Suggest next steps based on state
if [ ! -f "taxonomy.db" ]; then
    echo "  1️⃣  First Time Setup:"
    echo "      cd analysis/pipelines && ./quick_start.sh"
    echo ""
    echo "  2️⃣  Full Data Processing:"
    echo "      ./scripts/refresh_taxonomy.sh"
elif [ ! -f "taxonomy/validation_report.json" ]; then
    echo "  1️⃣  Validate Taxonomy:"
    echo "      python3 analysis/pipelines/validate_mece.py"
    echo ""
    echo "  2️⃣  View in UI:"
    echo "      cd poc && streamlit run skill_bridge_app.py"
else
    echo "  ✓ System Ready"
    echo ""
    echo "  • View UI: cd poc && streamlit run skill_bridge_app.py"
    echo "  • Check Status: ./scripts/status.sh"
    echo "  • Validate Data: ./scripts/validate_taxonomy.sh"
    echo "  • Update Data: ./scripts/refresh_taxonomy.sh"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "DOCUMENTATION"
echo "════════════════════════════════════════════════════════════"
echo "  • Quick Start: cat ../QUICKSTART.md"
echo "  • Full Guide: cat docs/architecture/base-skill-architecture.md"
echo "  • Pipeline Details: cat analysis/README.md"
echo ""

