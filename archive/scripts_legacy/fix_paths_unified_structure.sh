#!/bin/bash
# Unified category structure fix
# Replaces content/categories/{slug} → categories/{slug}

echo "🔧 Fixing category paths to unified structure..."

# Find all .md files and replace paths
find .claude/agents -name "*.md" -type f -exec sed -i 's|content/categories/{\([^}]*\)}|categories/{\1}|g' {} +
find .claude/agents/validators -name "*.md" -type f -exec sed -i 's|content/categories/{\([^}]*\)}|categories/{\1}|g' {} +

# Fix CLAUDE.md
sed -i 's|content/categories/{\([^}]*\)}|categories/{\1}|g' CLAUDE.md

# Fix specific examples with hardcoded slugs
find .claude/agents -name "*.md" -type f -exec sed -i 's|content/categories/aktivnaya-pena|categories/aktivnaya-pena|g' {} +
find .claude/agents/validators -name "*.md" -type f -exec sed -i 's|content/categories/aktivnaya-pena|categories/aktivnaya-pena|g' {} +

echo "✅ Paths updated in all agents and validators"
echo "📋 Summary: content/categories/{slug}/ → categories/{slug}/"
