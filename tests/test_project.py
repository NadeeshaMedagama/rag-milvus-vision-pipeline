"""Basic test suite for Python RAG application."""
import pytest
from pathlib import Path


def test_project_structure():
    """Test that essential project files exist."""
    project_root = Path(__file__).parent.parent

    # Check essential files
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "Dockerfile").exists()
    assert (project_root / "main.py").exists()
    assert (project_root / "query.py").exists()
    assert (project_root / "api_server.py").exists()

    # Check essential directories
    assert (project_root / "config").exists()
    assert (project_root / "services").exists()
    assert (project_root / "workflows").exists()
    assert (project_root / "models").exists()
    assert (project_root / "interfaces").exists()


def test_imports():
    """Test that core modules can be imported."""
    # Test config imports
    try:
        from config import settings
        assert settings is not None
    except ImportError as e:
        pytest.skip(f"Config import failed (expected if dependencies not installed): {e}")

    # Test models imports
    try:
        from models import data_models
        assert data_models is not None
    except ImportError as e:
        pytest.skip(f"Models import failed: {e}")


def test_environment_variables():
    """Test that environment variable handling works."""
    from pydantic_settings import BaseSettings

    # This should not raise an error even without .env
    class TestSettings(BaseSettings):
        test_var: str = "default"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"

    settings = TestSettings()
    assert settings.test_var == "default"


def test_readme_content():
    """Test that README contains important sections."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # Check for important sections
    assert "Python RAG with Milvus" in content
    assert "CI/CD Pipeline" in content
    assert "Features" in content
    assert "Installation" in content
    assert "Docker" in content


def test_requirements_file():
    """Test that requirements.txt is valid and contains key dependencies."""
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    content = requirements_path.read_text()

    # Check for key dependencies
    assert "langgraph" in content
    assert "langchain" in content
    assert "pymilvus" in content
    assert "openai" in content or "langchain-openai" in content
    assert "flask" in content


def test_dockerfile_validity():
    """Test that Dockerfile contains essential instructions."""
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    content = dockerfile_path.read_text()

    # Check for essential Dockerfile instructions
    assert "FROM python:" in content
    assert "COPY requirements.txt" in content
    assert "RUN pip install" in content
    assert "EXPOSE 5000" in content
    assert "CMD" in content or "ENTRYPOINT" in content


def test_dockerfile_excludes_build_essential():
    """Test Dockerfile avoids unnecessary compiler toolchain in runtime image."""
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    content = dockerfile_path.read_text()

    assert "build-essential" not in content


@pytest.mark.parametrize("workflow_file", [
    "ci.yml",
    "codeql.yml",
    "docker.yml",
    "release.yml",
    "dependency-check.yml",
    "dependabot-auto-merge.yml"
])
def test_workflow_files_exist(workflow_file):
    """Test that all CI/CD workflow files exist."""
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / workflow_file
    assert workflow_path.exists(), f"Workflow file {workflow_file} should exist"


def test_dependabot_config():
    """Test that Dependabot configuration exists."""
    dependabot_path = Path(__file__).parent.parent / ".github" / "dependabot.yml"
    assert dependabot_path.exists()

    content = dependabot_path.read_text()
    assert "version: 2" in content
    assert "package-ecosystem" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
