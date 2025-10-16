#!/bin/bash
# Automated Batch Runner with Auto-Consolidation and Monitoring
# This script runs all batches sequentially with proper progress tracking

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BATCH_SIZE=200
CHECKPOINT_INTERVAL=25
CONTENT_AREA="English Language Arts"
MAPPINGS_FILE="./llm_skill_mappings.csv"
PROGRESS_FILE="./batch_progress.txt"
STATUS_FILE="./batch_status.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a batch_runner.log
}

# Status update function
update_status() {
    local batch_num=$1
    local status=$2
    local skills_done=$3
    local total_mapped=$4
    
    cat > "$STATUS_FILE" <<EOF
{
  "current_batch": $batch_num,
  "batch_status": "$status",
  "skills_in_batch": $skills_done,
  "total_mapped": $total_mapped,
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "pid": $$
}
EOF
}

# Function to consolidate batch results
consolidate_batch() {
    local batch_dir=$1
    local batch_num=$2
    
    log "${GREEN}Consolidating batch $batch_num results...${NC}"
    
    # Find the mapping file
    MAPPING_FILE=$(ls -t "$batch_dir"/llm_assisted_mappings_*.csv 2>/dev/null | head -1)
    
    if [ ! -f "$MAPPING_FILE" ]; then
        log "${RED}ERROR: No mapping file found for batch $batch_num${NC}"
        return 1
    fi
    
    # Count new mappings
    NEW_MAPPINGS=$(tail -n +2 "$MAPPING_FILE" | wc -l | tr -d ' ')
    
    if [ "$NEW_MAPPINGS" -eq 0 ]; then
        log "${YELLOW}WARNING: No new mappings in batch $batch_num${NC}"
        return 1
    fi
    
    # Backup main file
    BACKUP_FILE="${MAPPINGS_FILE%.csv}_backup_$(date +%Y%m%d_%H%M%S).csv"
    cp "$MAPPINGS_FILE" "$BACKUP_FILE"
    log "  ✓ Backup created: $(basename $BACKUP_FILE)"
    
    # Append new mappings
    tail -n +2 "$MAPPING_FILE" >> "$MAPPINGS_FILE"
    log "  ✓ Added $NEW_MAPPINGS skills to main mappings file"
    
    # Update progress file
    TOTAL_MAPPED=$(($(wc -l < "$MAPPINGS_FILE") - 1))
    echo "$TOTAL_MAPPED" > "$PROGRESS_FILE"
    
    return 0
}

# Function to run a single batch
run_batch() {
    local batch_num=$1
    local start_index=$(( ($batch_num - 1) * $BATCH_SIZE ))
    local output_dir="./outputs/ela_batch_$(printf '%03d' $batch_num)"
    
    log "${YELLOW}============================================================${NC}"
    log "${YELLOW}STARTING BATCH $batch_num${NC}"
    log "${YELLOW}============================================================${NC}"
    log "Start Index: $start_index"
    log "Batch Size: $BATCH_SIZE"
    log "Output: $output_dir"
    log ""
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Update status
    update_status $batch_num "running" 0 $(( $(wc -l < "$MAPPINGS_FILE" 2>/dev/null || echo 1) - 1 ))
    
    # Run batch mapping
    BATCH_START=$(date +%s)
    
    if python3 -B scripts/batch_map_skills.py \
        --start-index $start_index \
        --batch-size $BATCH_SIZE \
        --content-area "$CONTENT_AREA" \
        --checkpoint-interval $CHECKPOINT_INTERVAL \
        --output-dir "$output_dir" \
        --skip-existing "$MAPPINGS_FILE" 2>&1 | tee "$output_dir/run.log"; then
        
        BATCH_STATUS="completed"
        log "${GREEN}✓ Batch $batch_num completed successfully${NC}"
    else
        BATCH_STATUS="failed"
        log "${RED}✗ Batch $batch_num failed${NC}"
        update_status $batch_num "failed" 0 $(( $(wc -l < "$MAPPINGS_FILE" 2>/dev/null || echo 1) - 1 ))
        return 1
    fi
    
    BATCH_END=$(date +%s)
    BATCH_TIME=$(( $BATCH_END - $BATCH_START ))
    BATCH_MINUTES=$(( $BATCH_TIME / 60 ))
    
    # Consolidate results
    if consolidate_batch "$output_dir" $batch_num; then
        TOTAL_MAPPED=$(($(wc -l < "$MAPPINGS_FILE") - 1))
        update_status $batch_num "consolidated" $BATCH_SIZE $TOTAL_MAPPED
        
        # Extract cost from summary
        SUMMARY_FILE=$(ls -t "$output_dir"/mapping_summary_*.txt 2>/dev/null | head -1)
        if [ -f "$SUMMARY_FILE" ]; then
            BATCH_COST=$(grep "Estimated Cost:" "$SUMMARY_FILE" | awk '{print $3}' | tr -d '$')
            log "  ✓ Cost: \$$BATCH_COST"
        fi
        
        log "  ✓ Time: ${BATCH_MINUTES}m"
        log "  ✓ Total mapped: $TOTAL_MAPPED / 3000"
        log ""
        
        return 0
    else
        log "${RED}✗ Failed to consolidate batch $batch_num${NC}"
        update_status $batch_num "consolidation_failed" 0 $(( $(wc -l < "$MAPPINGS_FILE" 2>/dev/null || echo 1) - 1 ))
        return 1
    fi
}

# Main execution
main() {
    log "${BLUE}============================================================${NC}"
    log "${BLUE}AUTOMATED ELA SKILLS BATCH MAPPING${NC}"
    log "${BLUE}============================================================${NC}"
    log ""
    
    # Check starting point
    TOTAL_MAPPED=$(($(wc -l < "$MAPPINGS_FILE" 2>/dev/null || echo 1) - 1))
    REMAINING=$((3000 - TOTAL_MAPPED))
    
    log "Current status:"
    log "  Total mapped: $TOTAL_MAPPED / 3000"
    log "  Remaining: $REMAINING"
    
    if [ $REMAINING -le 0 ]; then
        log "${GREEN}✓ All skills already mapped!${NC}"
        exit 0
    fi
    
    # Calculate starting batch
    START_BATCH=$(( ($TOTAL_MAPPED / $BATCH_SIZE) + 1 ))
    TOTAL_BATCHES=$(( (3000 + $BATCH_SIZE - 1) / $BATCH_SIZE ))
    
    log "  Starting from batch: $START_BATCH"
    log "  Total batches: $TOTAL_BATCHES"
    log ""
    
    # Track overall progress
    OVERALL_START=$(date +%s)
    TOTAL_COST=0
    BATCHES_COMPLETED=0
    
    # Run batches sequentially
    for ((BATCH_NUM=$START_BATCH; BATCH_NUM<=$TOTAL_BATCHES; BATCH_NUM++)); do
        # Check if we've mapped enough
        CURRENT_MAPPED=$(($(wc -l < "$MAPPINGS_FILE") - 1))
        if [ $CURRENT_MAPPED -ge 3000 ]; then
            log "${GREEN}✓ All 3000 skills mapped!${NC}"
            break
        fi
        
        if run_batch $BATCH_NUM; then
            BATCHES_COMPLETED=$((BATCHES_COMPLETED + 1))
            
            # Show progress
            log "${GREEN}Progress: $BATCHES_COMPLETED batches completed${NC}"
            
            # Brief pause between batches
            if [ $BATCH_NUM -lt $TOTAL_BATCHES ]; then
                log "Pausing 5 seconds before next batch..."
                sleep 5
            fi
        else
            log "${RED}Batch $BATCH_NUM failed. Stopping.${NC}"
            log "You can resume by running this script again."
            exit 1
        fi
    done
    
    # Final summary
    OVERALL_END=$(date +%s)
    TOTAL_TIME=$(( $OVERALL_END - $OVERALL_START ))
    TOTAL_HOURS=$(echo "scale=1; $TOTAL_TIME / 3600" | bc)
    FINAL_MAPPED=$(($(wc -l < "$MAPPINGS_FILE") - 1))
    
    log ""
    log "${GREEN}============================================================${NC}"
    log "${GREEN}ALL BATCHES COMPLETE!${NC}"
    log "${GREEN}============================================================${NC}"
    log "Total skills mapped: $FINAL_MAPPED"
    log "Batches completed: $BATCHES_COMPLETED"
    log "Total time: ${TOTAL_HOURS}h"
    log "Main mappings file: $MAPPINGS_FILE"
    log ""
    log "Next steps:"
    log "1. Check status: ./check_batch_status.sh"
    log "2. Restart Streamlit: pkill -f streamlit && cd ../poc && python3 -m streamlit run skill_bridge_app.py --server.headless=true 2>&1 &"
    log "3. Review quality in app: http://localhost:8501"
    log "${GREEN}============================================================${NC}"
    
    # Final status update
    update_status 0 "all_complete" 0 $FINAL_MAPPED
}

# Handle interruption
trap 'log "${YELLOW}Script interrupted. Progress is saved. Run again to resume.${NC}"; exit 130' INT TERM

# Run main
main "$@"

