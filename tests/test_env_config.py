import importlib
import os


def test_settings_reads_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Farm Ops")
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("DATABASE_PATH", "/tmp/test-farm.db")
    monkeypatch.setenv("SECRET_KEY", "env-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS512")
    monkeypatch.setenv("JWT_EXPIRY_HOURS", "24")

    import digital_farming.config as config
    importlib.reload(config)

    assert config.settings.app_name == "Farm Ops"
    assert config.settings.app_version == "9.9.9"
    assert config.settings.debug is True
    assert config.settings.database_path == "/tmp/test-farm.db"
    assert config.settings.secret_key == "env-secret"
    assert config.settings.jwt_algorithm == "HS512"
    assert config.settings.jwt_expiry_hours == 24


def test_security_uses_environment_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "security-secret")

    import security
    importlib.reload(security)

    assert security.SECRET_KEY == "security-secret"
