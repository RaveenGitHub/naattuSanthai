import datetime
import importlib


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


def test_create_token_uses_configured_jwt_expiry(monkeypatch):
    monkeypatch.setenv("JWT_EXPIRY_HOURS", "24")

    import security
    importlib.reload(security)

    token = security.create_token("operator1")
    payload = security.verify_token(token)
    expires_at = datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc)
    delta_seconds = (expires_at - datetime.datetime.now(datetime.timezone.utc)).total_seconds()

    assert 86000 <= delta_seconds <= 90000


def test_database_uses_environment_database_path(monkeypatch, tmp_path):
    target = tmp_path / "runtime.db"
    monkeypatch.setenv("DATABASE_PATH", str(target))

    import database
    importlib.reload(database)

    assert str(database.DB_PATH) == str(target)
