#!/bin/bash
# Real-time Batch Mapping Status Monitor

ANALYSIS_DIR="/Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/analysis"
cd "$ANALYSIS_DIR"

echo "============================================================"
echo "BATCH MAPPING STATUS MONITOR"
echo "============================================================"
echo ""
date
echo ""

# Check if process is running
if ps aux | grep "batch_map_skills" | grep -v grep > /dev/null; then
    echo "✅ BATCH PROCESS: RUNNING"
    BATCH_PID=$(ps aux | grep "batch_map_skills" | grep -v grep | awk '{print $2}')
    echo "   PID: $BATCH_PID"
    
    # Find which batch is running
    BATCH_DIR=$(ps aux | grep "batch_map_skills" | grep -v grep | grep -oE "ela_batch_[0-9]+" | head -1)
    if [ -n "$BATCH_DIR" ]; then
        echo "   Batch: $BATCH_DIR"
        BATCH_PATH="./outputs/$BATCH_DIR"
        
        # Check checkpoint for progress
        if [ -f "$BATCH_PATH"/checkpoint_*.csv ]; then
            CHECKPOINT=$(ls -t "$BATCH_PATH"/checkpoint_*.csv | head -1)
            SKILLS_DONE=$(($(wc -l < "$CHECKPOINT") - 1))
            echo "   Skills mapped: $SKILLS_DONE / 200"
            PERCENT=$((SKILLS_DONE * 100 / 200))
            echo "   Progress: ${PERCENT}%"
            
            # Show last update time
            LAST_UPDATE=$(stat -f "%Sm" -t "%H:%M:%S" "$CHECKPOINT" 2>/dev/null || stat -c "%y" "$CHECKPOINT" 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1)
            echo "   Last update: $LAST_UPDATE"
            
            # Estimate time remaining
            START_TIME=$(stat -f "%B" "$CHECKPOINT" 2>/dev/null || stat -c "%Y" "$CHECKPOINT" 2>/dev/null)
            CURRENT_TIME=$(date +%s)
            ELAPSED=$((CURRENT_TIME - START_TIME))
            if [ $SKILLS_DONE -gt 0 ]; then
                TIME_PER_SKILL=$((ELAPSED / SKILLS_DONE))
                REMAINING_SKILLS=$((200 - SKILLS_DONE))
                TIME_REMAINING=$((TIME_PER_SKILL * REMAINING_SKILLS))
                MINUTES_REMAINING=$((TIME_REMAINING / 60))
                echo "   Est. time remaining: ${MINUTES_REMAINING} minutes"
            fi
        else
            echo "   Status: Initializing (loading embeddings...)"
        fi
        
        # Show recent log output
        if [ -f "$BATCH_PATH/run.log" ]; then
            echo ""
            echo "Recent activity:"
            tail -10 "$BATCH_PATH/run.log" | grep -E "Processing:|Mapped|Checkpoint" | tail -3
        fi
    fi
else
    echo "❌ BATCH PROCESS: NOT RUNNING"
    
    # Check if last batch completed
    LAST_BATCH=$(ls -td outputs/ela_batch_* 2>/dev/null | head -1)
    if [ -n "$LAST_BATCH" ]; then
        echo ""
        echo "Last batch: $(basename $LAST_BATCH)"
        if [ -f "$LAST_BATCH"/mapping_summary_*.txt ]; then
            echo ""
            echo "Last batch summary:"
            cat "$LAST_BATCH"/mapping_summary_*.txt | head -10
        fi
    fi
fi

echo ""
echo "------------------------------------------------------------"
echo "OVERALL PROGRESS"
echo "------------------------------------------------------------"

# Count total mapped skills
TOTAL_MAPPED=$(($(wc -l < llm_skill_mappings.csv) - 1))
echo "Total mapped: $TOTAL_MAPPED / 3000 ELA skills"
OVERALL_PERCENT=$((TOTAL_MAPPED * 100 / 3000))
echo "Overall progress: ${OVERALL_PERCENT}%"

# Calculate remaining
REMAINING=$((3000 - TOTAL_MAPPED))
echo "Remaining: $REMAINING skills"

if [ $REMAINING -gt 0 ]; then
    BATCHES_REMAINING=$(( (REMAINING + 199) / 200 ))
    echo "Batches remaining: $BATCHES_REMAINING"
    
    # Estimate total time and cost
    EST_HOURS=$(echo "scale=1; $REMAINING * 9.3 / 3600" | bc)
    EST_COST=$(echo "scale=2; $REMAINING * 0.00855" | bc)
    echo "Est. time remaining: ${EST_HOURS}h"
    echo "Est. cost remaining: \$${EST_COST}"
fi

echo ""
echo "============================================================"
echo "Commands:"
echo "  Watch progress: watch -n 10 ./check_batch_status.sh"
echo "  View log: tail -f outputs/ela_batch_*/run.log"
echo "  Kill batch: pkill -f batch_map_skills"
echo "============================================================"

