# TODO: UK Content для категорий

**Цель:** Создать UK контент для всех категорий

---

## Как работать

1. Убедиться что `uk/data/uk_keywords.json` содержит ключи для категории
2. Выполнить цикл:
   - `/uk-category-init {slug}`
   - `/uk-generate-meta {slug}`
   - `/uk-content-generator {slug}`
   - `uk-content-reviewer {slug}`
   - `/uk-quality-gate {slug}`
3. Commit
4. Отметить `[x]` в чеклисте

---

## Фаза 1: Сбор ключей

- [x] `/uk-keywords-export` выполнен
- [ ] Частотность собрана (KeySO/Serpstat) — **PENDING** (RU fallback используется)
- [x] `uk/data/uk_keywords.json` создан (50 категорий, RU volume как fallback)

---

## Легенда

- `[x]` — полный цикл завершён (init + meta + content + review + quality-gate)
- `[~]` — init + meta готово, content pending
- `[ ]` — не начато

---

## Фаза 2: L3 Categories (листовые)

- [x] aktivnaya-pena
- [x] antibitum
- [x] antimoshka
- [~] antidozhd — init + meta done
- [~] akkumulyatornaya — init + meta done
- [~] cherniteli-shin — init + meta done
- [~] glina-i-avtoskraby — init + meta done
- [~] gubki-i-varezhki — init + meta done
- [~] keramika-dlya-diskov — init + meta done
- [~] kisti-dlya-deteylinga — init + meta done
- [~] malyarniy-skotch — init + meta done
- [~] mekhovye — init + meta done
- [~] nabory — init + meta done
- [~] neytralizatory-zapakha — init + meta done
- [~] obezzhirivateli — init + meta done
- [~] ochistiteli-diskov — init + meta done
- [~] ochistiteli-dvigatelya — init + meta done
- [~] ochistiteli-kozhi — init + meta done
- [~] ochistiteli-shin — init + meta done
- [~] ochistiteli-stekol — init + meta done
- [~] omyvatel — init + meta done
- [~] polirol-dlya-stekla — init + meta done
- [~] poliroli-dlya-plastika — init + meta done
- [~] polirovalnye-pasty — init + meta done
- [~] pyatnovyvoditeli — init + meta done
- [~] raspyliteli-i-penniki — init + meta done
- [~] shampuni-dlya-ruchnoy-moyki — init + meta done
- [~] shchetka-dlya-moyki-avto — init + meta done
- [~] silanty — init + meta done
- [~] sredstva-dlya-khimchistki-salona — init + meta done
- [~] tverdyy-vosk — init + meta done
- [~] ukhod-za-kozhey — init + meta done
- [~] ukhod-za-naruzhnym-plastikom — init + meta done
- [~] vedra-i-emkosti — init + meta done
- [~] zhidkiy-vosk — init + meta done

## Фаза 2: L2 Categories

- [~] aksessuary-dlya-naneseniya-sredstv — init + meta done
- [~] apparaty-tornador — init + meta done
- [~] avtoshampuni — init + meta done
- [~] keramika-i-zhidkoe-steklo — init + meta done
- [~] kvik-deteylery — init + meta done
- [~] mikrofibra-i-tryapki — init + meta done
- [~] sredstva-dlya-kozhi — init + meta done
- [~] voski — init + meta done

## Фаза 2: L1 Categories (хабы)

- [~] aksessuary — init + meta done
- [~] moyka-i-eksterer — init + meta done
- [~] oborudovanie — init + meta done
- [~] opt-i-b2b — init + meta done
- [~] polirovka — init + meta done
- [~] ukhod-za-intererom — init + meta done
- [~] zashchitnye-pokrytiya — init + meta done

---

**Progress:** 3/50 (content ready) | 50/50 (init + meta)
**Last batch:** 2026-01-23 — 47 categories init + meta + research copied
