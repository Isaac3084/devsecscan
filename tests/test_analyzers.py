import pytest
from pathlib import Path
from devsecscan.analyzers.repository_analyzer import RepositoryAnalyzer
from devsecscan.models.domain import RepositoryAnalysisError, RepositoryContext

def test_repository_analyzer_invalid_path():
    analyzer = RepositoryAnalyzer()
    with pytest.raises(RepositoryAnalysisError):
        analyzer.analyze("/path/that/does/not/exist/ever")

def test_repository_analyzer_empty_repo(tmp_path):
    analyzer = RepositoryAnalyzer()
    ctx = analyzer.analyze(str(tmp_path))
    assert ctx.primary_language is None
    assert ctx.total_files == 0
    assert ctx.dependencies == []

def test_repository_analyzer_full_flow(tmp_path):
    # Setup a fake python FastAPI project
    (tmp_path / "main.py").write_text("import fastapi")
    (tmp_path / "requirements.txt").write_text("fastapi==0.95.0\nuvicorn")
    (tmp_path / "poetry.lock").touch()
    
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "api.py").write_text("pass")
    
    analyzer = RepositoryAnalyzer()
    ctx = analyzer.analyze(str(tmp_path))
    
    assert ctx.primary_language == "python"
    assert ctx.detected_languages["python"] == 1.0
    assert ctx.package_manager == "poetry"
    assert ctx.framework == "fastapi"
    assert "fastapi" in ctx.dependencies
    assert "requirements.txt" in ctx.dependency_files
    assert ctx.total_files == 4 # main.py, requirements.txt, poetry.lock, api.py
    assert "src" in ctx.source_directories
