import pytest
from pathlib import Path

from devsecscan.analyzers.repository_analyzer import RepositoryAnalyzer
from devsecscan.security_detectors.secret_detector import SecretDetector
from devsecscan.findings.finding_engine import FindingEngine
from devsecscan.models.domain import RepositoryContext
from devsecscan.findings.categories import Category

def test_full_pipeline_integration(tmp_path):
    """
    End-to-End Integration Test:
    Verifies that the RepositoryAnalyzer correctly identifies the project metadata,
    and the FindingEngine correctly orchestrates the SecretDetector to find
    secrets across the mock repository, returning masked findings.
    """
    # 1. Setup Mock Repository
    repo_path = tmp_path / "integration_repo"
    repo_path.mkdir()
    
    # Metadata files for Repository Analyzer
    (repo_path / "pyproject.toml").write_text('''
[project]
name = "integration_test"
dependencies = ["fastapi", "uvicorn"]
    ''')
    
    # Source code with a secret
    src_dir = repo_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text('''
import os
def start():
    # Intentionally vulnerable code for testing
    OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"
    print("Starting server")
    ''')
    
    # Another file with a dummy generic secret
    (src_dir / "auth.js").write_text('''
const token = "dummy_token_12345";
    ''')

    # 2. Run Repository Analyzer
    analyzer = RepositoryAnalyzer()
    context = analyzer.analyze(str(repo_path))
    
    # Verify Context
    assert context.primary_language.lower() == "python"
    assert "fastapi" in context.dependencies
    assert context.framework == "fastapi"
    
    # 3. Setup Finding Engine & Secret Detector
    engine = FindingEngine()
    secret_detector = SecretDetector()
    engine.register(secret_detector)
    
    # 4. Execute Engine
    findings = engine.run(context)
    
    # 5. Verify Integrated Findings
    assert len(findings) >= 1
    
    # The findings should be sorted by Severity.
    # The OpenAI key is CRITICAL, so it should be near the top.
    openai_findings = [f for f in findings if "OpenAI" in f.title]
    assert len(openai_findings) == 1
    
    finding = openai_findings[0]
    assert finding.category == Category.SECRET
    assert "sk-1234" in finding.code_snippet 
    assert "7890" in finding.code_snippet
    assert "****************" in finding.code_snippet
    assert "sk-1234567890abcdef" not in finding.code_snippet # Ensure masking applied
    
    # Ensure line number and path resolution worked
    assert finding.file_path.replace("\\", "/").endswith("src/main.py")
    assert finding.line_number == 5
    assert finding.detector_name == "SecretDetector"
