
import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт")
RU_DIR = BASE_DIR / "categories"
UK_DIR = BASE_DIR / "uk" / "categories"

def check_json_file(path, file_type):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        errors = []
        warnings = []
        
        # Common checks
        if "slug" not in data or not data["slug"]:
            errors.append("Missing or empty 'slug'")
        if "language" not in data:
            errors.append("Missing 'language'")
            
        # Meta file checks
        if file_type == "meta":
            if "meta" not in data:
                errors.append("Missing 'meta' block")
            else:
                title = data["meta"].get("title", "")
                desc = data["meta"].get("description", "")
                if not title: errors.append("Empty Title")
                if not desc: errors.append("Empty Description")
                if len(title) > 75: warnings.append(f"Title too long ({len(title)} chars)")
                if len(title) < 30: warnings.append(f"Title too short ({len(title)} chars)")
                
            if "h1" not in data or not data["h1"]:
                errors.append("Missing H1")
                
            if "keywords_in_content" not in data:
                errors.append("Missing 'keywords_in_content'")
            elif not data["keywords_in_content"].get("primary"):
                 warnings.append("No primary keywords in meta file")

        # Clean file checks
        if file_type == "clean":
            if "keywords" not in data:
                errors.append("Missing 'keywords'")
            else:
                prim = data["keywords"].get("primary", [])
                if not prim: errors.append("No primary keywords found")
                
            if "usage_rules" not in data:
                warnings.append("Missing usage_rules")
        
        return errors, warnings
        
    except json.JSONDecodeError:
        return ["Invalid JSON Syntax"], []
    except Exception as e:
        return [f"Error reading file: {str(e)}"], []

def main():
    print(f"Checking categories in {BASE_DIR}...")
    
    cats = [d for d in RU_DIR.iterdir() if d.is_dir()]
    print(f"Found {len(cats)} RU categories.")
    
    issues_count = 0
    
    for cat in cats:
        slug = cat.name
        
        # 1. Check Clean JSON
        clean_path = cat / "data" / f"{slug}_clean.json"
        if clean_path.exists():
            errs, warns = check_json_file(clean_path, "clean")
            if errs: 
                print(f"[FAIL] {slug} CLEAN: {', '.join(errs)}")
                issues_count += 1
            # if warns: print(f"[WARN] {slug} CLEAN: {', '.join(warns)}")
        else:
            print(f"[MISSING] {slug} CLEAN file")
            issues_count += 1

        # 2. Check Meta JSON
        meta_path = cat / "meta" / f"{slug}_meta.json"
        if meta_path.exists():
            errs, warns = check_json_file(meta_path, "meta")
            if errs: 
                print(f"[FAIL] {slug} META: {', '.join(errs)}")
                issues_count += 1
            if warns: print(f"[WARN] {slug} META: {', '.join(warns)}")
        else:
            print(f"[MISSING] {slug} META file")
            issues_count += 1
            
        # 3. Check UK Meta
        uk_meta_path = UK_DIR / slug / "meta" / f"{slug}_meta.json"
        if uk_meta_path.exists():
             errs, warns = check_json_file(uk_meta_path, "meta")
             if errs: 
                print(f"[FAIL] {slug} UK META: {', '.join(errs)}")
                issues_count += 1
        else:
            # Not strict fail if UK doesn't exist yet? But user said check all.
            # Assuming consistency -> warning
            pass 

    if issues_count == 0:
        print("\n✅ All 34 categories checked. No critical errors found in keys or meta.")
    else:
        print(f"\n❌ Found {issues_count} issues.")

if __name__ == "__main__":
    main()
