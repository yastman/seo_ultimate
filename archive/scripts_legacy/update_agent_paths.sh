#!/bin/bash
# update_agent_paths.sh
# Updates all agent files with new category-based paths

AGENTS_DIR=".claude/agents"

echo "=== Updating agent paths to content/categories/{slug}/ ==="
echo ""

# Backup agents before modification
BACKUP_DIR="backups/agents_before_path_update_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$AGENTS_DIR" "$BACKUP_DIR/"
echo "✅ Backup created: $BACKUP_DIR"
echo ""

# Define old→new path mappings
declare -A path_mappings=(
    # Data files
    ["content/data/{slug}.json"]="content/categories/{slug}/data/{slug}.json"
    ["content/data/\${slug}.json"]="content/categories/\${slug}/data/\${slug}.json"

    # Keyword distribution
    ["content/data/{slug}_keywords_distributed.json"]="content/categories/{slug}/data/{slug}_keywords_distributed.json"
    ["content/data/\${slug}_keywords_distributed.json"]="content/categories/\${slug}/data/\${slug}_keywords_distributed.json"

    # Competitors
    ["content/data/competitors/{slug}/"]="content/categories/{slug}/competitors/"
    ["content/data/competitors/\${slug}/"]="content/categories/\${slug}/competitors/"
    ["content/data/competitors/{slug}/scraped"]="content/categories/{slug}/competitors/scraped"
    ["content/data/competitors/\${slug}/scraped"]="content/categories/\${slug}/competitors/scraped"
    ["content/data/competitors/{slug}/analysis_report.md"]="content/categories/{slug}/competitors/analysis_report.md"
    ["content/data/competitors/\${slug}/analysis_report.md"]="content/categories/\${slug}/competitors/analysis_report.md"

    # Perplexity research
    ["content/perplexity_results/{slug}_research.md"]="content/categories/{slug}/research/perplexity_research.md"
    ["content/perplexity_results/\${slug}_research.md"]="content/categories/\${slug}/research/perplexity_research.md"

    # Content (tier-based → category-based)
    ["content/tier_{tier}/{slug}.md"]="content/categories/{slug}/content/{slug}_ru.md"
    ["content/tier_\${tier}/{slug}.md"]="content/categories/{slug}/content/{slug}_ru.md"
    ["content/tier_\${tier,,}/{slug}.md"]="content/categories/{slug}/content/{slug}_ru.md"
    ["content/tier_\${tier,,}/\${slug}.md"]="content/categories/\${slug}/content/\${slug}_ru.md"

    # Meta tags
    ["content/meta_tags/{slug}_meta.json"]="content/categories/{slug}/meta/{slug}_meta.json"
    ["content/meta_tags/\${slug}_meta.json"]="content/categories/\${slug}/meta/\${slug}_meta.json"

    # Deliverables
    ["deliverables/{slug}/"]="content/categories/{slug}/deliverables/"
    ["deliverables/\${slug}/"]="content/categories/\${slug}/deliverables/"
)

# Find all agent files
agent_files=$(find "$AGENTS_DIR" -name "*.md" -type f \
    ! -name "ARCHITECTURE*" \
    ! -name "SYSTEM*" \
    ! -name "SHORT_SPEC*")

updated_count=0

for file in $agent_files; do
    filename=$(basename "$file")
    echo "Processing: $filename"

    modified=false

    # Apply all path replacements
    for old_path in "${!path_mappings[@]}"; do
        new_path="${path_mappings[$old_path]}"

        # Check if file contains old path
        if grep -q "$old_path" "$file" 2>/dev/null; then
            # Replace old path with new path
            sed -i "s|$old_path|$new_path|g" "$file"
            modified=true
        fi
    done

    if [ "$modified" = true ]; then
        echo "  ✅ Updated paths in $filename"
        updated_count=$((updated_count + 1))
    else
        echo "  ⏭️  No old paths found in $filename"
    fi
done

echo ""
echo "=== Update Complete ==="
echo "Files updated: $updated_count"
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Verify changes:"
echo "  grep -r 'content/data/' .claude/agents/ --include='*.md'"
echo "  grep -r 'content/tier_' .claude/agents/ --include='*.md'"
echo ""
echo "✅ All agents updated with new category-based paths"
