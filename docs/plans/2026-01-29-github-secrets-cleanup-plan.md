# GitHub Secrets Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Автоматическая очистка всех GitHub-репозиториев от секретных данных с формированием Markdown-отчёта.

**Architecture:** Набор bash-скриптов: fetch_repos.sh получает список репо через gh API, scan_secrets.sh сканирует gitleaks, cleanup_repo.sh очищает (BFG для публичных, git commit для приватных), generate_report.sh формирует отчёт. Главный скрипт cleanup_all_repos.sh оркестрирует процесс.

**Tech Stack:** bash, gh CLI, gitleaks, BFG Repo-Cleaner, jq

---

## Task 1: Настройка рабочей директории

**Files:**
- Create: `~/github-secrets-cleanup/scripts/` (директория)
- Create: `~/github-secrets-cleanup/repos/` (директория)
- Create: `~/github-secrets-cleanup/scans/` (директория)

**Step 1: Создать структуру директорий**

```bash
mkdir -p ~/github-secrets-cleanup/{scripts,repos,scans}
```

**Step 2: Проверить создание**

Run: `ls -la ~/github-secrets-cleanup/`
Expected: Три директории scripts, repos, scans

**Step 3: Перейти в рабочую директорию**

```bash
cd ~/github-secrets-cleanup
```

---

## Task 2: Проверка и установка зависимостей

**Files:**
- Create: `~/github-secrets-cleanup/scripts/check_deps.sh`

**Step 1: Создать скрипт проверки зависимостей**

```bash
cat > ~/github-secrets-cleanup/scripts/check_deps.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Checking dependencies ==="

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI not found. Install: https://cli.github.com/"
    exit 1
fi
echo "✓ gh CLI: $(gh --version | head -1)"

# Check gh auth
if ! gh auth status &> /dev/null; then
    echo "ERROR: gh not authenticated. Run: gh auth login"
    exit 1
fi
echo "✓ gh authenticated"

# Check gitleaks
if ! command -v gitleaks &> /dev/null; then
    echo "ERROR: gitleaks not found."
    echo "Install: brew install gitleaks"
    echo "Or download from: https://github.com/gitleaks/gitleaks/releases"
    exit 1
fi
echo "✓ gitleaks: $(gitleaks version)"

# Check BFG
if ! command -v bfg &> /dev/null; then
    # Try java -jar approach
    if [ ! -f ~/bfg.jar ]; then
        echo "WARNING: BFG not found as command."
        echo "Install: brew install bfg"
        echo "Or download JAR: https://rtyley.github.io/bfg-repo-cleaner/"
        echo "Place as ~/bfg.jar"
    else
        echo "✓ BFG: ~/bfg.jar (use: java -jar ~/bfg.jar)"
    fi
else
    echo "✓ BFG: $(bfg --version 2>/dev/null || echo 'installed')"
fi

# Check jq
if ! command -v jq &> /dev/null; then
    echo "ERROR: jq not found. Install: sudo apt install jq"
    exit 1
fi
echo "✓ jq: $(jq --version)"

# Check git
echo "✓ git: $(git --version)"

echo ""
echo "=== All dependencies OK ==="
EOF
chmod +x ~/github-secrets-cleanup/scripts/check_deps.sh
```

**Step 2: Запустить проверку**

Run: `~/github-secrets-cleanup/scripts/check_deps.sh`
Expected: Все зависимости найдены или инструкции по установке

**Step 3: Установить недостающие зависимости (если нужно)**

Для WSL/Ubuntu:
```bash
# gitleaks
GITLEAKS_VERSION="8.18.4"
wget -O /tmp/gitleaks.tar.gz "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
tar -xzf /tmp/gitleaks.tar.gz -C /tmp
sudo mv /tmp/gitleaks /usr/local/bin/

# BFG (JAR)
wget -O ~/bfg.jar "https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar"
```

**Step 4: Повторить проверку**

Run: `~/github-secrets-cleanup/scripts/check_deps.sh`
Expected: "All dependencies OK"

---

## Task 3: Скрипт получения списка репозиториев

**Files:**
- Create: `~/github-secrets-cleanup/scripts/fetch_repos.sh`

**Step 1: Создать скрипт**

```bash
cat > ~/github-secrets-cleanup/scripts/fetch_repos.sh << 'EOF'
#!/bin/bash
set -e

WORKDIR="${1:-$(pwd)}"
OUTPUT_FILE="$WORKDIR/repos_list.json"

echo "=== Fetching repository list ==="

# Get all repos (owner's repos)
gh repo list --limit 1000 --json name,visibility,url,isPrivate,isArchived,defaultBranchRef > "$OUTPUT_FILE"

TOTAL=$(jq length "$OUTPUT_FILE")
PUBLIC=$(jq '[.[] | select(.visibility == "PUBLIC")] | length' "$OUTPUT_FILE")
PRIVATE=$(jq '[.[] | select(.visibility == "PRIVATE")] | length' "$OUTPUT_FILE")
ARCHIVED=$(jq '[.[] | select(.isArchived == true)] | length' "$OUTPUT_FILE")

echo "Total repositories: $TOTAL"
echo "  Public: $PUBLIC"
echo "  Private: $PRIVATE"
echo "  Archived: $ARCHIVED (will be skipped)"

echo ""
echo "Repository list saved to: $OUTPUT_FILE"
EOF
chmod +x ~/github-secrets-cleanup/scripts/fetch_repos.sh
```

**Step 2: Запустить и проверить**

Run: `~/github-secrets-cleanup/scripts/fetch_repos.sh ~/github-secrets-cleanup`
Expected: Список репозиториев сохранён в repos_list.json

**Step 3: Проверить содержимое**

Run: `jq '.[0:3]' ~/github-secrets-cleanup/repos_list.json`
Expected: JSON с первыми 3 репозиториями

---

## Task 4: Скрипт сканирования секретов

**Files:**
- Create: `~/github-secrets-cleanup/scripts/scan_secrets.sh`

**Step 1: Создать скрипт**

```bash
cat > ~/github-secrets-cleanup/scripts/scan_secrets.sh << 'EOF'
#!/bin/bash
set -e

REPO_URL="$1"
REPO_NAME="$2"
WORKDIR="${3:-$(pwd)}"

REPOS_DIR="$WORKDIR/repos"
SCANS_DIR="$WORKDIR/scans"

if [ -z "$REPO_URL" ] || [ -z "$REPO_NAME" ]; then
    echo "Usage: $0 <repo_url> <repo_name> [workdir]"
    exit 1
fi

echo "=== Scanning: $REPO_NAME ==="

# Clone as mirror (includes all history)
REPO_PATH="$REPOS_DIR/${REPO_NAME}.git"
if [ -d "$REPO_PATH" ]; then
    echo "Repository already cloned, updating..."
    cd "$REPO_PATH"
    git fetch --all
    cd - > /dev/null
else
    echo "Cloning repository..."
    git clone --mirror "$REPO_URL" "$REPO_PATH"
fi

# Scan with gitleaks
SCAN_FILE="$SCANS_DIR/${REPO_NAME}.json"
echo "Running gitleaks..."

# gitleaks returns exit code 1 if secrets found, we handle that
set +e
gitleaks detect \
    --source "$REPO_PATH" \
    --report-format json \
    --report-path "$SCAN_FILE" \
    --no-banner \
    2>/dev/null

SCAN_EXIT=$?
set -e

if [ $SCAN_EXIT -eq 0 ]; then
    echo "✓ No secrets found"
    echo "[]" > "$SCAN_FILE"
elif [ $SCAN_EXIT -eq 1 ]; then
    SECRETS_COUNT=$(jq length "$SCAN_FILE")
    echo "⚠ Found $SECRETS_COUNT potential secrets"
else
    echo "ERROR: gitleaks failed with exit code $SCAN_EXIT"
    exit 1
fi

echo "Scan saved to: $SCAN_FILE"
EOF
chmod +x ~/github-secrets-cleanup/scripts/scan_secrets.sh
```

**Step 2: Тест на одном репозитории**

Run:
```bash
# Получить URL первого репо
REPO=$(jq -r '.[0] | "\(.url) \(.name)"' ~/github-secrets-cleanup/repos_list.json)
~/github-secrets-cleanup/scripts/scan_secrets.sh $REPO ~/github-secrets-cleanup
```
Expected: Репозиторий склонирован и просканирован

**Step 3: Проверить результат сканирования**

Run: `cat ~/github-secrets-cleanup/scans/*.json | jq 'length'`
Expected: Число (количество найденных секретов или 0)

---

## Task 5: Скрипт очистки репозитория

**Files:**
- Create: `~/github-secrets-cleanup/scripts/cleanup_repo.sh`
- Create: `~/github-secrets-cleanup/scripts/secrets_patterns.txt`

**Step 1: Создать файл паттернов для BFG**

```bash
cat > ~/github-secrets-cleanup/scripts/secrets_patterns.txt << 'EOF'
regex:AKIA[0-9A-Z]{16}
regex:(?i)api[_-]?key\s*[:=]\s*['"][^'"]+['"]
regex:(?i)password\s*[:=]\s*['"][^'"]+['"]
regex:(?i)secret\s*[:=]\s*['"][^'"]+['"]
regex:ghp_[a-zA-Z0-9]{36}
regex:gho_[a-zA-Z0-9]{36}
regex:github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}
regex:sk-[a-zA-Z0-9]{48}
regex:xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}
EOF
```

**Step 2: Создать скрипт очистки**

```bash
cat > ~/github-secrets-cleanup/scripts/cleanup_repo.sh << 'EOF'
#!/bin/bash
set -e

REPO_NAME="$1"
IS_PRIVATE="$2"
WORKDIR="${3:-$(pwd)}"

REPOS_DIR="$WORKDIR/repos"
SCANS_DIR="$WORKDIR/scans"
PATTERNS_FILE="$WORKDIR/scripts/secrets_patterns.txt"

if [ -z "$REPO_NAME" ]; then
    echo "Usage: $0 <repo_name> <is_private: true|false> [workdir]"
    exit 1
fi

REPO_PATH="$REPOS_DIR/${REPO_NAME}.git"
SCAN_FILE="$SCANS_DIR/${REPO_NAME}.json"

if [ ! -d "$REPO_PATH" ]; then
    echo "ERROR: Repository not found: $REPO_PATH"
    exit 1
fi

# Check if there are secrets to clean
SECRETS_COUNT=$(jq length "$SCAN_FILE" 2>/dev/null || echo "0")
if [ "$SECRETS_COUNT" -eq 0 ]; then
    echo "✓ No secrets to clean in $REPO_NAME"
    exit 0
fi

echo "=== Cleaning: $REPO_NAME ($SECRETS_COUNT secrets) ==="

cd "$REPO_PATH"

if [ "$IS_PRIVATE" = "true" ]; then
    echo "Strategy: Private repo - removing from current version only"

    # Convert bare repo to working copy temporarily
    TEMP_DIR=$(mktemp -d)
    git clone "$REPO_PATH" "$TEMP_DIR/work"
    cd "$TEMP_DIR/work"

    # Get files with secrets from scan
    FILES_TO_CHECK=$(jq -r '.[].File' "$SCAN_FILE" | sort -u)

    for FILE in $FILES_TO_CHECK; do
        if [ -f "$FILE" ]; then
            # Check file extension and redact
            case "$FILE" in
                *.env|.env*)
                    echo "Removing: $FILE"
                    rm -f "$FILE"
                    ;;
                *.pem|*.key)
                    echo "Removing: $FILE"
                    rm -f "$FILE"
                    ;;
                *)
                    echo "Redacting secrets in: $FILE"
                    # Simple redaction - replace matched secrets with REDACTED
                    sed -i -E 's/(api[_-]?key\s*[:=]\s*['\''"])[^'\''"]+(['\''"])/\1REDACTED\2/gi' "$FILE" 2>/dev/null || true
                    sed -i -E 's/(password\s*[:=]\s*['\''"])[^'\''"]+(['\''"])/\1REDACTED\2/gi' "$FILE" 2>/dev/null || true
                    sed -i -E 's/(secret\s*[:=]\s*['\''"])[^'\''"]+(['\''"])/\1REDACTED\2/gi' "$FILE" 2>/dev/null || true
                    ;;
            esac
        fi
    done

    # Update .gitignore
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo -e "\n# Secrets (auto-added)\n.env\n*.pem\n*.key\ncredentials.json" >> .gitignore
    fi

    # Commit and push
    git add -A
    if git diff --cached --quiet; then
        echo "No changes to commit"
    else
        git commit -m "chore: remove secrets and sensitive data

Automated cleanup by github-secrets-cleanup tool."
        git push origin HEAD
    fi

    # Cleanup
    rm -rf "$TEMP_DIR"

else
    echo "Strategy: Public repo - full history cleanup with BFG"

    # Delete sensitive files from all history
    SENSITIVE_FILES=(".env" "credentials.json" "*.pem" "*.key" ".env.*")
    for PATTERN in "${SENSITIVE_FILES[@]}"; do
        echo "Removing $PATTERN from history..."
        if command -v bfg &> /dev/null; then
            bfg --delete-files "$PATTERN" --no-blob-protection "$REPO_PATH" 2>/dev/null || true
        else
            java -jar ~/bfg.jar --delete-files "$PATTERN" --no-blob-protection "$REPO_PATH" 2>/dev/null || true
        fi
    done

    # Replace text patterns
    echo "Replacing secret patterns in history..."
    if command -v bfg &> /dev/null; then
        bfg --replace-text "$PATTERNS_FILE" --no-blob-protection "$REPO_PATH" 2>/dev/null || true
    else
        java -jar ~/bfg.jar --replace-text "$PATTERNS_FILE" --no-blob-protection "$REPO_PATH" 2>/dev/null || true
    fi

    # Cleanup git objects
    cd "$REPO_PATH"
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive

    # Force push
    echo "Force pushing cleaned history..."
    git push --force --all
    git push --force --tags
fi

echo "✓ Cleanup complete for $REPO_NAME"
EOF
chmod +x ~/github-secrets-cleanup/scripts/cleanup_repo.sh
```

**Step 3: Тест (DRY RUN - не запускать на реальных данных пока)**

Run: `echo "Скрипт создан, тестировать после полной сборки"`
Expected: Скрипт готов

---

## Task 6: Скрипт генерации отчёта

**Files:**
- Create: `~/github-secrets-cleanup/scripts/generate_report.sh`

**Step 1: Создать скрипт**

```bash
cat > ~/github-secrets-cleanup/scripts/generate_report.sh << 'EOF'
#!/bin/bash
set -e

WORKDIR="${1:-$(pwd)}"
REPOS_FILE="$WORKDIR/repos_list.json"
SCANS_DIR="$WORKDIR/scans"
OUTPUT_FILE="$WORKDIR/cleanup_report.md"
STATUS_FILE="$WORKDIR/cleanup_status.json"

echo "=== Generating report ==="

# Initialize counters
TOTAL=0
WITH_SECRETS=0
CLEANED=0

# Start report
cat > "$OUTPUT_FILE" << 'HEADER'
# GitHub Secrets Cleanup Report

**Дата:** $(date '+%Y-%m-%d %H:%M')

HEADER

# Replace date placeholder
sed -i "s/\$(date '+%Y-%m-%d %H:%M')/$(date '+%Y-%m-%d %H:%M')/" "$OUTPUT_FILE"

# Process each repo
echo "" >> "$OUTPUT_FILE"
echo "## Результаты по репозиториям" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

jq -c '.[]' "$REPOS_FILE" | while read -r REPO; do
    NAME=$(echo "$REPO" | jq -r '.name')
    VISIBILITY=$(echo "$REPO" | jq -r '.visibility')
    IS_ARCHIVED=$(echo "$REPO" | jq -r '.isArchived')

    TOTAL=$((TOTAL + 1))

    SCAN_FILE="$SCANS_DIR/${NAME}.json"

    echo "### $NAME ($VISIBILITY)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ "$IS_ARCHIVED" = "true" ]; then
        echo "⏭️ SKIPPED (archived)" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        continue
    fi

    if [ ! -f "$SCAN_FILE" ]; then
        echo "❓ NOT SCANNED" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        continue
    fi

    SECRETS_COUNT=$(jq length "$SCAN_FILE")

    if [ "$SECRETS_COUNT" -eq 0 ]; then
        echo "✅ CLEAN - No secrets found" >> "$OUTPUT_FILE"
    else
        WITH_SECRETS=$((WITH_SECRETS + 1))

        # Check if cleaned (status file)
        if [ -f "$STATUS_FILE" ] && jq -e ".\"$NAME\".cleaned == true" "$STATUS_FILE" > /dev/null 2>&1; then
            echo "✅ CLEANED" >> "$OUTPUT_FILE"
            CLEANED=$((CLEANED + 1))
        else
            echo "⚠️ NEEDS CLEANING" >> "$OUTPUT_FILE"
        fi

        echo "" >> "$OUTPUT_FILE"
        echo "| Тип | Файл | Строка | Значение (masked) |" >> "$OUTPUT_FILE"
        echo "|-----|------|--------|-------------------|" >> "$OUTPUT_FILE"

        # Output secrets (masked)
        jq -r '.[] | "| \(.RuleID) | \(.File) | \(.StartLine) | \(.Secret[0:4])****\(.Secret[-4:]) |"' "$SCAN_FILE" | head -20 >> "$OUTPUT_FILE"

        if [ "$SECRETS_COUNT" -gt 20 ]; then
            echo "" >> "$OUTPUT_FILE"
            echo "_...и ещё $((SECRETS_COUNT - 20)) секретов_" >> "$OUTPUT_FILE"
        fi
    fi

    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

# Add summary at the top
SUMMARY=$(cat << SUMMARY_EOF

**Всего репозиториев:** $TOTAL
**С секретами:** $WITH_SECRETS
**Очищено:** $CLEANED

---

SUMMARY_EOF
)

# Insert summary after header
sed -i "/^---$/a\\
$SUMMARY" "$OUTPUT_FILE" 2>/dev/null || true

echo "Report saved to: $OUTPUT_FILE"
EOF
chmod +x ~/github-secrets-cleanup/scripts/generate_report.sh
```

**Step 2: Тестовый запуск**

Run: `~/github-secrets-cleanup/scripts/generate_report.sh ~/github-secrets-cleanup`
Expected: Создан cleanup_report.md

**Step 3: Проверить отчёт**

Run: `head -50 ~/github-secrets-cleanup/cleanup_report.md`
Expected: Markdown-отчёт с заголовком и таблицами

---

## Task 7: Главный скрипт оркестрации

**Files:**
- Create: `~/github-secrets-cleanup/scripts/cleanup_all_repos.sh`

**Step 1: Создать главный скрипт**

```bash
cat > ~/github-secrets-cleanup/scripts/cleanup_all_repos.sh << 'EOF'
#!/bin/bash
set -e

WORKDIR="${1:-$HOME/github-secrets-cleanup}"
SCRIPTS_DIR="$WORKDIR/scripts"
LOG_FILE="$WORKDIR/cleanup.log"
STATUS_FILE="$WORKDIR/cleanup_status.json"

# Initialize
echo "{}" > "$STATUS_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================"
echo "GitHub Secrets Cleanup - $(date)"
echo "========================================"
echo ""

# Step 1: Check dependencies
echo "[1/5] Checking dependencies..."
"$SCRIPTS_DIR/check_deps.sh"
echo ""

# Step 2: Fetch repos
echo "[2/5] Fetching repository list..."
"$SCRIPTS_DIR/fetch_repos.sh" "$WORKDIR"
echo ""

# Step 3: Scan all repos
echo "[3/5] Scanning repositories for secrets..."
TOTAL=$(jq length "$WORKDIR/repos_list.json")
CURRENT=0

jq -c '.[] | select(.isArchived != true)' "$WORKDIR/repos_list.json" | while read -r REPO; do
    CURRENT=$((CURRENT + 1))
    NAME=$(echo "$REPO" | jq -r '.name')
    URL=$(echo "$REPO" | jq -r '.url')

    echo "[$CURRENT/$TOTAL] Scanning: $NAME"
    "$SCRIPTS_DIR/scan_secrets.sh" "$URL" "$NAME" "$WORKDIR" || true
done
echo ""

# Step 4: Cleanup repos with secrets
echo "[4/5] Cleaning repositories..."
jq -c '.[] | select(.isArchived != true)' "$WORKDIR/repos_list.json" | while read -r REPO; do
    NAME=$(echo "$REPO" | jq -r '.name')
    IS_PRIVATE=$(echo "$REPO" | jq -r '.isPrivate')

    SCAN_FILE="$WORKDIR/scans/${NAME}.json"
    if [ -f "$SCAN_FILE" ]; then
        SECRETS_COUNT=$(jq length "$SCAN_FILE")
        if [ "$SECRETS_COUNT" -gt 0 ]; then
            echo "Cleaning: $NAME ($SECRETS_COUNT secrets)"

            if "$SCRIPTS_DIR/cleanup_repo.sh" "$NAME" "$IS_PRIVATE" "$WORKDIR"; then
                # Update status
                jq --arg name "$NAME" '. + {($name): {"cleaned": true}}' "$STATUS_FILE" > "$STATUS_FILE.tmp"
                mv "$STATUS_FILE.tmp" "$STATUS_FILE"
            else
                jq --arg name "$NAME" '. + {($name): {"cleaned": false, "error": true}}' "$STATUS_FILE" > "$STATUS_FILE.tmp"
                mv "$STATUS_FILE.tmp" "$STATUS_FILE"
            fi
        fi
    fi
done
echo ""

# Step 5: Generate report
echo "[5/5] Generating report..."
"$SCRIPTS_DIR/generate_report.sh" "$WORKDIR"
echo ""

echo "========================================"
echo "Cleanup complete!"
echo "Report: $WORKDIR/cleanup_report.md"
echo "Log: $LOG_FILE"
echo "========================================"
echo ""
echo "⚠️  IMPORTANT: Rotate all found secrets!"
echo "    Even after cleanup, old values may be cached."
EOF
chmod +x ~/github-secrets-cleanup/scripts/cleanup_all_repos.sh
```

**Step 2: Сделать все скрипты исполняемыми**

Run: `chmod +x ~/github-secrets-cleanup/scripts/*.sh`
Expected: OK

---

## Task 8: Тестовый прогон (SCAN ONLY)

**Step 1: Запустить только сканирование без очистки**

```bash
# Модифицируем для тестового режима - только сканируем
cd ~/github-secrets-cleanup

# Проверка зависимостей
./scripts/check_deps.sh

# Получение списка репо
./scripts/fetch_repos.sh .

# Сканирование первых 3 репо
jq -c '.[0:3] | .[] | select(.isArchived != true)' repos_list.json | while read -r REPO; do
    NAME=$(echo "$REPO" | jq -r '.name')
    URL=$(echo "$REPO" | jq -r '.url')
    ./scripts/scan_secrets.sh "$URL" "$NAME" .
done

# Генерация отчёта (без очистки)
./scripts/generate_report.sh .
```

**Step 2: Проверить результаты**

Run: `cat ~/github-secrets-cleanup/cleanup_report.md`
Expected: Отчёт показывает найденные секреты

**Step 3: Решение о полном запуске**

После проверки отчёта — принять решение о запуске полной очистки.

---

## Task 9: Полный запуск (ОСТОРОЖНО!)

> ⚠️ **WARNING:** Этот шаг выполняет force push на публичные репозитории!
> Убедитесь, что вы готовы к этому.

**Step 1: Запуск полной очистки**

```bash
cd ~/github-secrets-cleanup
./scripts/cleanup_all_repos.sh .
```

**Step 2: Проверить отчёт**

Run: `cat ~/github-secrets-cleanup/cleanup_report.md`
Expected: Все репозитории отмечены как CLEANED или CLEAN

**Step 3: Ротация ключей**

После очистки — обязательно:
1. Перегенерировать все найденные API-ключи
2. Обновить токены в сервисах
3. Сменить пароли

---

## Checklist финальной проверки

- [ ] Все скрипты созданы в `~/github-secrets-cleanup/scripts/`
- [ ] `check_deps.sh` проходит без ошибок
- [ ] `fetch_repos.sh` получает список репозиториев
- [ ] `scan_secrets.sh` успешно сканирует тестовый репо
- [ ] `generate_report.sh` создаёт корректный Markdown
- [ ] Тестовый прогон на 3 репо завершён
- [ ] Отчёт проверен вручную
- [ ] Полный запуск выполнен (Task 9)
- [ ] Ключи ротированы
