-- deploy/sync/01_update_structure.sql
-- Синхронизация структуры дерева

-- Наборы: L1 → L2 под Аксессуары
UPDATE oc_category SET parent_id = 445 WHERE category_id = 466;

-- Пересчитать category_path для Наборы
DELETE FROM oc_category_path WHERE category_id = 466;
INSERT INTO oc_category_path (category_id, path_id, level) VALUES
(466, 445, 0),
(466, 466, 1);
