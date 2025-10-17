#!/bin/bash
#
# Quick Test Script for Enhanced Base Skill Extraction
#
# This script demonstrates the improved pipeline with Phase 1 enhancements:
# 1. Redundancy-seeded clustering
# 2. Specification discovery
# 3. Quality metrics
# 4. Enhanced MECE validation
#
# Usage:
#   ./quick_test_enhancements.sh [--with-redundancy] [--limit N]

set -e  # Exit on error

# Default settings
LIMIT=50
USE_REDUNDANCY=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --with-redundancy)
      USE_REDUNDANCY=true
      shift
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --with-redundancy    Use redundancy analysis results (better quality)"
      echo "  --limit N            Limit to N skills (default: 50)"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Enhanced Base Skill Extraction - Quick Test${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Configuration:"
echo "  - Skills to process: $LIMIT"
echo "  - Redundancy integration: $([ "$USE_REDUNDANCY" = true ] && echo 'ENABLED' || echo 'DISABLED')"
echo ""

# Check if we're in the right directory
if [ ! -f "$SCRIPT_DIR/test_enhanced_extraction.py" ]; then
    echo -e "${YELLOW}Error: test_enhanced_extraction.py not found${NC}"
    echo "Please run this script from the rock-skills/analysis/pipelines directory"
    exit 1
fi

# Check for required files
INPUT_FILE="$PROJECT_ROOT/rock-skills/rock_data/skill_list_filtered_data_set.csv"
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${YELLOW}Error: Input file not found: $INPUT_FILE${NC}"
    exit 1
fi

# Build command
CMD="python3 test_enhanced_extraction.py --input $INPUT_FILE --limit $LIMIT"

# Add redundancy results if enabled
if [ "$USE_REDUNDANCY" = true ]; then
    REDUNDANCY_FILE="$PROJECT_ROOT/rock-skills/analysis/redundancy/outputs/relationships/relationships_latest.json"
    if [ -f "$REDUNDANCY_FILE" ]; then
        CMD="$CMD --redundancy-results $REDUNDANCY_FILE"
        echo -e "${GREEN}✓ Redundancy results found${NC}"
    else
        echo -e "${YELLOW}⚠ Redundancy results not found, will proceed without it${NC}"
        echo "  (Run redundancy analysis first for better results)"
    fi
fi

# Check for enhanced metadata (optional)
METADATA_FILE=$(ls "$PROJECT_ROOT/rock-skills/analysis/outputs/filtered_enhanced_metadata/skill_metadata_enhanced_"*.csv 2>/dev/null | head -1)
if [ -n "$METADATA_FILE" ]; then
    CMD="$CMD --enhanced-metadata $METADATA_FILE"
    echo -e "${GREEN}✓ Enhanced metadata found${NC}"
fi

# Check for SoR taxonomy (optional)
SOR_FILE="$PROJECT_ROOT/rock-skills/POC_science_of_reading_literacy_skills_taxonomy.csv"
if [ -f "$SOR_FILE" ]; then
    CMD="$CMD --sor-taxonomy $SOR_FILE"
    echo -e "${GREEN}✓ SoR taxonomy found${NC}"
fi

echo ""
echo -e "${BLUE}Running enhanced extraction pipeline...${NC}"
echo ""

# Run the test
cd "$SCRIPT_DIR"
eval $CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}✅ Test completed successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review test results in: analysis/pipelines/test_outputs/"
    echo "  2. Try with more skills: ./quick_test_enhancements.sh --limit 100"
    if [ "$USE_REDUNDANCY" = false ]; then
        echo "  3. Run with redundancy: ./quick_test_enhancements.sh --with-redundancy"
    fi
    echo ""
else
    echo ""
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}⚠️  Test completed with warnings${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo ""
    echo "MECE score may be below target. Consider:"
    echo "  - Running with redundancy: ./quick_test_enhancements.sh --with-redundancy"
    echo "  - Increasing sample size: ./quick_test_enhancements.sh --limit 100"
    echo ""
fi

