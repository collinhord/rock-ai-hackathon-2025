#!/bin/bash

# Automated ELA Skills Batch Mapping Runner
# Maps all remaining ELA skills in batches of 200

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BATCH_SIZE=200
CHECKPOINT_INTERVAL=25
CONTENT_AREA="English Language Arts"
MAPPINGS_FILE="./llm_skill_mappings.csv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "AUTOMATED ELA SKILLS BATCH MAPPING"
echo "============================================================"
echo ""

# Count remaining skills
echo "Checking remaining skills..."
REMAINING=$(python3 -c "
import pandas as pd
skills = pd.read_csv('../rock_schemas/SKILLS.csv', usecols=['SKILL_ID', 'CONTENT_AREA_NAME'])
mappings = pd.read_csv('$MAPPINGS_FILE')
ela = skills[skills['CONTENT_AREA_NAME'] == '$CONTENT_AREA']
remaining = ela[~ela['SKILL_ID'].isin(mappings['SKILL_ID'])]
print(len(remaining))
")

echo -e "${GREEN}Remaining ELA skills to map: $REMAINING${NC}"

if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}✓ All ELA skills already mapped!${NC}"
    exit 0
fi

# Calculate number of batches
NUM_BATCHES=$(( ($REMAINING + $BATCH_SIZE - 1) / $BATCH_SIZE ))
echo -e "${BLUE}Will run $NUM_BATCHES batches of $BATCH_SIZE skills each${NC}"
echo ""

# Track overall progress
TOTAL_MAPPED=0
TOTAL_COST=0
START_TIME=$(date +%s)

# Run batches sequentially
for ((BATCH_NUM=1; BATCH_NUM<=$NUM_BATCHES; BATCH_NUM++)); do
    BATCH_START=$(date +%s)
    START_INDEX=$(( ($BATCH_NUM - 1) * $BATCH_SIZE ))
    OUTPUT_DIR="./outputs/ela_batch_$(printf '%03d' $BATCH_NUM)"
    
    echo "============================================================"
    echo -e "${YELLOW}BATCH $BATCH_NUM of $NUM_BATCHES${NC}"
    echo "Start Index: $START_INDEX"
    echo "Batch Size: $BATCH_SIZE"
    echo "Output: $OUTPUT_DIR"
    echo "============================================================"
    echo ""
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Run batch mapping (foreground to avoid hanging)
    python3 -B scripts/batch_map_skills.py \
        --start-index $START_INDEX \
        --batch-size $BATCH_SIZE \
        --content-area "$CONTENT_AREA" \
        --checkpoint-interval $CHECKPOINT_INTERVAL \
        --output-dir "$OUTPUT_DIR" \
        --skip-existing "$MAPPINGS_FILE" \
        2>&1 | tee "$OUTPUT_DIR/run.log"
    
    # Check if batch succeeded
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠ Batch $BATCH_NUM failed or was interrupted${NC}"
        echo "Check log at: $OUTPUT_DIR/run.log"
        exit 1
    fi
    
    # Consolidate mappings
    MAPPING_FILE=$(ls -t "$OUTPUT_DIR"/llm_assisted_mappings_*.csv 2>/dev/null | head -1)
    if [ -f "$MAPPING_FILE" ]; then
        echo ""
        echo "Consolidating batch $BATCH_NUM mappings..."
        
        # Count new mappings
        NEW_MAPPINGS=$(tail -n +2 "$MAPPING_FILE" | wc -l | tr -d ' ')
        
        # Backup main file
        cp "$MAPPINGS_FILE" "${MAPPINGS_FILE%.csv}_backup_$(date +%Y%m%d_%H%M%S).csv"
        
        # Append new mappings
        tail -n +2 "$MAPPING_FILE" >> "$MAPPINGS_FILE"
        
        echo -e "${GREEN}✓ Added $NEW_MAPPINGS skills to main mappings file${NC}"
        TOTAL_MAPPED=$(( $TOTAL_MAPPED + $NEW_MAPPINGS ))
    else
        echo -e "${YELLOW}⚠ No mapping file found for batch $BATCH_NUM${NC}"
    fi
    
    # Extract cost from summary
    SUMMARY_FILE=$(ls -t "$OUTPUT_DIR"/mapping_summary_*.txt 2>/dev/null | head -1)
    if [ -f "$SUMMARY_FILE" ]; then
        BATCH_COST=$(grep "Estimated Cost:" "$SUMMARY_FILE" | awk '{print $3}' | tr -d '$')
        TOTAL_COST=$(python3 -c "print(f'{$TOTAL_COST + $BATCH_COST:.2f}')")
    fi
    
    # Calculate batch time
    BATCH_END=$(date +%s)
    BATCH_TIME=$(( $BATCH_END - $BATCH_START ))
    BATCH_MINUTES=$(( $BATCH_TIME / 60 ))
    
    echo ""
    echo "Batch $BATCH_NUM complete:"
    echo "  - Mapped: $NEW_MAPPINGS skills"
    echo "  - Time: ${BATCH_MINUTES}m"
    echo "  - Cost: \$$BATCH_COST"
    echo ""
    
    # Overall progress
    ELAPSED=$(( $(date +%s) - $START_TIME ))
    ELAPSED_MINUTES=$(( $ELAPSED / 60 ))
    echo "Overall Progress:"
    echo "  - Total mapped: $TOTAL_MAPPED skills"
    echo "  - Batches complete: $BATCH_NUM / $NUM_BATCHES"
    echo "  - Elapsed time: ${ELAPSED_MINUTES}m"
    echo "  - Total cost: \$$TOTAL_COST"
    echo ""
    
    # Brief pause between batches
    if [ $BATCH_NUM -lt $NUM_BATCHES ]; then
        echo "Pausing 5 seconds before next batch..."
        sleep 5
    fi
done

# Final summary
END_TIME=$(date +%s)
TOTAL_TIME=$(( $END_TIME - $START_TIME ))
TOTAL_HOURS=$(python3 -c "print(f'{$TOTAL_TIME / 3600:.1f}')")

echo "============================================================"
echo -e "${GREEN}ALL BATCHES COMPLETE!${NC}"
echo "============================================================"
echo "Total skills mapped: $TOTAL_MAPPED"
echo "Total time: ${TOTAL_HOURS}h"
echo "Total cost: \$$TOTAL_COST"
echo "Main mappings file: $MAPPINGS_FILE"
echo ""
echo "Next steps:"
echo "1. Restart Streamlit to see new mappings"
echo "2. Review mapping quality in the app"
echo "3. Check review queue for low-confidence skills"
echo "============================================================"

