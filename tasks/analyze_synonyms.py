import json
import os
import re
from collections import defaultdict

# Configuration
CATEGORIES_DIR = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\categories"
REPORT_FILE = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\tasks\synonym_cleanup_report.md"

# Synonyms for normalization
AUTO_SYNONYMS = ["авто", "автомобиля", "машины", "машина", "автомобиль", "в авто", "для авто"]
STOP_WORDS = ["для", "в", "на"]

def normalize_keyword(keyword):
    """
    Creates a canonical form of the keyword for comparison.
    1. Lowercase
    2. Remove 'avto' related words (to handle 'polirovka avto' == 'polirovka')
    3. Sort words (to handle 'pasta polirovochnaya' == 'polirovochnaya pasta')
    """
    text = keyword.lower()
    
    # 1. Remove specific auto terms to catch "body" == "body auto"
    # We replace them with empty string to ignore them in comparison
    for syn in AUTO_SYNONYMS:
        text = text.replace(syn, "")
    
    # 2. Remove stop words
    for sw in STOP_WORDS:
        # distinct word replacement to avoid breaking inside words
        text = re.sub(rf"\b{sw}\b", "", text)
        
    # 3. Clean up spaces
    words = [w for w in re.split(r'\s+', text) if w.strip()]
    
    # 4. Handle specific stemming/variations (simple rules)
    # "polirovochnaya" vs "polirovalnaya" -> "polir"
    normalized_words = []
    for w in words:
        if w.startswith("полиров") or w.startswith("полирал"):
            normalized_words.append("полир")
        elif w.startswith("очистит"):
            normalized_words.append("очист")
        else:
            normalized_words.append(w)
            
    # 5. Sort to handle word order
    normalized_words.sort()
    
    return " ".join(normalized_words)

def analyze_category(category_path):
    json_path = os.path.join(category_path, "data", f"{os.path.basename(category_path)}_clean.json")
    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return None

    keywords_flat = []
    
    # Flatten all keywords with metadata
    sections = ['primary', 'secondary', 'supporting', 'commercial']
    for section in sections:
        if section in data.get('keywords', {}):
            for k in data['keywords'][section]:
                k['original_section'] = section
                keywords_flat.append(k)

    # Group by normalized key
    clusters = defaultdict(list)
    for k in keywords_flat:
        norm = normalize_keyword(k['keyword'])
        if not norm: # If empty (e.g. just "avto"), use original
             norm = k['keyword'].lower()
        clusters[norm].append(k)

    # Logic to select winner and losers
    proposed_changes = []
    
    for norm, group in clusters.items():
        if len(group) < 2:
            continue
            
        # Sort group to find winner:
        # 1. Volume (desc)
        # 2. Length (asc) - preference for shorter "kuzov" vs "kuzov avto" if volumes equal?
        #    Wait, prompt said: "kuzov (20) vs kuzov avto (20) -> keep short".
        #    "polirovochnaya (1600) vs polirovalnaya (20) -> keep high volume".
        # So: Primary sort key is Volume (desc). Secondary is Length (asc).
        
        group.sort(key=lambda x: (-x.get('volume', 0), len(x['keyword'])))
        
        winner = group[0]
        losers = group[1:]
        
        # Check if we should actually merge.
        # If the normalized key is too aggressive, we might merge wrong things.
        # But for valid synonyms, we proceed.
        
        change_record = {
            "winner": winner,
            "losers": losers,
            "norm_key": norm
        }
        proposed_changes.append(change_record)
        
    return {
        "slug": data.get('slug', os.path.basename(category_path)),
        "changes": proposed_changes,
        "total_keywords": len(keywords_flat)
    }

def generate_report():
    report_lines = ["# Synonym Cleanup Report\n"]
    report_lines.append("| Category | Total Keys | Clusters Found | Details |")
    report_lines.append("|---|---|---|---|")
    
    cats = sorted(os.listdir(CATEGORIES_DIR))
    
    for cat in cats:
        cat_path = os.path.join(CATEGORIES_DIR, cat)
        if not os.path.isdir(cat_path):
            continue
            
        result = analyze_category(cat_path)
        if not result or not result['changes']:
            continue
            
        # Detailed breakdown for this category
        details_str = "<br>".join([
            f"**Keep**: `{c['winner']['keyword']}` ({c['winner']['volume']}) <br> **Drop**: " +
            ", ".join([f"`{l['keyword']}` ({l['volume']})" for l in c['losers']])
            for c in result['changes']
        ])
        
        report_lines.append(f"| {result['slug']} | {result['total_keywords']} | {len(result['changes'])} | {details_str} |")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"Report generated at {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
