#!/usr/bin/env python3
"""
DEPRECATED: Use validate_content.py instead.

This script is kept for backwards compatibility only.
All functionality has been migrated to validate_content.py (SSOT).

Migration:
    OLD: python3 scripts/quality_runner.py file.md "keyword" B
    NEW: python3 scripts/validate_content.py file.md "keyword"

---

Quality Runner — Python Orchestrator for Stage 8.1 Quality Checks

Replaces bash quality_check_stage_8_1.sh with Python API calls for:
- Markdown structure (pymarkdownlnt)
- Grammar (language_tool_python)
- Water/Nausea (Natasha via check_water_natasha.py)
- Keyword density (check_simple_v2_md.py)
- NER/Blacklist (check_ner_brands.py) - бренды, города, AI-fluff

Usage:
    python3 scripts/quality_runner.py <file.md> "<keyword>" <tier>

Example:
    python3 scripts/quality_runner.py \\
        categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \\
        "активная пена" \\
        B

Exit codes:
    0 - ALL PASS
    1 - WARNINGS (continue workflow)
    2 - ERRORS (stop workflow)
"""

import sys
import subprocess
from pathlib import Path
from typing import Tuple, Dict, List
import json

# Allow running as `python3 scripts/quality_runner.py` without PYTHONPATH=.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Color codes for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

class QualityCheck:
    def __init__(self, file_path: str, keyword: str, tier: str, skip_grammar: bool = False, skip_water: bool = False, skip_ner: bool = False):
        self.file_path = Path(file_path)
        self.keyword = keyword
        self.tier = tier
        self.skip_grammar = skip_grammar
        self.skip_water = skip_water
        self.skip_ner = skip_ner
        self.results = {
            'markdown': {'status': 'pending', 'errors': []},
            'grammar': {'status': 'skipped' if skip_grammar else 'pending', 'errors': []},
            'water': {'status': 'skipped' if skip_water else 'pending', 'metrics': {}},
            'keywords': {'status': 'pending', 'metrics': {}},
            'ner': {'status': 'skipped' if skip_ner else 'pending', 'findings': {}},
            'commercial': {'status': 'pending', 'markers': {}},
            'seo_structure': {'status': 'pending', 'checks': {}}
        }

        # Validate inputs
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if tier not in ['A', 'B', 'C']:
            raise ValueError(f"Invalid tier: {tier}. Must be A, B, or C")

    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{BLUE}{'='*70}{NC}")
        print(f"{BLUE}{title:^70}{NC}")
        print(f"{BLUE}{'='*70}{NC}\n")

    def print_result(self, check_name: str, status: str, message: str = ""):
        """Print check result with color"""
        if status == 'PASS':
            print(f"✅ {GREEN}{check_name}: PASS{NC}")
        elif status == 'WARN':
            print(f"⚠️  {YELLOW}{check_name}: WARNING{NC}")
        elif status == 'FAIL':
            print(f"❌ {RED}{check_name}: FAIL{NC}")

        if message:
            print(f"   {message}")

    def check_markdown_structure(self) -> Tuple[str, List[str]]:
        """
        Check 1: Markdown structure using pymarkdownlnt

        Returns:
            (status, errors) where status is 'PASS'/'WARN'/'FAIL'
        """
        self.print_header("CHECK 1: Markdown Structure")

        try:
            # Try pymarkdownlnt first (Python API)
            from pymarkdown.api import PyMarkdownApi

            # Create API instance and scan file
            api = PyMarkdownApi()
            scan_result = api.scan_path(str(self.file_path))

            # Check if scan was successful
            if not scan_result or not scan_result.scan_failures:
                self.results['markdown']['status'] = 'PASS'
                self.print_result("Markdown structure", "PASS")
                return ('PASS', [])

            # Parse errors from scan_failures
            errors = []
            for failure in scan_result.scan_failures:
                errors.append(f"{failure.scan_file}:{failure.line_number}:{failure.column_number}: {failure.rule_id} - {failure.rule_description}")

            self.results['markdown']['status'] = 'WARN'
            self.results['markdown']['errors'] = errors

            self.print_result("Markdown structure", "WARN", f"Found {len(errors)} issues")
            for error in errors[:5]:  # Show first 5
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")

            return ('WARN', errors)

        except ImportError:
            # Fallback to markdownlint CLI
            print(f"{YELLOW}pymarkdownlnt not installed, using markdownlint CLI{NC}")

            try:
                result = subprocess.run(
                    ['markdownlint', str(self.file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.results['markdown']['status'] = 'PASS'
                    self.print_result("Markdown structure", "PASS")
                    return ('PASS', [])

                errors = result.stdout.strip().split('\n') if result.stdout else []
                self.results['markdown']['status'] = 'WARN'
                self.results['markdown']['errors'] = errors

                self.print_result("Markdown structure", "WARN", f"Found {len(errors)} issues")
                return ('WARN', errors)

            except FileNotFoundError:
                error_msg = "Neither pymarkdownlnt nor markdownlint CLI found"
                self.results['markdown']['status'] = 'FAIL'
                self.results['markdown']['errors'] = [error_msg]
                self.print_result("Markdown structure", "FAIL", error_msg)
                return ('FAIL', [error_msg])

    def check_grammar(self) -> Tuple[str, List[str]]:
        """
        Check 2: Grammar using language_tool_python
        """
        if self.skip_grammar:
            print(f"\n{BLUE}{'='*70}{NC}")
            print(f"{BLUE}CHECK 2: Grammar & Spelling (SKIPPED){NC}")
            print(f"{BLUE}{'='*70}{NC}\n")
            return ('PASS', [])

        self.print_header("CHECK 2: Grammar & Spelling")

        try:
            import language_tool_python

            # Initialize LanguageTool for Russian
            tool = language_tool_python.LanguageTool('ru-RU')

            # Read file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Remove markdown syntax (basic cleanup)
            import re
            text_clean = re.sub(r'#+\s+', '', text)  # Remove headers
            text_clean = re.sub(r'\*\*(.+?)\*\*', r'\1', text_clean)  # Remove bold
            text_clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text_clean)  # Remove links

            # Check grammar
            matches = tool.check(text_clean)

            if not matches:
                self.results['grammar']['status'] = 'PASS'
                self.print_result("Grammar", "PASS", "No errors found")
                return ('PASS', [])

            # Parse errors
            errors = []
            for match in matches:
                errors.append({
                    'line': match.context,
                    'message': match.message,
                    'rule': match.ruleId,
                    'suggestions': match.replacements[:3]  # Top 3 suggestions
                })

            self.results['grammar']['status'] = 'WARN'
            self.results['grammar']['errors'] = errors

            self.print_result("Grammar", "WARN", f"Found {len(errors)} potential issues")

            # Show first 5 errors with details
            for i, error in enumerate(errors[:5], 1):
                print(f"   {i}. {error['message']}")
                print(f"      Context: {error['line']}")
                if error['suggestions']:
                    print(f"      Suggestions: {', '.join(error['suggestions'])}")

            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")

            return ('WARN', errors)

        except ImportError:
            error_msg = "language_tool_python not installed (pip install language-tool-python)"
            self.results['grammar']['status'] = 'WARN'
            self.results['grammar']['errors'] = [error_msg]
            self.print_result("Grammar", "WARN", error_msg)
            return ('WARN', [error_msg])
        except Exception as e:
            error_msg = f"Grammar check failed: {str(e)}"
            self.results['grammar']['status'] = 'FAIL'
            self.results['grammar']['errors'] = [error_msg]
            self.print_result("Grammar", "FAIL", error_msg)
            return ('FAIL', [error_msg])

    def check_water_nausea(self) -> Tuple[str, Dict]:
        """
        Check 3: Water & Nausea using Natasha (direct import)
        """
        if self.skip_water:
            print(f"\n{BLUE}{'='*70}{NC}")
            print(f"{BLUE}CHECK 3: Water & Nausea (SKIPPED){NC}")
            print(f"{BLUE}{'='*70}{NC}\n")
            return ('PASS', {})

        self.print_header("CHECK 3: Water & Nausea (Natasha)")

        try:
            # Direct import instead of subprocess
            from scripts.check_water_natasha import calculate_metrics_from_text

            # Read file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Call function directly
            result = calculate_metrics_from_text(text)

            if not result:
                error_msg = "No metrics calculated (empty text or no Russian words)"
                self.results['water']['status'] = 'FAIL'
                self.print_result("Water/Nausea", "FAIL", error_msg)
                return ('FAIL', {})

            # Extract metrics
            metrics = {
                'water': result['water_percent'],
                'classic_nausea': result['classic_nausea'],
                'academic_nausea': result['academic_nausea'],
                'lemma_repetition': result['lemma_repetition_index']
            }

            self.results['water']['metrics'] = metrics

            # Tier-aware thresholds (v7.3 Shop Mode) via seo_utils (SSOT)
            from scripts.seo_utils import get_tier_requirements

            tier_req = get_tier_requirements(self.tier)
            water_min = float(tier_req.get('water_min', 40.0))
            water_max = float(tier_req.get('water_max', 60.0))
            water_blocker_low = float(tier_req.get('water_blocker_low', 30.0))
            water_blocker_high = float(tier_req.get('water_blocker_high', water_max + 1.0))

            classic_max = float(tier_req.get('nausea_classic_max', 3.5))
            classic_blocker = float(tier_req.get('nausea_classic_blocker', classic_max + 0.1))

            academic_min = float(tier_req.get('nausea_academic_min', 7.0))
            academic_max = float(tier_req.get('nausea_academic_max', 9.5))

            water_ok = water_min <= metrics['water'] <= water_max
            classic_ok = metrics['classic_nausea'] <= classic_max

            # Academic nausea: < min = INFO (не блокирует), min-max = OK, > 12 = FAIL (по текущей спецификации)
            academic_nausea_fail = metrics['academic_nausea'] > 12.0

            # Blockers (останавливают workflow)
            water_blocker = metrics['water'] < water_blocker_low or metrics['water'] >= water_blocker_high
            classic_blocker_hit = metrics['classic_nausea'] >= classic_blocker

            if academic_nausea_fail or water_blocker or classic_blocker_hit:
                self.results['water']['status'] = 'FAIL'
                self.print_result(
                    "Water/Nausea",
                    "FAIL",
                    f"Water: {metrics['water']:.1f}%, "
                    f"Classic Nausea: {metrics['classic_nausea']:.2f}, "
                    f"Academic Nausea: {metrics['academic_nausea']:.1f}%"
                )
            elif water_ok and classic_ok:
                self.results['water']['status'] = 'PASS'
                self.print_result("Water/Nausea", "PASS")
            else:
                self.results['water']['status'] = 'WARN'
                self.print_result(
                    "Water/Nausea",
                    "WARN",
                    f"Water: {metrics['water']:.1f}%, "
                    f"Classic Nausea: {metrics['classic_nausea']:.2f}, "
                    f"Academic Nausea: {metrics['academic_nausea']:.1f}%"
                )

            # Print metrics
            print(f"   Water: {metrics['water']:.1f}% (target: {water_min:.0f}-{water_max:.0f}%)")
            print(f"   Classic Nausea: {metrics['classic_nausea']:.2f} (target: ≤{classic_max:.1f})")
            print(f"   Academic Nausea: {metrics['academic_nausea']:.1f}% (target: {academic_min:.1f}-{academic_max:.1f}%)")
            print(f"   Lemma Repetition: {metrics['lemma_repetition']:.1f}% (internal)")

            return (self.results['water']['status'], metrics)

        except ImportError as e:
            error_msg = f"Cannot import check_water_natasha: {str(e)}"
            self.results['water']['status'] = 'FAIL'
            self.print_result("Water/Nausea", "FAIL", error_msg)
            return ('FAIL', {})
        except Exception as e:
            error_msg = f"Water/nausea check failed: {str(e)}"
            self.results['water']['status'] = 'FAIL'
            self.print_result("Water/Nausea", "FAIL", error_msg)
            return ('FAIL', {})

    def check_keyword_density(self) -> Tuple[str, Dict]:
        """
        Check 4: Keyword density using check_simple_v2_md.py

        FIXED: Использует JSON-выход для точного парсинга density/coverage

        Returns:
            (status, metrics) where status is 'PASS'/'WARN'/'FAIL'
        """
        self.print_header("CHECK 4: Keyword Density")

        # Call check_simple_v2_md.py script with --json flag
        script_path = Path(__file__).parent / 'check_simple_v2_md.py'

        if not script_path.exists():
            error_msg = f"Script not found: {script_path}"
            self.results['keywords']['status'] = 'FAIL'
            self.print_result("Keyword Density", "FAIL", error_msg)
            return ('FAIL', {})

        try:
            # Run with --json flag for machine-readable output
            result = subprocess.run(
                [sys.executable, str(script_path), str(self.file_path), self.keyword, self.tier, '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse JSON report (more reliable than text parsing)
            json_path = self.file_path.parent / f"{self.file_path.stem}_validation.json"
            metrics = {}

            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)

                    # Extract density/coverage from JSON
                    density_check = json_data.get('checks', {}).get('density_distribution', {})
                    density_metrics = density_check.get('metrics', {})

                    metrics['density'] = density_metrics.get('total_density', 0.0)
                    metrics['coverage'] = density_metrics.get('coverage', 0.0)
                    metrics['keywords_found'] = density_metrics.get('keywords_found', 0)
                    metrics['keywords_total'] = density_metrics.get('keywords_total', 0)
                    metrics['warnings_count'] = density_metrics.get('warnings_count', 0)
                    metrics['errors_count'] = density_metrics.get('errors_count', 0)

                except (json.JSONDecodeError, KeyError) as e:
                    # JSON parsing failed - treat as no data
                    print(f"{YELLOW}⚠️  Warning: Could not parse JSON report: {e}{NC}")
                    self.results['keywords']['status'] = 'WARN'

            else:
                # JSON not generated
                print(f"{RED}❌ JSON report not found: {json_path}{NC}")
                self.results['keywords']['status'] = 'FAIL'
                return ('FAIL', {})

            self.results['keywords']['metrics'] = metrics

            # Check exit code
            if result.returncode == 0:
                self.results['keywords']['status'] = 'PASS'
                self.print_result("Keyword Density", "PASS")
            elif result.returncode == 1:
                self.results['keywords']['status'] = 'WARN'
                self.print_result("Keyword Density", "WARN",
                                f"Density: {metrics.get('density', 'N/A')}%, "
                                f"Coverage: {metrics.get('coverage', 'N/A')}%")
            else:
                self.results['keywords']['status'] = 'FAIL'
                self.print_result("Keyword Density", "FAIL", result.stdout)

            # Print metrics
            print(f"   Density: {metrics.get('density', 'N/A')}% (target: ≤2%)")
            print(f"   Coverage: {metrics.get('coverage', 'N/A')}% (target: 50-60%)")
            if 'keywords_found' in metrics:
                print(f"   Keywords: {metrics['keywords_found']}/{metrics['keywords_total']} found")
            if 'warnings_count' in metrics and metrics['warnings_count'] > 0:
                print(f"   Warnings: {metrics['warnings_count']}")

            return (self.results['keywords']['status'], metrics)

        except Exception as e:
            error_msg = f"Keyword density check failed: {str(e)}"
            self.results['keywords']['status'] = 'FAIL'
            self.print_result("Keyword Density", "FAIL", error_msg)
            return ('FAIL', {})

    def check_ner_blacklist(self) -> Tuple[str, Dict]:
        """
        Check 5: NER & Blacklist — проверка брендов, городов, AI-fluff

        Uses check_ner_brands.py for:
        - Brand mentions (Koch Chemie, Grass, Karcher, etc.)
        - City mentions (Киев, Харьков, Одесса, etc.)
        - AI-fluff phrases ("в этой статье", "давайте разберёмся", etc.)
        - NER entities (ORG, LOC, PER) via Natasha
        """
        if self.skip_ner:
            print(f"\n{BLUE}{'='*70}{NC}")
            print(f"{BLUE}CHECK 5: NER & Blacklist (SKIPPED){NC}")
            print(f"{BLUE}{'='*70}{NC}\n")
            return ('PASS', {})

        self.print_header("CHECK 5: NER & Blacklist (Brands/Cities/AI-fluff)")

        try:
            # Direct import from check_ner_brands
            from scripts.check_ner_brands import check_blacklist, check_ner

            # Read file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Run blacklist check (fast)
            blacklist_results = check_blacklist(text)

            # Run NER check (may be slower)
            ner_results = check_ner(text)

            # Combine findings
            findings = {
                'brands': blacklist_results.get('brands', []),
                'cities': blacklist_results.get('cities', []),
                'ai_fluff': blacklist_results.get('ai_fluff', []),
                'strict_phrases': blacklist_results.get('strict_phrases', []),
                'ner_entities': ner_results.get('ner_entities', [])
            }

            self.results['ner']['findings'] = findings

            # Count issues
            brands_count = len(findings['brands'])
            cities_count = len(findings['cities'])
            ai_fluff_count = len(findings['ai_fluff'])
            strict_count = len(findings['strict_phrases'])
            
            total_issues = brands_count + cities_count + ai_fluff_count + strict_count

            # Print findings
            if findings['strict_phrases']:
                print(f"   ❌ STRICT BLACKLIST (CRITICAL): {strict_count}")
                for item in findings['strict_phrases']:
                    print(f"      • {RED}{item['entity']}{NC}")

            if findings['brands']:
                print(f"   ⚠️  Бренды найдены: {brands_count}")
                for item in findings['brands'][:3]:
                    print(f"      • {item['entity']}")
                if brands_count > 3:
                    print(f"      ... и ещё {brands_count - 3}")

            if findings['cities']:
                print(f"   ⚠️  Города найдены: {cities_count}")
                for item in findings['cities'][:3]:
                    print(f"      • {item['entity']}")
                if cities_count > 3:
                    print(f"      ... и ещё {cities_count - 3}")

            if findings['ai_fluff']:
                print(f"   ⚠️  AI-fluff фразы: {ai_fluff_count}")
                for item in findings['ai_fluff'][:3]:
                    print(f"      • \"{item['entity']}\"")
                if ai_fluff_count > 3:
                    print(f"      ... и ещё {ai_fluff_count - 3}")

            # NER info (informational only)
            ner_orgs = [e for e in findings['ner_entities'] if e.get('type') == 'ORG']
            ner_locs = [e for e in findings['ner_entities'] if e.get('type') == 'LOC']
            if ner_orgs or ner_locs:
                print(f"   ℹ️  NER обнаружил: {len(ner_orgs)} ORG, {len(ner_locs)} LOC")

            # Determine status
            if strict_count > 0:
                self.results['ner']['status'] = 'FAIL'
                self.print_result("NER & Blacklist", "FAIL", f"Found {strict_count} CRITICAL blacklist phrases")
                return ('FAIL', findings)
            elif total_issues == 0:
                self.results['ner']['status'] = 'PASS'
                self.print_result("NER & Blacklist", "PASS", "Запрещённые сущности не найдены")
                return ('PASS', findings)
            else:
                self.results['ner']['status'] = 'WARN'
                self.print_result("NER & Blacklist", "WARN",
                                f"Найдено {total_issues} проблем: {brands_count} брендов, "
                                f"{cities_count} городов, {ai_fluff_count} AI-фраз")
                return ('WARN', findings)

        except ImportError as e:
            error_msg = f"Cannot import check_ner_brands: {str(e)}"
            self.results['ner']['status'] = 'WARN'
            self.print_result("NER & Blacklist", "WARN", error_msg)
            return ('WARN', {})
        except Exception as e:
            error_msg = f"NER check failed: {str(e)}"
            self.results['ner']['status'] = 'WARN'
            self.print_result("NER & Blacklist", "WARN", error_msg)
            return ('WARN', {})

    def _parse_density_text_fallback(self, output: str) -> Dict:
        """
        Fallback text parsing for density/coverage (more robust)

        FIXED: Парсит density и coverage по конкретным строкам, а не глобально

        Args:
            output: stdout from check_simple_v2_md.py

        Returns:
            Dict with density and coverage metrics
        """
        metrics = {}
        import re

        # Split по строкам для точного парсинга
        lines = output.strip().split('\n')

        for line in lines:
            # Density: ищем строку с "Density:" или "Плотность:"
            if 'Density:' in line or 'Плотность:' in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    metrics['density'] = float(match.group(1))

            # Coverage: ищем строку с "Coverage:" или "Покрытие:"
            if 'Coverage:' in line or 'Покрытие:' in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    metrics['coverage'] = float(match.group(1))

        return metrics

    def check_commercial_markers(self) -> Tuple[str, Dict]:
        """
        Check 6: Commercial Markers — проверка коммерческих слов для E-commerce

        SEO v7.3: Текст должен содержать минимум N коммерческих маркеров
        (купить, цена, доставка, заказать и т.д.)
        """
        self.print_header("CHECK 6: Commercial Markers (E-commerce)")

        try:
            # Import from seo_utils
            from scripts.seo_utils import check_commercial_markers, get_tier_requirements

            # Get tier requirements
            tier_req = get_tier_requirements(self.tier)
            min_required = tier_req.get('commercial_min', 3)

            # Read file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Run commercial markers check
            result = check_commercial_markers(text, min_required)

            self.results['commercial']['markers'] = result

            # Print details
            print(f"   Tier {self.tier} требует: минимум {min_required} маркеров")
            print(f"   Найдено: {result['found_count']} маркеров")

            if result['found_markers']:
                print(f"   ✓ Маркеры: {', '.join(result['found_markers'][:6])}")
                if len(result['found_markers']) > 6:
                    print(f"      ... и ещё {len(result['found_markers']) - 6}")

            # Determine status
            if result['passed']:
                self.results['commercial']['status'] = 'PASS'
                self.print_result("Commercial Markers", "PASS", result['message'])
                return ('PASS', result)
            else:
                self.results['commercial']['status'] = 'FAIL'
                self.print_result("Commercial Markers", "FAIL",
                                 f"Найдено {result['found_count']}/{min_required} — добавьте коммерческие слова!")
                return ('FAIL', result)

        except ImportError as e:
            error_msg = f"Cannot import seo_utils: {str(e)}"
            self.results['commercial']['status'] = 'WARN'
            self.print_result("Commercial Markers", "WARN", error_msg)
            return ('WARN', {})
        except Exception as e:
            error_msg = f"Commercial markers check failed: {str(e)}"
            self.results['commercial']['status'] = 'FAIL'
            self.print_result("Commercial Markers", "FAIL", error_msg)
            return ('FAIL', {})

    def check_seo_structure(self) -> Tuple[str, Dict]:
        """
        Check 7: SEO Structure — проверка структурных SEO-требований

        Проверяет:
        - Main keyword в INTRO (первые 150 символов)
        - Keywords в H2 заголовках (минимум 2 из 4)
        - Частота main keyword (3-7 раз, антиспам)
        """
        self.print_header("CHECK 7: SEO Structure (Keyword Placement)")

        try:
            from scripts.check_seo_structure import check_seo_structure

            status, results = check_seo_structure(str(self.file_path), self.keyword)

            self.results['seo_structure']['status'] = status
            self.results['seo_structure']['checks'] = results

            # Print results
            intro = results['intro']
            h2 = results['h2']
            freq = results['frequency']

            # 1. INTRO check
            icon = "✅" if intro['passed'] else "❌"
            print(f"   {icon} INTRO: {intro['message']}")
            if intro['passed'] and not intro['in_first_sentence']:
                print(f"      ⚠️  Лучше переместить keyword в первое предложение")

            # 2. H2 check
            icon = "✅" if h2['passed'] else "⚠️"
            print(f"   {icon} H2: {h2['message']}")
            if h2['h2_with_keyword']:
                print(f"      ✓ С keyword: {', '.join(h2['h2_with_keyword'][:2])}")
            if h2['h2_without_keyword'] and not h2['passed']:
                print(f"      ⚠️  Без keyword: {', '.join(h2['h2_without_keyword'][:2])}")

            # 3. Frequency check
            if freq['status'] == 'OK':
                icon = "✅"
            elif freq['is_spam']:
                icon = "❌"
            else:
                icon = "⚠️"
            print(f"   {icon} Частота: {freq['message']}")

            # Overall result
            if status == 'PASS':
                self.print_result("SEO Structure", "PASS", "Все структурные требования выполнены")
            elif status == 'WARN':
                self.print_result("SEO Structure", "WARN", "Есть замечания по структуре")
            else:
                self.print_result("SEO Structure", "FAIL", "Критические проблемы со структурой")

            return (status, results)

        except ImportError as e:
            error_msg = f"Cannot import check_seo_structure: {str(e)}"
            self.results['seo_structure']['status'] = 'FAIL'
            self.print_result("SEO Structure", "FAIL", error_msg)
            return ('FAIL', {})
        except Exception as e:
            error_msg = f"SEO structure check failed: {str(e)}"
            self.results['seo_structure']['status'] = 'FAIL'
            self.print_result("SEO Structure", "FAIL", error_msg)
            return ('FAIL', {})

    def run_all_checks(self) -> int:
        """
        Run all quality checks (7 total — v7.4 Hybrid)

        Returns:
            Exit code: 0 (PASS), 1 (WARN), 2 (FAIL)
        """
        print(f"\n{GREEN}Starting Quality Checks for: {self.file_path.name}{NC}")
        print(f"Keyword: {self.keyword}")
        print(f"Tier: {self.tier}")
        print(f"SEO Standard: v7.4 (Shop Mode + Structure)")

        # Run checks (7 total — v7.4)
        md_status, _ = self.check_markdown_structure()
        grammar_status, _ = self.check_grammar()
        water_status, _ = self.check_water_nausea()
        keyword_status, _ = self.check_keyword_density()
        ner_status, _ = self.check_ner_blacklist()
        commercial_status, _ = self.check_commercial_markers()
        seo_structure_status, _ = self.check_seo_structure()

        # Summary
        self.print_header("SUMMARY")

        statuses = [md_status, grammar_status, water_status, keyword_status, ner_status, commercial_status, seo_structure_status]
        check_names = ['Markdown', 'Grammar', 'Water/Nausea', 'Keywords', 'NER/Blacklist', 'Commercial', 'SEO Structure']

        # Print individual results
        for name, status in zip(check_names, statuses):
            if status == 'PASS':
                print(f"   ✅ {name}: PASS")
            elif status == 'WARN':
                print(f"   ⚠️  {name}: WARNING")
            else:
                print(f"   ❌ {name}: FAIL")

        print()

        if all(s == 'PASS' for s in statuses):
            print(f"{GREEN}✅ ALL 7 CHECKS PASSED{NC}")
            return 0

        if any(s == 'FAIL' for s in statuses):
            print(f"{RED}❌ SOME CHECKS FAILED{NC}")
            return 2

        print(f"{YELLOW}⚠️  CHECKS PASSED WITH WARNINGS{NC}")
        return 1


def build_parser() -> "argparse.ArgumentParser":
    import argparse

    parser = argparse.ArgumentParser(description="Quality Runner — Python Orchestrator (7 checks — v7.4 Hybrid)")
    parser.add_argument("file_path", help="Path to Markdown file")
    parser.add_argument("keyword", help="Main keyword")
    parser.add_argument("tier", choices=["A", "B", "C"], help="Content Tier (A, B, C)")
    parser.add_argument("--skip-grammar", action="store_true", help="Skip grammar check")
    parser.add_argument("--skip-water", action="store_true", help="Skip water/nausea check")
    parser.add_argument("--skip-ner", action="store_true", help="Skip NER/blacklist check")
    parser.add_argument(
        "--no-write-report",
        action="store_true",
        help="Do not write *_quality_report.json рядом с файлом",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    """Main entry point (returns exit code instead of sys.exit)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        checker = QualityCheck(
            args.file_path,
            args.keyword,
            args.tier,
            skip_grammar=args.skip_grammar,
            skip_water=args.skip_water,
            skip_ner=args.skip_ner,
        )
        exit_code = checker.run_all_checks()

        if not args.no_write_report:
            file_stem = Path(args.file_path).stem
            results_file = Path(args.file_path).parent / f"{file_stem}_quality_report.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(checker.results, f, indent=2, ensure_ascii=False)
            print(f"\n{BLUE}Results saved to: {results_file}{NC}")

        return exit_code

    except Exception as e:
        print(f"\n{RED}ERROR: {str(e)}{NC}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
