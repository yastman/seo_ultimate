"""TDD test: issue #7 — upload_to_db.py must import without mysql.connector present.

The bug: tests/unit/test_upload_to_db.py caused ImportError because
scripts/upload_to_db.py had a top-level `import mysql.connector`.
Fix: defer the import to the connect() function (lazy import).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is importable even without it being a package
SCRIPTS_DIR = Path(__file__).parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import upload_to_db  # noqa: E402


class TestImportDoesNotRequireMysql:
    """upload_to_db must be importable even if mysql.connector is missing."""

    def test_module_importable_without_mysql(self, monkeypatch):
        """Removing mysql from sys.modules must not break module import."""
        # Remove mysql from sys.modules to simulate missing package
        saved = {k: v for k, v in sys.modules.items() if "mysql" in k}
        for k in saved:
            sys.modules.pop(k, None)
        try:
            # Re-import must succeed — mysql import is lazy
            import importlib
            importlib.reload(upload_to_db)
        except ImportError as exc:
            pytest.fail(f"upload_to_db import failed without mysql: {exc}")
        finally:
            sys.modules.update(saved)


class TestGetConnectionConfig:
    """get_connection_config reads env vars with sensible defaults."""

    def test_returns_dict_with_required_keys(self):
        config = upload_to_db.get_connection_config()
        assert "host" in config
        assert "port" in config
        assert "database" in config
        assert "user" in config
        assert "password" in config

    def test_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "myhost")
        monkeypatch.setenv("MYSQL_DATABASE", "mydb")
        config = upload_to_db.get_connection_config()
        assert config["host"] == "myhost"
        assert config["database"] == "mydb"


class TestConnect:
    """connect() must raise ImportError if mysql.connector is missing."""

    def test_raises_import_error_if_mysql_missing(self, monkeypatch):
        """When mysql.connector cannot be imported, connect() raises ImportError."""
        def bad_import(name, *args, **kwargs):
            if name == "mysql.connector":
                raise ImportError("No module named 'mysql'")
            return original_import(name, *args, **kwargs)

        import builtins
        original_import = builtins.__import__
        monkeypatch.setattr(builtins, "__import__", bad_import)

        with pytest.raises(ImportError, match="mysql-connector-python"):
            upload_to_db.connect({})

    def test_calls_connector_connect(self):
        """connect() must pass config dict to mysql.connector.connect()."""
        mock_connector = MagicMock()
        mock_connector.connect.return_value = MagicMock()

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_connector

        with patch.dict(sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_connector}):
            config = {"host": "localhost", "port": 3306, "database": "db", "user": "u", "password": "p"}
            upload_to_db.connect(config)

        mock_connector.connect.assert_called_once_with(**config)


class TestExecuteSqlFile:
    """execute_sql_file splits SQL by semicolons and executes each statement."""

    def test_returns_statement_count(self, tmp_path):
        sql_path = tmp_path / "test.sql"
        sql_path.write_text("INSERT INTO t VALUES (1);\nINSERT INTO t VALUES (2);", encoding="utf-8")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        count = upload_to_db.execute_sql_file(mock_conn, sql_path)

        assert count == 2
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()


class TestMain:
    """main() returns exit codes correctly."""

    def test_no_args_returns_1(self):
        assert upload_to_db.main([]) == 1

    def test_missing_file_returns_1(self, tmp_path):
        assert upload_to_db.main([str(tmp_path / "nope.sql")]) == 1

    def test_missing_mysql_returns_1(self, tmp_path):
        sql_path = tmp_path / "test.sql"
        sql_path.write_text("SELECT 1;", encoding="utf-8")

        with patch.object(upload_to_db, "connect", side_effect=ImportError("mysql-connector-python is required")):
            result = upload_to_db.main([str(sql_path)])
        assert result == 1

    def test_success_returns_0(self, tmp_path):
        sql_path = tmp_path / "test.sql"
        sql_path.write_text("SELECT 1;", encoding="utf-8")

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = MagicMock()

        with patch.object(upload_to_db, "connect", return_value=mock_conn):
            result = upload_to_db.main([str(sql_path)])

        assert result == 0
        mock_conn.close.assert_called_once()
