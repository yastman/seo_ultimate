
import sys
import json
import csv
from pathlib import Path

# Add scripts dir to path to import seo_utils (if needed for slugs)
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

try:
    from seo_utils import slugify
except ImportError:
    def slugify(text):
        return text.lower().replace(' ', '-')

PROJECT_ROOT = Path(r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт")
# CORRECT CSV
CSV_PATH = PROJECT_ROOT / "Структура _Ultimate.csv"
RU_ROOT = PROJECT_ROOT / "categories"
UK_ROOT = PROJECT_ROOT / "uk" / "categories"

def get_csv_categories():
    categories = []
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        return []

    print(f"Reading CSV: {CSV_PATH.name}")
    
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            col0 = row[0].strip()
            
            # Logic to identify categories in this specific CSV format
            # Based on previous file read:
            # L3: <Name>
            # Or <Name>, <Count/Count>, ... (Header lines without L1/L2 prefix)
            
            name = None
            
            if col0.startswith('L3:'):
                name = col0.replace('L3:', '').strip()
            elif col0.startswith('L2:'):
                # Some L2s are categories too if they have content
                name = col0.replace('L2:', '').strip()
            elif col0.startswith('L1:'):
                 pass
            elif len(row) > 1:
                # Check if it looks like a category line: "Name, 5/59, ..."
                # Avoid keywords which usually have numbers in col 2 (Volume)
                # But here col 1 is "kol-vo".
                # Example keyword: "active foam,,1300" -> col1 is empty
                # Example category: "Active Foam,52," -> col1 is 52
                
                count_val = row[1].strip()
                if count_val and not col0.lower() == 'фраза':
                     # If col1 has content, it's likely a category header because keywords have empty col1 in this file (based on previous cat view)
                     # Wait, let's re-verify line 9: "пена для мойки... ,, 1300". Col 1 is empty.
                     # Line 8: "L3: Активная пена,52,". Col 1 is 52.
                     # Line 80: "Омыватель,35,". Col 1 is 35.
                     
                     name = col0
            
            if name:
                # slugify
                # We need simple slugify or from utils. 
                # Ideally we check what the folder name actually IS if it exists?
                # But we want to audit against EXPECTED.
                
                # Check for "Омыватель" -> omyvatel (transliteration needed?)
                # Since we don't have full translit logic here without `transliterate` or `seo_utils` full map
                # We will rely on listing existing folders and matching loosely or just outputting names.
                # Actually `seo_utils` has L3_TO_SLUG which is populated from the OTHER csv.
                # We might need to guess slugs or just check if "slugified" version exists.
                
                slug = slugify(name) # This is rudimentary (just spaces), won't handle cyrillic->latin
                categories.append({'name': name, 'raw_slug': slug})

    return categories

def check_structure():
    print("=== PROJECT AUDIT START ===")
    
    # Get all real directory slugs to compare against
    ru_slugs = {d.name: d.name for d in RU_ROOT.iterdir() if d.is_dir()} if RU_ROOT.exists() else {}
    uk_slugs = {d.name: d.name for d in UK_ROOT.iterdir() if d.is_dir()} if UK_ROOT.exists() else {}
    
    csv_cats = get_csv_categories()
    print(f"Found {len(csv_cats)} potential categories in CSV.")

    print(f"\nExisting RU Directories: {len(ru_slugs)}")
    print(f"Existing UK Directories: {len(uk_slugs)}")
    
    # We can't easily match Russian Name -> Slug without the transliteration logic used originally.
    # So we will list the categories found in CSV and try to see if they map to ANY existing folder.
    # Or just report standard audit on existing folders.
    
    print("\n[AUDIT] Checking existing folders status:")
    
    print(f"{'Slug':<30} | {'RU Clean':<8} | {'RU Meta':<8} | {'RU Cont':<8} | {'UK Meta':<8} | {'UK Cont':<8}")
    print("-" * 90)

    # Union of all known slugs from file system
    all_slugs = set(ru_slugs.keys()) | set(uk_slugs.keys())
    
    issues = []
    
    for slug in sorted(all_slugs):
        ru_path = RU_ROOT / slug
        uk_path = UK_ROOT / slug
        
        ru_clean = (ru_path / "data" / f"{slug}_clean.json").exists() if (ru_path / "data").exists() else False
        ru_meta = (ru_path / "meta" / f"{slug}_meta.json").exists() if (ru_path / "meta").exists() else False
        ru_content = (ru_path / "content" / f"{slug}_ru.md").exists() if (ru_path / "content").exists() else False
        
        uk_meta = (uk_path / "meta" / f"{slug}_meta.json").exists() if (uk_path / "meta").exists() else False
        uk_content = (uk_path / "content" / f"{slug}_uk.md").exists() if (uk_path / "content").exists() else False
        
        res = [
            "OK" if ru_clean else "MISS",
            "OK" if ru_meta else "MISS",
            "OK" if ru_content else "...",
            "OK" if uk_meta else "MISS",
            "OK" if uk_content else "..."
        ]
        
        # Check for critical missing pieces (Init should have Clean+Meta)
        if "MISS" in [res[0], res[1], res[3]]:
             print(f"{slug:<30} | {res[0]:<8} | {res[1]:<8} | {res[2]:<8} | {res[3]:<8} | {res[4]:<8} <--- ISSUE")
             issues.append(slug)
        else:
             print(f"{slug:<30} | {res[0]:<8} | {res[1]:<8} | {res[2]:<8} | {res[3]:<8} | {res[4]:<8}")

    if not issues:
        print("\nSUCCESS: All existing category folders have basic required files (Clean data + Meta).")
    else:
        print(f"\nWARNING: Found {len(issues)} categories with missing base files.")

    # Create report
    with open("AUDIT_REPORT_FULL.md", "w", encoding="utf-8") as f:
        f.write(f"# Project Audit Report\n\n")
        f.write(f"**Date:** 2025-12-31\n")
        f.write(f"**Source CSV:** {CSV_PATH.name}\n\n")
        f.write(f"## Categories Status\n\n")
        f.write(f"Total Folders Found: {len(all_slugs)}\n")
        f.write(f"Issues Found: {len(issues)}\n\n")
        if issues:
            f.write("### Problematic Categories\n")
            for i in issues:
                f.write(f"- {i}\n")
        else:
            f.write("All categories appear healthy structurally.\n")

if __name__ == "__main__":
    check_structure()
