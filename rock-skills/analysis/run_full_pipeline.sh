#!/bin/bash
# Complete data pipeline for master concepts generation
# 
# This script orchestrates the full workflow:
# 1. Variant Classification (identifies State A and State B relationships)
# 2. Metadata Enrichment (optional - extracts pedagogical characteristics)
# 3. Master Concepts Generation (creates bridging layer from variant groups)

set -e  # Exit on error

echo "================================================================"
echo "ROCK Skills Master Concepts Pipeline"
echo "================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Variant Classification
echo "Step 1: Running variant classification..."
echo "--------------------------------------------------------"
python3 variant_classifier.py
if [ $? -ne 0 ]; then
    echo "❌ Variant classification failed"
    exit 1
fi
echo "✅ Variant classification complete"
echo ""

# Step 2: Metadata Enrichment (only if needed)
echo "Step 2: Checking metadata enrichment status..."
echo "--------------------------------------------------------"
if [ -f "outputs/skill_metadata_enriched.csv" ]; then
    echo "✅ Metadata enrichment already exists ($(wc -l < outputs/skill_metadata_enriched.csv) skills)"
    echo "   Skipping metadata extraction"
else
    echo "⚠️  Metadata enrichment not found"
    echo ""
    echo "   To add metadata enrichment (text_type, text_mode, skill_domain):"
    echo "   Run: python3 scripts/metadata_extractor.py --content-area 'English Language Arts'"
    echo ""
    echo "   This step is optional but recommended for richer master concepts."
    echo "   Proceeding without metadata enrichment..."
fi
echo ""

# Step 3: Generate Master Concepts
echo "Step 3: Generating master concepts from variant groups..."
echo "--------------------------------------------------------"
python3 scripts/generate_master_concepts.py
if [ $? -ne 0 ]; then
    echo "❌ Master concept generation failed"
    exit 1
fi
echo "✅ Master concepts generated"
echo ""

echo "================================================================"
echo "Pipeline Complete!"
echo "================================================================"
echo ""
echo "📁 Generated files:"
echo "   - analysis/outputs/variant-classification-report.csv"
echo "   - analysis/outputs/progression-chains-summary.csv"
echo "   - analysis/master-concepts.csv"
echo "   - analysis/skill_master_concept_mapping.csv"
echo ""
echo "💡 Next steps:"
echo "   1. Refresh Streamlit app to see new data:"
echo "      cd ../poc && streamlit run skill_bridge_app.py"
echo ""
echo "   2. Optionally run metadata enrichment for enhanced concepts:"
echo "      cd scripts && python3 metadata_extractor.py --content-area 'English Language Arts'"
echo ""
echo "   3. Re-run this pipeline after metadata enrichment:"
echo "      ./run_full_pipeline.sh"
echo ""

