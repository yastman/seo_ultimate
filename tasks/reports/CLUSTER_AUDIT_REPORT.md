# Audit Report: Cluster Purity

**Date:** 2026-01-05
**Status:** REVIEW

## 🚨 Critical Issues (Must Fix First)

| Source Cluster                           | Keyword Examples (Vol)                                                    | Issue Type                | Proposal (Target)                                                                     |
| :--------------------------------------- | :------------------------------------------------------------------------ | :------------------------ | :------------------------------------------------------------------------------------ |
| **Filter: Аккумуляторная** (Полировка)   | `полировочная машинка` (8100), `купить полировочную машинку` (880)        | **False Positive Filter** | The filter is too greedy. Move generic keys to **General L2: Полировальные машинки**. |
| **L3: Аппараты Tornador**                | `автохимия от производителя` (10), `поставщики` (10), `производство` (10) | **B2B Intent**            | Create **Special: Опт и B2B** and move all wholesale keys there.                      |
| **L3: Аппараты Tornador**                | `оборудование для химчистки авто` (90), `оборудование для моек` (10)      | **Wrong Level**           | Create **General L2: Оборудование** or **L3: Оборудование для моек**.                 |
| **Cluster: Средства для кожи (General)** | `для химчистки салона` (50), `жидкость для химчистки салона` (20)         | **Wrong Category**        | Move to **L2: Очистители салона (Универсальные)**. "Leather" is too specific.         |
| **L3: Активная пена**                    | `автошампунь для ручной мойки` (390), `шампунь для ручной мойки` (10)     | **Wrong Product**         | Create **L3: Шампуни для ручной мойки** (separate from Active Foam).                  |
| **L2: Очистители двигателя**             | `полироль для наружного пластика` (40)                                    | **Wrong Category**        | Create **L3: Чернители наружного пластика** (in Exterior) or add to **Polishes**.     |

## ⚠️ Mix of Intents (Medium Priority)

| Source Cluster               | Keyword Examples                                                   | Issue Type     | Proposal                                                            |
| :--------------------------- | :----------------------------------------------------------------- | :------------- | :------------------------------------------------------------------ |
| **L3: Наборы для мойки**     | `набор для ухода за кожей` (30), `набор кругов для полировки` (30) | Wrong Category | Move to **L3: Наборы для салона** and **L3: Наборы для полировки**. |
| **L3: Кисти для детейлинга** | `щетка для дисков` (50), `щетка для мытья дисков` (10)             | Wrong Product  | Move to **L2: Щетки и кисти** (General or Wheel Brushes).           |
| **L3: Очистители шин**       | `защитное покрытие для дисков` (10)                                | Wrong Product  | Move to **L3: Керамика для дисков** or **Силанты**.                 |
| **Cluster: Тряпка для авто** | `тряпка для салона`, `тряпка для панели`                           | Specific Use   | Keep in General for now, or tagging "Interior" if volume grows.     |
| **L3: Аппараты Tornador**    | `диски для полировки` (10)                                         | Wrong Category | Move to **L2: Полировальные круги**.                                |

## ℹ️ Minor / Observations

| Source Cluster         | Keyword Examples               | Note                                                                          |
| :--------------------- | :----------------------------- | :---------------------------------------------------------------------------- |
| **cluster: Омыватель** | `стеклоомыватель украина`      | Geo-specific queries. Keep for local SEO.                                     |
| **L2: Воски**          | `восковый полироль`            | Ambiguous. "Wax polish" suggests AIO (All-in-One). Keep in Waxes or Polishes. |
| **L3: Антидождь**      | `покрытие для лобового стекла` | Could be ceramic. "Antirain" is safer for now.                                |

---

## 🛠 Action Plan

1. **Stop "Cordless" Filter from eating L2**: The script/logic defining the filter needs adjustment. It interprets "polyrovka" or similar generic terms as belonging to the filter if not careful, OR the CSV structure itself has these keys erroneously tagged with `Cluster: Аккумуляторная`.
1. **Split "Manual Wash" from "Active Foam"**: This is a distinct washing method (2nd phase).
1. **Clean up "Tornador"**: It is currently the "trash bin" for equipment and B2B keys.
1. **Create "Universal Interior Cleaner"**: We have "Leather" and "Stain Removers", but we miss the general "Interior Cleaner / APC" category for general "dry cleaning" queries.

**Approver:** Antigravity using `data/STRUCTURE.md` analysis.
