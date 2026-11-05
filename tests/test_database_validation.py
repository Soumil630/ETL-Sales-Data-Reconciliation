import sys
import types

import pytest

from src.database import load_target


def stub_mysql_connector(monkeypatch, connect):
    mysql_module = types.ModuleType("mysql")
    mysql_module.__path__ = []
    connector_module = types.ModuleType("mysql.connector")
    connector_module.connect = connect
    mysql_module.connector = connector_module
    monkeypatch.setitem(sys.modules, "mysql", mysql_module)
    monkeypatch.setitem(sys.modules, "mysql.connector", connector_module)


def test_database_rejects_non_select_queries(tmp_path):
    config = {"target": {"mode": "mysql", "query": "DELETE FROM fact_sales"}}

    with pytest.raises(ValueError, match="read-only SELECT"):
        load_target(config, tmp_path)


def test_database_requires_environment_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("TEST_DB_USER", raising=False)
    config = {
        "target": {"mode": "mysql", "query": "SELECT 1"},
        "database": {
            "user_env": "TEST_DB_USER",
            "password_env": "TEST_DB_PASSWORD",
        },
    }

    with pytest.raises(ValueError, match="Database user is unset"):
        load_target(config, tmp_path)


def test_database_uses_credentials_from_config(tmp_path, monkeypatch):
    captured = {}

    class Cursor:
        description = [("value",)]

        def execute(self, query):
            assert query == "SELECT 1"

        def fetchall(self):
            return [(1,)]

        def close(self):
            pass

    class Connection:
        def cursor(self, dictionary):
            assert dictionary is True
            return Cursor()

        def close(self):
            pass

    def connect(**kwargs):
        captured.update(kwargs)
        return Connection()

    stub_mysql_connector(monkeypatch, connect)
    config = {
        "target": {"mode": "mysql", "query": "SELECT 1"},
        "database": {
            "host": "localhost",
            "database": "test_db",
            "user": "config-user",
            "password": "config-password",
        },
    }

    frame, _ = load_target(config, tmp_path)

    assert frame.to_dict(orient="records") == [{"value": 1}]
    assert captured["user"] == "config-user"
    assert captured["password"] == "config-password"


def test_database_environment_credentials_override_config(tmp_path, monkeypatch):
    captured = {}

    class Cursor:
        description = [("value",)]

        def execute(self, query):
            pass

        def fetchall(self):
            return [(1,)]

        def close(self):
            pass

    class Connection:
        def cursor(self, dictionary):
            return Cursor()

        def close(self):
            pass

    def connect(**kwargs):
        captured.update(kwargs)
        return Connection()

    stub_mysql_connector(monkeypatch, connect)
    monkeypatch.setenv("TEST_DB_USER", "env-user")
    monkeypatch.setenv("TEST_DB_PASSWORD", "env-password")
    config = {
        "target": {"mode": "mysql", "query": "SELECT 1"},
        "database": {
            "user": "config-user",
            "password": "config-password",
            "user_env": "TEST_DB_USER",
            "password_env": "TEST_DB_PASSWORD",
            "host": "localhost",
            "database": "test_db",
        },
    }

    load_target(config, tmp_path)

    assert captured["user"] == "env-user"
    assert captured["password"] == "env-password"
