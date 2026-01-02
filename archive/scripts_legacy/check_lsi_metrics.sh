#!/bin/bash
# LSI Metrics Checker — SEO 2025
# Usage: ./check_lsi_metrics.sh <file.md> "<primary_keyword_root>"

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

FILE="$1"
PRIMARY_ROOT="$2"

if [ -z "$FILE" ] || [ -z "$PRIMARY_ROOT" ]; then
    echo "Usage: $0 <file.md> \"<primary_keyword_root>\""
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

echo "=== LSI METRICS REPORT ==="
echo "File: $FILE"
echo ""

# Primary keyword count (case insensitive, Cyrillic)
PRIMARY=$(grep -oiE "${PRIMARY_ROOT}" "$FILE" 2>/dev/null | wc -l)
echo "PRIMARY '$PRIMARY_ROOT': $PRIMARY (target: 3-5)"

# LSI counts
echo ""
echo "LSI SYNONYMS:"
SOSTAV=$(grep -oiE "состав" "$FILE" 2>/dev/null | wc -l)
SREDSTVO=$(grep -oiE "средств" "$FILE" 2>/dev/null | wc -l)
PRODUKT=$(grep -oiE "продукт" "$FILE" 2>/dev/null | wc -l)
FORMULA=$(grep -oiE "формул" "$FILE" 2>/dev/null | wc -l)
KONCENTRAT=$(grep -oiE "концентрат" "$FILE" 2>/dev/null | wc -l)
RASTVOR=$(grep -oiE "раствор" "$FILE" 2>/dev/null | wc -l)
HIMIYA=$(grep -oiE "хими" "$FILE" 2>/dev/null | wc -l)
AVTOHIM=$(grep -oiE "автохими" "$FILE" 2>/dev/null | wc -l)

echo "  состав:     $SOSTAV"
echo "  средств:    $SREDSTVO"
echo "  продукт:    $PRODUKT"
echo "  формул:     $FORMULA"
echo "  концентрат: $KONCENTRAT"
echo "  раствор:    $RASTVOR"
echo "  хими:       $HIMIYA"
echo "  автохими:   $AVTOHIM"

LSI_TOTAL=$((SOSTAV + SREDSTVO + PRODUKT + FORMULA + KONCENTRAT + RASTVOR + HIMIYA + AVTOHIM))
echo ""
echo "LSI TOTAL: $LSI_TOTAL (target: 20-30)"

# Ratio
if [ "$PRIMARY" -gt 0 ]; then
    RATIO=$((LSI_TOTAL / PRIMARY))
    echo "RATIO LSI:Primary: $RATIO:1 (target: >=5:1)"
else
    RATIO=0
    echo "RATIO: N/A (primary=0)"
fi

# Structure
echo ""
echo "STRUCTURE:"
H2=$(grep -cE "^## " "$FILE" 2>/dev/null || echo 0)
FAQ=$(grep -cE "^\*\*.*\?\*\*" "$FILE" 2>/dev/null || echo 0)
LISTS_BULLET=$(grep -cE "^\* " "$FILE" 2>/dev/null || echo 0)
LISTS_NUM=$(grep -cE "^[0-9]+\. " "$FILE" 2>/dev/null || echo 0)
LISTS=$((LISTS_BULLET + LISTS_NUM))
TABLES=$(grep -cE "^\|" "$FILE" 2>/dev/null || echo 0)
CHARS=$(cat "$FILE" | tr -d ' \n\t' | wc -c)

echo "  H2:     $H2 (target: 2-3)"
echo "  FAQ:    $FAQ (target: 4-5)"
echo "  Lists:  $LISTS (target: >=1)"
echo "  Tables: $TABLES"
echo "  Chars:  $CHARS (target: 2500-3500)"

# Status
echo ""
echo "=== STATUS ==="

PASS=true
ISSUES=""

if [ "$PRIMARY" -gt 5 ]; then
    PASS=false
    ISSUES="$ISSUES  - Primary too high: $PRIMARY (max 5)\n"
fi

if [ "$LSI_TOTAL" -lt 20 ]; then
    PASS=false
    ISSUES="$ISSUES  - LSI too low: $LSI_TOTAL (min 20)\n"
fi

if [ "$PRIMARY" -gt 0 ] && [ "$RATIO" -lt 5 ]; then
    PASS=false
    ISSUES="$ISSUES  - Ratio too low: $RATIO:1 (min 5:1)\n"
fi

if [ "$CHARS" -lt 2500 ]; then
    PASS=false
    ISSUES="$ISSUES  - Too short: $CHARS chars (min 2500)\n"
fi

if [ "$CHARS" -gt 3500 ]; then
    PASS=false
    ISSUES="$ISSUES  - Too long: $CHARS chars (max 3500)\n"
fi

if [ "$PASS" = true ]; then
    echo "PASS - Ready for final review"
else
    echo "REVIEW NEEDED:"
    echo -e "$ISSUES"
fi
