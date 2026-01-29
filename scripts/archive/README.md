# Archived Scripts

These scripts have been superseded by unified validators with `--lang` support.

## Archived Files

| File | Replaced By |
|------|-------------|
| `validate_uk.py` | `validate_meta.py --lang uk` |

## Usage

Do not use scripts from this directory. Use the main scripts with appropriate `--lang` parameter.

### Examples

```bash
# Instead of:
python3 scripts/archive/validate_uk.py {slug}

# Use:
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json --lang uk
python3 scripts/validate_meta.py --all  # Auto-detects UK from path
```
