import os
import subprocess
import sys
from pathlib import Path


def test_dockerfile_exists():
    assert Path("Dockerfile").exists()


def test_compose_file_exists():
    assert Path("docker-compose.yml").exists()


def test_dockerfile_uses_environment_based_runtime_port():
    content = Path("Dockerfile").read_text(encoding="utf-8")
    assert "${PORT:-8000}" in content or "PORT" in content


def test_compose_file_passes_runtime_environment_settings():
    content = Path("docker-compose.yml").read_text(encoding="utf-8")
    for key in [
        "APP_ENV",
        "APP_DEBUG",
        "PORT",
        "DATABASE_PATH",
        "SECRET_KEY",
        "IMD_API_KEY",
        "IMD_API_TOKEN",
        "IMD_CITY_FORECAST_URL",
    ]:
        assert key in content


def test_env_example_exists():
    assert Path(".env.example").exists()


def test_readme_mentions_project_setup():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "FastAPI" in content or "uvicorn" in content or "Docker" in content
    assert "--env-file .env" in content


def test_app_initializes_a_new_database_on_first_import(tmp_path):
    database_path = tmp_path / "first-run.db"
    environment = os.environ.copy()
    environment["DATABASE_PATH"] = str(database_path)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import app; "
                "from database import get_connection; "
                "conn = get_connection(); "
                "print(conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); "
                "conn.close()"
            ),
        ],
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) >= 3


def test_weather_refresh_has_standalone_worker_and_windows_task_registration():
    assert Path("digital_farming/weather_refresh.py").exists()
    assert Path("scripts/Register-WeatherRefreshTask.ps1").exists()
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "weather_refresh" in readme
    assert "Register-WeatherRefreshTask.ps1" in readme
