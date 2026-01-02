#!/bin/bash
# validate_category.sh
# Проверяет структуру и файлы категории
#
# UPDATED: Использует unified structure categories/{slug}/ (v9.2+)

SLUG="$1"

if [ -z "$SLUG" ]; then
  echo "Usage: $0 <category-slug>"
  echo "Example: $0 aktivnaya-pena"
  exit 1
fi

# Check for jq dependency
if ! command -v jq &> /dev/null; then
  echo "❌ ERROR: 'jq' not found. Install it first:"
  echo "   Ubuntu/Debian: sudo apt install jq"
  echo "   macOS: brew install jq"
  exit 1
fi

# Configuration constants (easy to update)
readonly MIN_GAPS=5
readonly EXPECTED_PROMPTS=3
readonly MIN_SCRAPED=5

# FIXED: Unified structure (v9.2+)
ROOT="categories/$SLUG"

echo "=== Validating category: $SLUG ==="
echo ""

# Check if category folder exists
if [ ! -d "$ROOT" ]; then
  echo "❌ Category folder not found: $ROOT"
  exit 1
fi

# Stage 0: Data Preparation
echo "Stage 0: Data Preparation"
if [ -f "$ROOT/data/${SLUG}.json" ]; then
  # Check JSON validity
  if jq -e '.tier, .keywords, .category_name_ru' "$ROOT/data/${SLUG}.json" > /dev/null 2>&1; then
    tier=$(jq -r '.tier' "$ROOT/data/${SLUG}.json")
    kw_count=$(jq '.keywords | length' "$ROOT/data/${SLUG}.json")
    echo "  ✅ Data JSON exists (Tier: $tier, Keywords: $kw_count)"
  else
    echo "  ⚠️  Data JSON invalid (missing required fields)"
  fi
else
  echo "  ❌ Missing: $ROOT/data/${SLUG}.json"
fi
echo ""

# Stage 1: Competitor Analysis
echo "Stage 1: Competitor Analysis"
if [ -f "$ROOT/competitors/analysis_report.md" ]; then
  gaps=$(grep -c "GAP [0-9]:" "$ROOT/competitors/analysis_report.md" 2>/dev/null || echo 0)
  if [ $gaps -ge $MIN_GAPS ]; then
    echo "  ✅ Analysis report exists ($gaps GAPS identified)"
  else
    echo "  ⚠️  Analysis report exists but insufficient GAPS ($gaps < $MIN_GAPS)"
  fi

  # Count scraped competitors
  scraped_count=$(ls "$ROOT/competitors/scraped/"*.md 2>/dev/null | wc -l)
  if [ $scraped_count -ge $MIN_SCRAPED ]; then
    echo "  ✅ Scraped competitors: $scraped_count"
  else
    echo "  ⚠️  Scraped competitors: $scraped_count (minimum: $MIN_SCRAPED)"
  fi
else
  echo "  ❌ Missing: $ROOT/competitors/analysis_report.md"
fi
echo ""

# Stage 2: Keyword Distribution
echo "Stage 2: Keyword Distribution"
if [ -f "$ROOT/data/${SLUG}_keywords_distributed.json" ]; then
  if jq -e '.keywords.primary, .keywords.secondary, .keywords.supporting' "$ROOT/data/${SLUG}_keywords_distributed.json" > /dev/null 2>&1; then
    primary=$(jq '.keywords.primary | length' "$ROOT/data/${SLUG}_keywords_distributed.json")
    secondary=$(jq '.keywords.secondary | length' "$ROOT/data/${SLUG}_keywords_distributed.json")
    supporting=$(jq '.keywords.supporting | length' "$ROOT/data/${SLUG}_keywords_distributed.json")
    echo "  ✅ Keywords distributed (P: $primary, S: $secondary, Sup: $supporting)"
  else
    echo "  ⚠️  Keywords JSON invalid (missing role categories)"
  fi
else
  echo "  ❌ Missing: $ROOT/data/${SLUG}_keywords_distributed.json"
fi
echo ""

# Stage 3: Perplexity Research
echo "Stage 3: Perplexity Research"
if [ -f "$ROOT/research/perplexity_research.md" ]; then
  prompts=$(grep -c "## PROMPT [1-3]:" "$ROOT/research/perplexity_research.md" 2>/dev/null || echo 0)
  if [ $prompts -eq $EXPECTED_PROMPTS ]; then
    echo "  ✅ Perplexity research complete ($EXPECTED_PROMPTS prompts)"
  else
    echo "  ⚠️  Incomplete research ($prompts prompts, expected $EXPECTED_PROMPTS)"
  fi

  # Check for concrete data
  params=$(grep -E "[0-9]+°C|pH [0-9]|[0-9]+%" "$ROOT/research/perplexity_research.md" 2>/dev/null | wc -l)
  echo "  ✅ Concrete parameters found: $params"
else
  echo "  ❌ Missing: $ROOT/research/perplexity_research.md"
fi
echo ""

# Stage 4: Content Generation (RU)
echo "Stage 4: Content Generation (RU)"
if [ -f "$ROOT/content/${SLUG}_ru.md" ]; then
  words=$(wc -w < "$ROOT/content/${SLUG}_ru.md")
  h2_count=$(grep -c "^## " "$ROOT/content/${SLUG}_ru.md" 2>/dev/null || echo 0)

  # Determine tier requirement
  if [ -f "$ROOT/data/${SLUG}.json" ]; then
    tier=$(jq -r '.tier' "$ROOT/data/${SLUG}.json")
    case $tier in
      A) min_words=1200 ;;
      B) min_words=900 ;;
      C) min_words=700 ;;
      *) min_words=700 ;;
    esac

    if [ $words -ge $min_words ]; then
      echo "  ✅ RU content ($words words, $h2_count H2, Tier $tier: >= $min_words)"
    else
      echo "  ⚠️  RU content too short ($words < $min_words for Tier $tier)"
    fi
  else
    echo "  ✅ RU content ($words words, $h2_count H2)"
  fi
else
  echo "  ❌ Missing: $ROOT/content/${SLUG}_ru.md"
fi
echo ""

# Stage 5: Meta Tags
echo "Stage 5: Meta Tags"
if [ -f "$ROOT/meta/${SLUG}_meta.json" ]; then
  if jq -e '.ru' "$ROOT/meta/${SLUG}_meta.json" > /dev/null 2>&1; then
    ru_count=$(jq '.ru | length' "$ROOT/meta/${SLUG}_meta.json")

    if [ $ru_count -eq 3 ]; then
      echo "  ✅ Meta tags (RU: $ru_count variants)"
    else
      echo "  ⚠️  Meta tags incomplete (RU: $ru_count, expected 3)"
    fi
  else
    echo "  ⚠️  Meta tags JSON invalid (missing ru section)"
  fi
else
  echo "  ❌ Missing: $ROOT/meta/${SLUG}_meta.json"
fi
echo ""

# Stage 6: Packaging
echo "Stage 6: Packaging (Deliverables)"
if [ -d "$ROOT/deliverables" ]; then
  files_count=$(ls "$ROOT/deliverables" 2>/dev/null | wc -l)
  echo "  ✅ Deliverables directory exists ($files_count files)"

  # Check required files
  required_files=("README.md" "QUALITY_REPORT.md" "${SLUG}_ru.md" "${SLUG}_meta.json")
  missing=0

  for file in "${required_files[@]}"; do
    if [ -f "$ROOT/deliverables/$file" ]; then
      echo "    ✅ $file"
    else
      echo "    ❌ $file (missing)"
      missing=$((missing + 1))
    fi
  done

  if [ $missing -eq 0 ]; then
    echo "  ✅ All required files present"
  else
    echo "  ⚠️  Missing $missing required file(s)"
  fi
else
  echo "  ❌ Missing: $ROOT/deliverables/"
fi
echo ""

# Summary
echo "=== Validation Summary ==="
echo ""
echo "Category: $SLUG"
echo "Path: $ROOT"
echo ""

# Count completed stages
completed=0
[ -f "$ROOT/data/${SLUG}.json" ] && completed=$((completed + 1))
[ -f "$ROOT/competitors/analysis_report.md" ] && completed=$((completed + 1))
[ -f "$ROOT/data/${SLUG}_keywords_distributed.json" ] && completed=$((completed + 1))
[ -f "$ROOT/research/perplexity_research.md" ] && completed=$((completed + 1))
[ -f "$ROOT/content/${SLUG}_ru.md" ] && completed=$((completed + 1))
[ -f "$ROOT/meta/${SLUG}_meta.json" ] && completed=$((completed + 1))
[ -d "$ROOT/deliverables" ] && completed=$((completed + 1))

echo "Stages completed: $completed/7"
echo ""

if [ $completed -eq 7 ]; then
  echo "✅ Category is COMPLETE"
  exit 0
elif [ $completed -ge 3 ]; then
  echo "🔄 Category is IN PROGRESS"
  exit 0
else
  echo "⏸️  Category is PENDING (only $completed stages done)"
  exit 0
fi
