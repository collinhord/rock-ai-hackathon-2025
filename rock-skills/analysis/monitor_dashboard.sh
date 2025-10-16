#!/bin/bash
# Real-time Monitoring Dashboard for Batch Mapping

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

STATUS_FILE="./batch_status.json"
MAPPINGS_FILE="./llm_skill_mappings.csv"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Clear screen and show dashboard
show_dashboard() {
    clear
    echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║         ELA SKILLS BATCH MAPPING - LIVE DASHBOARD             ║${NC}"
    echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Check if runner is active
    if ps aux | grep "auto_batch_runner.sh" | grep -v grep > /dev/null || \
       ps aux | grep "batch_map_skills.py" | grep -v grep > /dev/null; then
        echo -e "${GREEN}● STATUS: ACTIVE${NC}"
        RUNNER_PID=$(ps aux | grep -E "auto_batch_runner|batch_map_skills" | grep -v grep | head -1 | awk '{print $2}')
        echo -e "${CYAN}  PID: $RUNNER_PID${NC}"
    else
        echo -e "${YELLOW}○ STATUS: IDLE${NC}"
    fi
    echo ""
    
    # Read status file if exists
    if [ -f "$STATUS_FILE" ]; then
        CURRENT_BATCH=$(jq -r '.current_batch' "$STATUS_FILE" 2>/dev/null || echo "?")
        BATCH_STATUS=$(jq -r '.batch_status' "$STATUS_FILE" 2>/dev/null || echo "unknown")
        SKILLS_IN_BATCH=$(jq -r '.skills_in_batch' "$STATUS_FILE" 2>/dev/null || echo "0")
        TOTAL_MAPPED=$(jq -r '.total_mapped' "$STATUS_FILE" 2>/dev/null || echo "0")
        LAST_UPDATE=$(jq -r '.timestamp' "$STATUS_FILE" 2>/dev/null || echo "N/A")
        
        echo -e "${BOLD}CURRENT BATCH${NC}"
        echo -e "  Batch Number: ${YELLOW}$CURRENT_BATCH${NC} of 14"
        echo -e "  Status: ${CYAN}$BATCH_STATUS${NC}"
        echo -e "  Last Update: $LAST_UPDATE"
        echo ""
    fi
    
    # Overall progress
    TOTAL_MAPPED=$(($(wc -l < "$MAPPINGS_FILE" 2>/dev/null || echo 1) - 1))
    REMAINING=$((3000 - TOTAL_MAPPED))
    PERCENT=$((TOTAL_MAPPED * 100 / 3000))
    
    echo -e "${BOLD}OVERALL PROGRESS${NC}"
    echo -e "  Mapped: ${GREEN}$TOTAL_MAPPED${NC} / 3000 skills"
    echo -e "  Progress: ${YELLOW}$PERCENT%${NC}"
    echo -e "  Remaining: ${CYAN}$REMAINING${NC} skills"
    
    # Progress bar
    FILLED=$((PERCENT / 2))
    echo -n "  ["
    for ((i=0; i<50; i++)); do
        if [ $i -lt $FILLED ]; then
            echo -n "="
        else
            echo -n " "
        fi
    done
    echo -e "] ${PERCENT}%"
    echo ""
    
    # Estimates
    if [ $REMAINING -gt 0 ]; then
        BATCHES_REMAINING=$(( (REMAINING + 199) / 200 ))
        EST_HOURS=$(echo "scale=1; $REMAINING * 9.3 / 3600" | bc 2>/dev/null || echo "?")
        EST_COST=$(echo "scale=2; $REMAINING * 0.00855" | bc 2>/dev/null || echo "?")
        
        echo -e "${BOLD}ESTIMATES${NC}"
        echo -e "  Batches Remaining: ${CYAN}$BATCHES_REMAINING${NC}"
        echo -e "  Time Remaining: ${YELLOW}~${EST_HOURS}h${NC}"
        echo -e "  Cost Remaining: ${GREEN}\$${EST_COST}${NC}"
        echo ""
    fi
    
    # Check current batch progress
    CURRENT_BATCH_DIR=$(ls -td outputs/ela_batch_* 2>/dev/null | head -1)
    if [ -n "$CURRENT_BATCH_DIR" ] && [ -f "$CURRENT_BATCH_DIR"/checkpoint_*.csv ]; then
        CHECKPOINT=$(ls -t "$CURRENT_BATCH_DIR"/checkpoint_*.csv | head -1)
        SKILLS_DONE=$(($(wc -l < "$CHECKPOINT") - 1))
        BATCH_PERCENT=$((SKILLS_DONE * 100 / 200))
        
        echo -e "${BOLD}CURRENT BATCH DETAIL${NC}"
        echo -e "  Skills Mapped: ${GREEN}$SKILLS_DONE${NC} / 200"
        echo -e "  Batch Progress: ${YELLOW}$BATCH_PERCENT%${NC}"
        
        # Batch progress bar
        BATCH_FILLED=$((BATCH_PERCENT / 2))
        echo -n "  ["
        for ((i=0; i<50; i++)); do
            if [ $i -lt $BATCH_FILLED ]; then
                echo -n "#"
            else
                echo -n " "
            fi
        done
        echo -e "] ${BATCH_PERCENT}%"
        
        # Recent activity
        if [ -f "$CURRENT_BATCH_DIR/run.log" ]; then
            echo ""
            echo -e "${BOLD}RECENT ACTIVITY${NC}"
            tail -5 "$CURRENT_BATCH_DIR/run.log" | grep -E "Processing:|Mapped|Checkpoint" | tail -3 | while read line; do
                echo -e "  ${CYAN}${line:0:60}...${NC}"
            done
        fi
    fi
    
    echo ""
    echo -e "${BOLD}${BLUE}────────────────────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}Press Ctrl+C to exit monitor | Refreshing every 5 seconds${NC}"
}

# Continuous monitoring
if [ "$1" == "--once" ]; then
    show_dashboard
else
    while true; do
        show_dashboard
        sleep 5
    done
fi

