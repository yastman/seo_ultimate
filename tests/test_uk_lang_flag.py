"""
Test that all UK skills/agents use --lang uk flag for validation scripts.

This test prevents regression - ensures UK files always use proper language flag.
"""

import re
from pathlib import Path

import pytest

# Scripts that MUST have --lang uk when used in UK context
SCRIPTS_REQUIRING_LANG_UK = [
    "check_keyword_density.py",
    "check_h1_sync.py",
    "check_semantic_coverage.py",
]

# Files that should use --lang uk
UK_FILES = [
    ".claude/agents/uk-content-generator.md",
    ".claude/agents/uk-content-reviewer.md",
    ".claude/agents/uk-quality-gate.md",
    ".claude/skills/uk-content-generator/skill.md",
    ".claude/skills/uk-quality-gate/skill.md",
    ".claude/skills/quality-gate/skill.md",  # Has UK section
]


@pytest.mark.parametrize("filepath", UK_FILES)
def test_uk_files_have_lang_flag(filepath):
    """Each UK file must use --lang uk for relevant scripts when targeting UK content."""
    path = Path(filepath)
    if not path.exists():
        pytest.skip(f"File not found: {filepath}")

    content = path.read_text(encoding="utf-8")

    for script in SCRIPTS_REQUIRING_LANG_UK:
        # Find all usages of the script in bash code blocks or commands
        # Pattern matches: script_name followed by anything on same line
        pattern = rf"python3?\s+scripts/{script}\s+[^\n]+"
        matches = re.findall(pattern, content)

        for match in matches:
            # Only check for --lang uk if command targets UK content
            # (contains uk/ path or is a global UK check)
            is_uk_command = "uk/" in match or "uk_" in match
            # Scripts without path args (like check_h1_sync.py) need context check
            if script in ["check_h1_sync.py", "check_semantic_coverage.py"]:
                # These scripts use --lang flag, check if in UK context
                is_uk_command = (
                    True
                    if "uk-" in filepath or "UK" in content[max(0, content.find(match) - 200) : content.find(match)]
                    else False
                )

            if is_uk_command:
                assert "--lang uk" in match, f"{filepath}: {script} missing --lang uk\nFound: {match}"


def test_no_orphan_uk_validation_without_lang():
    """Grep-style check: no UK path validation without --lang uk."""
    for filepath in UK_FILES:
        path = Path(filepath)
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")

        # Find lines with uk/categories AND check_keyword_density but NO --lang uk
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if "uk/categories" in line and "check_keyword_density" in line:
                assert "--lang uk" in line, f"{filepath}:{i} has UK path but missing --lang uk:\n{line}"
