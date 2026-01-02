import json
from pathlib import Path

def generate_keywords_summary():
    categories_dir = Path(r'c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\categories')
    clean_files = list(categories_dir.glob('**/data/*_clean.json'))
    
    md_output = "# Сводка ключевых слов (Clean JSON)\n\n"
    
    for clean_file in sorted(clean_files):
        try:
            with open(clean_file, encoding='utf-8') as f:
                data = json.load(f)
            
            slug = data.get('slug', clean_file.parent.parent.name)
            md_output += f"## Категория: {slug}\n\n"
            
            keywords = data.get('keywords', {})
            
            for group_name in ['primary', 'secondary', 'supporting', 'commercial']:
                group_kws = keywords.get(group_name, [])
                if group_kws:
                    md_output += f"### {group_name.capitalize()}\n"
                    for kw in group_kws:
                        vol = kw.get('volume', 0)
                        md_output += f"- {kw['keyword']} (vol: {vol})\n"
                    md_output += "\n"
            
            md_output += "---\n\n"
        except Exception as e:
            md_output += f"Error processing {clean_file}: {e}\n\n"

    output_path = Path(r'c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\ALL_CLEAN_KEYWORDS.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)
    
    print(f"✅ Summary written to {output_path}")

if __name__ == "__main__":
    generate_keywords_summary()
