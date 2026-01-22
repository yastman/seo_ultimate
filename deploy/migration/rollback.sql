-- ROLLBACK: Delete newly created categories
-- Use if Phase 2 needs to be undone
-- Run: cat deploy/migration/rollback.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'

SET NAMES utf8mb4;

-- Delete SEO URLs for new categories
DELETE FROM oc_seo_url WHERE query IN ('category_id=476', 'category_id=477', 'category_id=478', 'category_id=479');

-- Delete category paths
DELETE FROM oc_category_path WHERE category_id >= 476;

-- Delete category descriptions
DELETE FROM oc_category_description WHERE category_id >= 476;

-- Delete categories
DELETE FROM oc_category WHERE category_id >= 476;

-- Verify deletion
SELECT COUNT(*) as remaining FROM oc_category WHERE category_id >= 476;

-- ============================================
-- FULL ROLLBACK (restore from backup)
-- ============================================
-- Run this to restore EVERYTHING:
-- ult 'sudo mysql -u root -pfr1daYTw1st yastman_test < /home/yastman/backups/categories_backup_20260121_191135.sql'
-- ult 'sudo cp /home/yastman/backups/htaccess_backup_*.txt /home/yastman/sites/ultimate.net.ua/.htaccess'
-- ult 'sudo rm -rf /home/yastman/sites/ultimate.net.ua/system/storage/cache/*'
