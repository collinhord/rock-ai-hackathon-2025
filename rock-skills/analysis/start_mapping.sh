#!/bin/bash
# Quick launcher for ELA mapping in tmux

echo "🚀 Starting ELA Skills Mapping in tmux..."
echo "============================================================"
echo ""
echo "This will:"
echo "  - Map 2,730 remaining ELA skills"
echo "  - Run 14 batches of 200 skills each"
echo "  - Take approximately 6-7 hours"
echo "  - Cost approximately \$49"
echo ""
echo "Starting tmux session 'ela_mapping'..."
echo ""

# Start tmux with the mapping script
tmux new-session -d -s ela_mapping "cd /Users/collin.hord/Documents/GitHub/rock-ai-hackathon-2025/rock-skills/analysis && ./run_all_ela_batches.sh; echo 'Press Enter to close'; read"

# Attach to the session
echo "✓ Session started! Attaching now..."
echo ""
echo "To detach: Press Ctrl+B, then D"
echo "To reattach: tmux attach -t ela_mapping"
echo ""
sleep 2
tmux attach -t ela_mapping

