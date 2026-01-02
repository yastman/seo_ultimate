#!/bin/bash
# ⚠️ DEPRECATED — Redirects to quality_runner.py
#
# This script has been replaced by quality_runner.py
# See: scripts/deprecated/quality_check_stage_8_1.sh for original code

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}⚠️  DEPRECATED: quality_check_stage_8_1.sh${NC}"
echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}This script has been deprecated and replaced by:${NC}"
echo -e "${GREEN}  python3 scripts/quality_runner.py${NC}"
echo ""
echo -e "${BLUE}Reason:${NC}"
echo "  - Missing check_grammar.py dependency"
echo "  - Bash text parsing is fragile"
echo "  - quality_runner.py has better error handling"
echo "  - quality_runner.py supports JSON output"
echo ""
echo -e "${BLUE}New usage:${NC}"
echo -e "  ${GREEN}python3 scripts/quality_runner.py <file> \"<keyword>\" <tier>${NC}"
echo ""
echo -e "${BLUE}Example:${NC}"
echo "  python3 scripts/quality_runner.py \\"
echo "      categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \\"
echo "      \"активная пена\" \\"
echo "      B"
echo ""
echo -e "${YELLOW}Archived version:${NC}"
echo "  scripts/deprecated/quality_check_stage_8_1.sh"
echo ""
echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Auto-redirect if arguments provided (convenience)
if [ $# -ge 3 ]; then
    CATEGORY=$1
    KEYWORD=$2
    TIER=$3
    FILE="categories/$CATEGORY/content/${CATEGORY}_ru.md"

    echo -e "${YELLOW}Auto-redirecting to quality_runner.py...${NC}"
    echo ""

    exec python3 scripts/quality_runner.py "$FILE" "$KEYWORD" "$TIER"
fi

exit 1
