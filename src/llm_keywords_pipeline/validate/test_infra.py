import os
import sys


def check_structure():
    required_paths = [
        "src/llm_keywords_pipeline",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tests/smoke",
        "tests/fixtures",
        "tests/helpers",
        "tests/conftest.py",
        "docs/testing.md",
        "pytest.ini",
        ".coveragerc",
    ]

    missing = []
    for path in required_paths:
        if not os.path.exists(path):
            missing.append(path)

    if missing:
        print(f"Missing paths: {missing}")
        return False

    print("Directory structure is correct")
    return True


def check_imports():
    try:
        import pytest

        print(f"Pytest available: {pytest.__version__}")
        return True
    except ImportError:
        print("Pytest not installed in current environment")
        return False


if __name__ == "__main__":
    print("Checking test infrastructure...")
    structure_ok = check_structure()
    imports_ok = check_imports()

    if structure_ok:
        sys.exit(0)
    else:
        sys.exit(1)
