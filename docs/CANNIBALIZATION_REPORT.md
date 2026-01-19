# Cannibalization & Assortment Analysis Report

**Date:** 2026-01-14
**Status:** READY FOR REVIEW
**Objective:** Optimize category structure to prevent keyword cannibalization and improve UX based on actual product availability.

## 🚨 Critical Issues Identified (Confirmed via SQL Audit)

### 1. The "Polishing" Problem (Category ID: 457)

-   **Status:** 🔴 **CRITICAL CANNIBALIZATION**
-   **Evidence:** Category 457 contains **EVERYTHING** related to polishing:
    -   Machines (duplicating ID 461)
    -   Pads (duplicating ID 459)
    -   Pastes (duplicating ID 458)
-   **Impact:** It steals traffic from all specific subcategories. Users land on a mixed "dumpster" page instead of specific selections.
-   **Recommendation:**
    -   **Physical Action:** Remove ALL product assignments from Category 457.
    -   **Structural Action:** Make 457 a pure **Parent Category** (Landing Page) with links to children.

### 2. Microfiber (446) vs. Rags (451)

-   **Status:** 🔴 **DUPLICATE INTENT**
-   **Evidence:**
    -   `Протирочні матеріали, мікрофібри (ID: 446)`: Contains towels, cloths, applicators.
    -   `Ганчірка для авто (ID: 451)`: Contains **identically** the same products (Towels, Microfibers).
-   **Impact:** "Ганчірка" (Rag) is just a synonym for Microfiber. Having two physical categories splits link equity and confuses users.
-   **Recommendation:** **MERGE** 451 INTO 446. Delete 451. Use "Ганчірка" as a keyword/synonym for 446.

### 3. Equipment (462) vs. Tornador (463)

-   **Status:** 🟠 **PARTIAL OVERLAP**
-   **Evidence:**
    -   `Обладнання (ID: 462)` contains "Апарат Tornador Z-020", "Z-030", "Mini Gun".
    -   `Апарати Tornador (ID: 463)` contains the exact same items.
-   **Recommendation:** Remove Tornador products from 462. Keep 462 for Vacuums, Ozone Generators, and Compressors.

### 4. Waxes: Solid (437) vs. Liquid?

-   **Status:** 🟠 **MISCLASSIFICATION**
-   **Evidence:**
    -   `Тверді воски (ID: 437)` contains "Рідкий віск Collinite 845".
    -   Category `Рідкий воск (ID: 456)` exists but appears empty or underutilized in the report.
    -   Category `Консервація та сушіння (ID: 414)` contains "Рідкий Віск-Консервант".
-   **Recommendation:**
    -   Define clear rules: "Solid" (Paste/Hard), "Liquid" (Creme/Spray).
    -   Move Collinite 845 to a proper "Liquid/Creme Wax" category or merge 456 into a broader "Waxes" parent.

### 5. Polishing Machines (461) vs. Cordless (Akku)

-   **Status:** 🟠 **PARENT-CHILD CONFLICT**
-   **Evidence:** `Полірувальні машинки (461)` contains "Акумуляторна Полірувальна Машинка".
-   **Analysis:** `akkumulyatornaya` likely exists as a Filter or Virtual Category (no unique SQL ID found in main range).
-   **Resolution:** As discussed, **REMOVE** "Cordless/Battery" keywords from the Parent (461) metadata to allow the specific sub-page to rank.

### 6. Tires vs. Blackeners (420)

-   **Status:** 🟡 **OVERLAP**
-   **Evidence:** `Засоби для шин (ID 420)` contains mostly blackeners (gels, dressings). Distinct "Cleaner" category is weak.
-   **Recommendation:** Rename 420 to **"Засоби для шин та гуми"** (Tires & Rubber). Consolidate all tire semantics here.

## 🏗️ Execution Plan

### Phase 1: Mergers (Quick Wins)

-   [ ] **Microfiber:** Move all products from 451 -> 446. Disable 451.
-   [ ] **Tornador:** Unlink Tornador products from 462.
-   [ ] **Polishing:** Unlink ALL products from 457 (Root).

### Phase 2: Metadata Fixes

-   [x] **Shampuni-dlya-ruchnoy-moyki:** Remove acidic keywords to prevent cannibalization with kislotnyy (2026-01-19)
-   [ ] **Machines:** De-optimize Parent (461) for "Cordless" keywords.
-   [ ] **Waxes:** Fix product names/assignments for Liquid vs Solid.

### Phase 3: Structural Updates

-   [ ] Rename 420 `ochistiteli-shin` -> `sredstva-dlya-shin`.
-   [ ] Verify `akkumulyatornaya` URL works (is it a filter?).

---

**Approvals Required:**

-   [ ] Merge Microfiber/Rags?
-   [ ] Empty the Polishing Root Category?
