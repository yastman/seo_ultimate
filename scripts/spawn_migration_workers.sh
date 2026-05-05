#!/bin/bash

# Create windows
tmux new-window -n "W1-brush"
tmux new-window -n "W2-access"
tmux new-window -n "W3-orphan"

# W1: Category 477
cat << 'PROMPT1' | xargs -0 tmux send-keys -t "W1-brush"
claude --dangerously-skip-permissions 'W1: Изучить товары из категории 477 и составить маппинг.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 1

ДАННЫЕ: data/generated/all_products_dump.tsv
Формат: product_id	model	manufacturer_id	name	categories

КАТЕГОРИИ для маппинга:
- 494 = Щётки для мойки (диски, шини, двигун, жорстка, Vikan, Tampico, мідна, ПВХ)
- 495 = Кисти для детейлинга (пензель, мяка, салон, вентиляція, шкіра, текстиль)
- 453 = Губки (губка, рукавиця)
- 466 = Наборы (набір — залишити в 2х категоріях)

WORKFLOW:
1. grep товари з 477
2. Для кожного товару визнач категорію за назвою
3. Створи маппинг TSV: product_id	name	old	new	reason
4. Збережи в data/generated/mapping_W1.tsv

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W1-migration.log

НЕ делай git commit. НЕ генеруй SQL.'
PROMPT1
tmux send-keys -t "W1-brush" Enter

# W2: Category 445
cat << 'PROMPT2' | xargs -0 tmux send-keys -t "W2-access"
claude --dangerously-skip-permissions 'W2: Изучить товары из категории 445 и составить маппинг.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 2

ДАННЫЕ: data/generated/all_products_dump.tsv

КАТЕГОРИИ:
- 446 = Микрофибра (мікрофібра, серветка, рушник)
- 447 = Распылители (тригер, пінник, пляшка)
- 448 = Вёдра (відро, сепаратор)
- 453 = Губки (губка, рукавиця, аплікатор)
- 454 = Скотч (нітрилові рукавиці)
- 466 = Наборы
- 494/495 = Щітки/Кисті

WORKFLOW:
1. grep товари з 445
2. Визнач листову категорію за назвою
3. Створи маппинг TSV
4. Збережи в data/generated/mapping_W2.tsv

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W2-migration.log

НЕ делай git commit. НЕ генеруй SQL.'
PROMPT2
tmux send-keys -t "W2-access" Enter

# W3: Orphans
cat << 'PROMPT3' | xargs -0 tmux send-keys -t "W3-orphan"
claude --dangerously-skip-permissions 'W3: Изучить orphans и товары в родительских категориях.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 3

ДАННЫЕ: data/generated/all_products_dump.tsv

WORKFLOW:
1. Знайди товари без категорій (NULL)
2. Знайди товари в родительських (435,457,462,468,425)
3. Визнач правильні категорії за назвою
4. Створи маппинг TSV
5. Збережи в data/generated/mapping_W3.tsv

Родительські категорії:
- 435 (Покриття) листові: 436/437/438/439
- 457 (Полірування) листові: 458/459/461
- 462 (Обладнання) листові: 463
- 468 (Мийка) листові: 469/470/471/472
- 425 (Інтерєр) листові: 427/428/429/431/434

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W3-migration.log

НЕ делай git commit. НЕ генеруй SQL.'
PROMPT3
tmux send-keys -t "W3-orphan" Enter

echo "Workers spawned"
