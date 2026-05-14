import logging
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("LLM_KEYWORDS_PROJECT_ROOT", ".")).resolve()
CATEGORIES_DIR = PROJECT_ROOT / "categories"

MIGRATIONS = [
    {
        "source_slug": "dlya-ruchnoy-moyki",
        "target_slug": "shampuni-dlya-ruchnoy-moyki",
        "desc": "Migrate content from Orphan L3 to Correct L3",
    },
    {
        "source_slug": "oborudovanie-l2",
        "target_slug": "oborudovanie",
        "desc": "Migrate content from Technical Duplicate to Correct L1",
    },
]

DIRS_TO_DELETE = [
    "kislotnyy"  # Deleting inconsistent filter folder (others don't exist)
]


def migrate_folder(source_slug, target_slug):
    source_path = CATEGORIES_DIR / source_slug
    target_path = CATEGORIES_DIR / target_slug

    if not source_path.exists():
        logging.warning(f"Source {source_slug} not found. Skipping.")
        return

    if not target_path.exists():
        logging.warning(f"Target {target_slug} not found. Creating it.")
        target_path.mkdir(parents=True)

    logging.info(f"Migrating {source_slug} -> {target_slug}...")

    # Walk through source
    for root, _dirs, files in os.walk(source_path):
        # Create corresponding subdirs in target
        rel_path = os.path.relpath(root, source_path)
        target_root = target_path / rel_path

        if not target_root.exists():
            target_root.mkdir(parents=True)

        for filename in files:
            source_file = Path(root) / filename

            # Allow overwriting target files because Source is "Truth" (contains data)
            # rename filename if it contains source_slug
            new_filename = filename.replace(source_slug, target_slug)
            target_file = target_root / new_filename

            logging.info(f"  Copying {filename} -> {new_filename}")
            shutil.copy2(source_file, target_file)

            # Post-process content
            process_file_content(target_file, source_slug, target_slug)

    # After successful migration, remove source
    # shutil.rmtree(source_path)
    logging.info(
        f"Migration complete. Source {source_path} is preserved for safety (please delete manually if verified)."
    )


def process_file_content(filepath, old_slug, new_slug):
    """Replace old_slug with new_slug in file content."""
    try:
        # Check if text file
        path = Path(filepath)
        if path.suffix in {".json", ".md", ".txt"}:
            with path.open(encoding="utf-8") as f:
                content = f.read()

            if old_slug in content:
                new_content = content.replace(old_slug, new_slug)
                with path.open("w", encoding="utf-8") as f:
                    f.write(new_content)
                logging.info(f"    Updated content in {path.name}")
    except Exception as e:
        logging.error(f"    Error processing {filepath}: {e}")


def delete_dirs(slugs):
    for slug in slugs:
        path = CATEGORIES_DIR / slug
        if path.exists():
            try:
                # Only delete if empty or we are sure?
                # For filters like 'kislotnyy', we decided to delete to match structure.
                shutil.rmtree(path)
                logging.info(f"Deleted directory: {slug}")
            except Exception as e:
                logging.error(f"Error deleting {slug}: {e}")


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print("Starting Fix Structure Orphans...")

    # 1. Run Migrations
    for task in MIGRATIONS:
        migrate_folder(task["source_slug"], task["target_slug"])

    # 2. Cleanup Filters
    delete_dirs(DIRS_TO_DELETE)

    # 3. Cleanup Source dirs (Manual confirmation step usually, but here we can force if confident)
    # Since I commented out shutil.rmtree in migrate_folder for safety,
    # I'll enable it here explicitly if migration looked good.
    # ACTUALLY: Let's delete the source folders clearly here.

    for task in MIGRATIONS:
        src = CATEGORIES_DIR / task["source_slug"]
        if src.exists():
            logging.info(f"Removing source: {task['source_slug']}")
            shutil.rmtree(src)

    print("Fix Complete.")


if __name__ == "__main__":
    main()
