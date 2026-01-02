# TASKS — SEO Content Pipeline

**Последнее обновление:** 2025-12-31
**Всего RU категорий:** 51 ✅
**Всего UK категорий:** 34
**Нужно Meta:** 17 новых

---

## ✅ СОЗДАНИЕ КАТЕГОРИЙ — ЗАВЕРШЕНО

Все 51 категория созданы (было 39, добавлено 12 + 5 ранее = 17 новых)

---

## 🔄 ТЕКУЩИЕ ЗАДАЧИ

### ⬜ Следующий шаг: /generate-meta для 17 новых

| #  | Slug                            | Clean | Meta | UK  | Volume |
|----|---------------------------------|-------|------|-----|--------|
| 1  | tverdyy-vosk                    | ✅    | ⬜   | ⬜  | 1000+  |
| 2  | zhidkiy-vosk                    | ✅    | ⬜   | ⬜  | 480+   |
| 3  | pyatnovyvoditeli                | ✅    | ⬜   | ⬜  | 2400   |
| 4  | ochistiteli-kuzova              | ✅    | ⬜   | ⬜  | 590    |
| 5  | akkumulyatornye-mashinki        | ✅    | ⬜   | ⬜  | 260    |
| 6  | avtoshampuni                    | ✅    | ⬜   | ⬜  | 480    |
| 7  | sredstva-dlya-stekol            | ✅    | ⬜   | ⬜  | L2     |
| 8  | sredstva-dlya-diskov-i-shin     | ✅    | ⬜   | ⬜  | L2     |
| 9  | s-voskom                        | ✅    | ⬜   | ⬜  | SEO    |
| 10 | kislotnyy-shampun               | ✅    | ⬜   | ⬜  | 70     |
| 11 | zashchitnoe-pokrytie-dlya-koles | ✅    | ⬜   | ⬜  | 10     |
| 12 | dlya-vneshnego-plastika         | ✅    | ⬜   | ⬜  | 40     |
| 13 | mikrofibra-dlya-polirovki       | ✅    | ⬜   | ⬜  | 50     |
| 14 | mikrofibra-dlya-stekol          | ✅    | ⬜   | ⬜  | 50     |
| 15 | nabory-dlya-deteylinga          | ✅    | ⬜   | ⬜  | 260    |
| 16 | porolonovye                     | ✅    | ⬜   | ⬜  | L3     |
| 17 | oborudovanie                    | ✅    | ⬜   | ⬜  | 90     |

---

## 🛠 Исправить дубли

- [ ] D1: Убрать "меховой/шерстяной круг" из polirovalnye-krugi (есть в mekhovye)
- [ ] D2: Реструктуризация voski после создания подкатегорий

---

## 📊 ПРОГРЕСС

| Этап         | RU     | UK     |
|--------------|--------|--------|
| Init (папки) | 51/51 ✅| 34/51  |
| Clean (JSON) | 51/51 ✅| 34/51  |
| Meta (JSON)  | 34/51  | 34/51  |
| Research     | 13/51  | —      |
| Content      | 13/51  | 13/51  |

---

## ✅ ПОЛНОСТЬЮ ГОТОВО (13 категорий)

aktivnaya-pena, dlya-ruchnoy-moyki, ochistiteli-stekol, glina-i-avtoskraby, antimoshka, antibitum, cherniteli-shin, ochistiteli-diskov, ochistiteli-shin, dlya-khimchistki-salona, ochistiteli-dvigatelya, keramika-i-zhidkoe-steklo, gubki-i-varezhki

---

## ⏳ Init+Meta готово, нужен Research+Content (21 категория)

polirovalnye-mashinki, malyarnyy-skotch, mikrofibra-i-tryapki, polirovalnye-pasty, polirovalnye-krugi, neytralizatory-zapakha, apparaty-tornador, raspyliteli-i-penniki, poliroli-dlya-plastika, kvik-deteylery, obezzhirivateli, voski, antidozhd, aksessuary-dlya-naneseniya, sredstva-dlya-kozhi, shchetki-i-kisti, omyvatel, polirol-dlya-stekla, vedra-i-emkosti, silanty, mekhovye

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /uk-content-init → /quality-gate → /deploy
```

---

## Команды валидации

```bash
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo
```

---

**Version:** 9.0
**Last Updated:** 2025-12-31
