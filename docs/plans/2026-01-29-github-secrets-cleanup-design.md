# GitHub Secrets Cleanup — Design Document

**Дата:** 2026-01-29
**Статус:** Draft
**Цель:** Автоматическая очистка всех GitHub-репозиториев от секретных данных с формированием отчёта

---

## 1. Требования

### Scope
- Все репозитории на GitHub-аккаунте (публичные и приватные)

### Типы секретов для поиска
- API-ключи (AWS, GCP, Azure, OpenAI, Stripe, etc.)
- Токены (GitHub, GitLab, Slack, Discord, etc.)
- Пароли в коде и конфигах
- Файлы credentials: `.env`, `credentials.json`, `config.yml` с секретами
- Приватные ключи SSH/SSL (*.pem, *.key, id_rsa)
- Connection strings к БД (PostgreSQL, MySQL, MongoDB, Redis)
- Webhook URLs с токенами

### Стратегия очистки
| Тип репозитория | Действие |
|-----------------|----------|
| Публичный | Полная очистка истории (BFG Repo-Cleaner) + force push |
| Приватный | Удаление из текущей версии + обычный commit/push |

### Отчёт
- Формат: Markdown
- Содержание: список репозиториев, найденные секреты (замаскированные), статус очистки

### Автоматизация
- Полностью автоматический процесс через `gh` CLI
- Без создания бэкапов

---

## 2. Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                     cleanup_all_repos.sh                    │
│                      (главный скрипт)                       │
└─────────────────────────────────────────────────────────────┘
                              │
      ┌───────────────┬───────┴───────┬───────────────┐
      ▼               ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│ fetch_    │   │ scan_     │   │ cleanup_  │   │ generate_ │
│ repos.sh  │   │ secrets.sh│   │ repo.sh   │   │ report.sh │
└───────────┘   └───────────┘   └───────────┘   └───────────┘
      │               │               │               │
      ▼               ▼               ▼               ▼
   gh api        gitleaks         BFG / git      Markdown
```

### Рабочая директория

```
~/github-secrets-cleanup/
├── scripts/
│   ├── cleanup_all_repos.sh      # Главный скрипт
│   ├── fetch_repos.sh            # Получение списка репо
│   ├── scan_secrets.sh           # Сканирование gitleaks
│   ├── cleanup_repo.sh           # Очистка одного репо
│   └── generate_report.sh        # Генерация отчёта
├── repos/                        # Склонированные репозитории
├── scans/                        # Результаты сканирования (JSON)
├── cleanup_report.md             # Итоговый отчёт
└── cleanup.log                   # Лог выполнения
```

---

## 3. Инструменты

| Инструмент | Назначение | Установка |
|------------|------------|-----------|
| `gh` | GitHub CLI — список репо, клонирование, push | `sudo apt install gh` или `brew install gh` |
| `gitleaks` | Сканер секретов (140+ паттернов) | `brew install gitleaks` или бинарник с GitHub |
| `BFG Repo-Cleaner` | Быстрая очистка истории git | `brew install bfg` или JAR с GitHub |
| `jq` | Парсинг JSON | `sudo apt install jq` |

---

## 4. Алгоритм

### 4.1. Получение списка репозиториев

```bash
# Все репозитории (публичные + приватные)
gh repo list --limit 1000 --json name,visibility,url,isPrivate
```

Выход: `repos_list.json` со структурой:
```json
[
  {"name": "repo-name", "visibility": "public", "url": "...", "isPrivate": false},
  ...
]
```

### 4.2. Сканирование секретов

Для каждого репозитория:

```bash
# Клонирование с историей
git clone --mirror <repo_url> repos/<repo_name>.git

# Сканирование gitleaks
gitleaks detect --source repos/<repo_name>.git \
  --report-format json \
  --report-path scans/<repo_name>.json
```

Gitleaks найдёт:
- AWS Access Keys, Secret Keys
- GitHub/GitLab tokens
- Private keys (RSA, DSA, EC, PGP)
- Generic passwords в коде
- Connection strings
- JWT tokens
- Slack/Discord webhooks

### 4.3. Очистка репозитория

**Для публичных репозиториев (полная очистка истории):**

```bash
# Создание файла с паттернами для удаления
cat > secrets_to_remove.txt << EOF
password=*
api_key=*
AKIA*           # AWS Access Key ID
*.pem
*.key
.env
credentials.json
EOF

# BFG удаляет из всей истории
bfg --delete-files .env repos/<repo_name>.git
bfg --delete-files "*.pem" repos/<repo_name>.git
bfg --replace-text secrets_to_remove.txt repos/<repo_name>.git

# Очистка и force push
cd repos/<repo_name>.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

**Для приватных репозиториев (только текущая версия):**

```bash
cd repos/<repo_name>
git checkout main

# Удаление файлов
rm -f .env credentials.json *.pem *.key

# Замена секретов в коде (sed)
find . -type f -name "*.py" -exec sed -i 's/api_key\s*=\s*"[^"]*"/api_key = "REDACTED"/g' {} \;
find . -type f -name "*.js" -exec sed -i 's/apiKey\s*:\s*"[^"]*"/apiKey: "REDACTED"/g' {} \;

# Обновление .gitignore
echo -e "\n# Secrets\n.env\n*.pem\n*.key\ncredentials.json" >> .gitignore

# Commit и push
git add -A
git commit -m "chore: remove secrets and sensitive data"
git push
```

### 4.4. Генерация отчёта

```markdown
# GitHub Secrets Cleanup Report

**Дата:** 2026-01-29
**Всего репозиториев:** 25
**С секретами:** 8
**Очищено:** 8

## Результаты по репозиториям

### repo-name-1 (public) ✅ CLEANED

| Тип | Файл | Строка | Значение (masked) |
|-----|------|--------|-------------------|
| AWS Access Key | config.py | 42 | AKIA****XXXX |
| Generic Password | .env | 3 | ******* |

**Действие:** Полная очистка истории (BFG)

---

### repo-name-2 (private) ✅ CLEANED

| Тип | Файл | Строка | Значение (masked) |
|-----|------|--------|-------------------|
| GitHub Token | deploy.sh | 15 | ghp_****XXXX |

**Действие:** Удаление из текущей версии

---

### repo-name-3 (public) ✔️ CLEAN

Секреты не найдены.

---
```

---

## 5. Обработка ошибок

| Ситуация | Действие |
|----------|----------|
| Репо архивирован | Пропустить, отметить в отчёте |
| Нет прав на push | Пропустить, отметить в отчёте |
| Force push запрещён (protected branch) | Попробовать через API отключить protection, очистить, вернуть |
| gitleaks не нашёл секретов | Отметить как CLEAN |
| BFG упал | Логировать ошибку, попробовать git filter-branch |

---

## 6. Безопасность

### Риски
1. **Force push может сломать CI/CD** — если пайплайны зависят от конкретных коммитов
2. **Коллабораторы потеряют локальную историю** — им придётся делать `git fetch --all && git reset --hard origin/main`
3. **GitHub кэширует старые коммиты** — даже после force push, старые коммиты доступны по SHA ~90 дней

### Митигация
- После очистки публичных репо: **обязательно ротировать все найденные ключи**
- Отчёт содержит список ключей для ротации
- Для критичных репо рассмотреть полное удаление и создание нового

---

## 7. Ограничения

- Не сканирует GitHub Gists
- Не проверяет GitHub Actions secrets (они уже защищены)
- Не удаляет секреты из форков (нужен доступ к форкам)
- Gitleaks может пропустить кастомные форматы секретов

---

## 8. Checklist для запуска

- [ ] `gh auth status` — проверить авторизацию
- [ ] `gh auth refresh -s delete_repo` — добавить scope если нужно
- [ ] Установить gitleaks: `brew install gitleaks` или скачать бинарник
- [ ] Установить BFG: `brew install bfg` или скачать JAR
- [ ] Создать рабочую директорию: `mkdir -p ~/github-secrets-cleanup/{scripts,repos,scans}`
- [ ] Запустить: `./cleanup_all_repos.sh`
- [ ] Проверить отчёт: `cat cleanup_report.md`
- [ ] **Ротировать все найденные ключи!**

---

## 9. Альтернативные подходы

### Вариант A: GitHub Secret Scanning (если включён)
GitHub сам сканирует публичные репо и уведомляет. Но:
- Не очищает автоматически
- Только для публичных репо
- Ограниченный набор паттернов

### Вариант B: Сервис GitGuardian
- SaaS для мониторинга секретов
- Платный для приватных репо
- Не очищает историю

### Вариант C: Ручная проверка
- Долго и ненадёжно
- Не масштабируется

**Выбран вариант:** Автоматизация через gitleaks + BFG — бесплатно, полный контроль, работает с приватными репо.

---

## 10. Примерное время выполнения

| Этап | Время (для 25 репо) |
|------|---------------------|
| Клонирование | ~5-10 мин |
| Сканирование | ~10-15 мин |
| Очистка | ~15-30 мин |
| Генерация отчёта | ~1 мин |
| **Итого** | **~30-60 мин** |

Зависит от размера репозиториев и количества найденных секретов.
