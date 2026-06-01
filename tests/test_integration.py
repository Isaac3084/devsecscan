import pytest
from pathlib import Path

from devsecscan.analyzers.repository_analyzer import RepositoryAnalyzer
from devsecscan.security_detectors.secret_detector import SecretDetector
from devsecscan.findings.finding_engine import FindingEngine
from devsecscan.risk_engine.risk_classifier import RiskClassifier
from devsecscan.risk_engine.deployment_gate import DeploymentGate
from devsecscan.models.domain import RepositoryContext
from devsecscan.models.risk_assessment import DeploymentStatus
from devsecscan.findings.categories import Category


def _build_repo(tmp_path):
    """Helper: creates a realistic mock repository on disk."""
    repo = tmp_path / "myapp"
    repo.mkdir()

    (repo / "pyproject.toml").write_text(
        '[project]\nname = "myapp"\ndependencies = ["fastapi", "uvicorn"]\n'
    )

    src = repo / "src"
    src.mkdir()
    (src / "main.py").write_text(
        'OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"\n'
        'print("Starting server")\n'
    )
    (src / "config.py").write_text(
        'AWS_KEY = "AKIA1234567890123456"\n'
    )

    # Test fixtures should be ignored by the ignore system
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text(
        'FAKE_KEY = "sk-testfaketestfaketestfaketest"\n'
    )

    return repo


def test_full_pipeline_with_risk_engine(tmp_path):
    """
    End-to-end integration: RepositoryAnalyzer → FindingEngine → RiskClassifier → DeploymentGate.
    Verifies that the entire chain produces a correct RepositoryRiskSummary.
    """
    repo = _build_repo(tmp_path)

    # 1. Analyze repo
    analyzer = RepositoryAnalyzer()
    context = analyzer.analyze(str(repo))
    assert context.primary_language.lower() == "python"

    # 2. Detect secrets
    engine = FindingEngine()
    engine.register(SecretDetector())
    findings = engine.run(context)

    # Only src/ secrets should appear; tests/ should be ignored
    file_paths = [f.file_path.replace("\\", "/") for f in findings]
    for fp in file_paths:
        assert "tests/" not in fp, f"Test fixture leaked into findings: {fp}"

    # We expect at least the OpenAI key and the AWS key
    titles = [f.title for f in findings]
    assert any("OpenAI" in t for t in titles)
    assert any("AWS" in t for t in titles)

    # 3. Classify risks
    classifier = RiskClassifier()
    assessments = classifier.classify_all(findings)
    assert len(assessments) == len(findings)

    # At least one assessment should be DO_NOT_DEPLOY (the CRITICAL OpenAI key)
    statuses = [a.deployment_status for a in assessments]
    assert DeploymentStatus.DO_NOT_DEPLOY in statuses

    # 4. Deployment gate
    gate = DeploymentGate()
    summary = gate.evaluate(findings, assessments)

    assert summary.deployment_status == DeploymentStatus.DO_NOT_DEPLOY
    assert summary.critical >= 1
    assert summary.total_findings >= 2


def test_safe_repository(tmp_path):
    """
    Integration test for a clean repository with no secrets.
    Should produce SAFE deployment status.
    """
    repo = tmp_path / "clean_app"
    repo.mkdir()
    src = repo / "src"
    src.mkdir()
    (src / "main.py").write_text('print("Hello, world!")\n')

    analyzer = RepositoryAnalyzer()
    context = analyzer.analyze(str(repo))

    engine = FindingEngine()
    engine.register(SecretDetector())
    findings = engine.run(context)

    classifier = RiskClassifier()
    assessments = classifier.classify_all(findings)

    gate = DeploymentGate()
    summary = gate.evaluate(findings, assessments)

    assert summary.total_findings == 0
    assert summary.deployment_status == DeploymentStatus.SAFE
