from pathlib import Path


def test_dockerfile_exists():
    assert Path("Dockerfile").exists()


def test_compose_file_exists():
    assert Path("docker-compose.yml").exists()


def test_env_example_exists():
    assert Path(".env.example").exists()


def test_readme_mentions_project_setup():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "FastAPI" in content or "uvicorn" in content or "Docker" in content
