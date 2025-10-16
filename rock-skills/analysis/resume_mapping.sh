#!/bin/bash

# Resume LLM Skills Mapping - Batch 10
# This script resumes the mapping process, skipping already-mapped skills

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
OUTPUT_DIR="./outputs/ela_batch_010"
BATCH_SIZE=200
START_INDEX=0  # Will be filtered by skip-existing anyway

echo "======================================================================"
echo "RESUMING LLM SKILLS MAPPING"
echo "======================================================================"
echo "Output Directory: $OUTPUT_DIR"
echo "Batch Size: $BATCH_SIZE skills"
echo "Skipping: llm_skill_mappings.csv (1,600 already mapped)"
echo "======================================================================"
echo ""

# Run the mapping script
python3 scripts/batch_map_skills.py \
    --skills-path rock_schemas/SKILLS.csv \
    --taxonomy-path POC_science_of_reading_literacy_skills_taxonomy.csv \
    --content-area "English Language Arts" \
    --output-dir "$OUTPUT_DIR" \
    --batch-size $BATCH_SIZE \
    --checkpoint-interval 25 \
    --skip-existing llm_skill_mappings.csv \
    2>&1 | tee "${OUTPUT_DIR}/run.log"

echo ""
echo "======================================================================"
echo "BATCH COMPLETE!"
echo "======================================================================"
echo "Check results in: $OUTPUT_DIR"
echo ""

