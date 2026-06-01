import pytest
from pathlib import Path
from devsecscan.security_detectors.secret_detector import SecretDetector
from devsecscan.models.domain import RepositoryContext
from devsecscan.models.secret_rule import SecretRule
from devsecscan.findings.severity import Severity

def test_secret_detector_masking():
    detector = SecretDetector()
    # Length > 8
    assert detector._mask_secret("sk-1234567890abcdefghijk") == "sk-1234*************hijk"
    # Length <= 8
    assert detector._mask_secret("abcdefgh") == "***"

def test_secret_detector_false_positive_reduction():
    detector = SecretDetector()
    rule = SecretRule(name="Test", description="Test", pattern="test", severity=Severity.HIGH, confidence=0.5)
    
    # Increase
    assert detector._adjust_confidence(rule, "API_KEY = myvalue") == 0.6
    # Decrease
    assert detector._adjust_confidence(rule, "this is an example token") == 0.3
    # Cap at 1.0
    rule_high = SecretRule(name="Test", description="Test", pattern="test", severity=Severity.HIGH, confidence=0.95)
    assert detector._adjust_confidence(rule_high, "API_KEY = myvalue") == 1.0

def test_secret_detector_full_scan(tmp_path):
    # Setup test repo
    (tmp_path / "config.py").write_text('OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"\nAWS_KEY = "AKIA1234567890123456"')
    (tmp_path / "test.py").write_text('dummy_token = "ghp_1234567890abcdefghijk1234567890abcde"')
    
    ctx = RepositoryContext(project_path=str(tmp_path))
    detector = SecretDetector()
    findings = detector.detect(ctx)
    
    # We should have found OpenAI, AWS, Github, and a generic token
    assert len(findings) >= 3
    
    titles = [f.title for f in findings]
    assert "Hardcoded OpenAI API Key" in titles
    assert "Hardcoded AWS Access Key ID" in titles
    assert "Hardcoded GitHub Personal Access Token" in titles
    
    # Check masking
    for finding in findings:
        assert "***" in finding.code_snippet
        assert "sk-1234567890" not in finding.code_snippet

def test_secret_detector_generic_rule(tmp_path):
    (tmp_path / ".env").write_text('password = "supersecretpassword123"\nDB_PASSWORD="dummy"')
    
    ctx = RepositoryContext(project_path=str(tmp_path))
    detector = SecretDetector()
    findings = detector.detect(ctx)
    
    assert len(findings) == 1
    assert findings[0].confidence > 0.3

def test_secret_detector_ignores_rule_definitions_and_explicit_examples(tmp_path):
    (tmp_path / "rules.py").write_text(
        'pattern=r"sk-[A-Za-z0-9]{20,}"\n'
        '    e.g. sk-1234567890abcdefghijk\n'
        'SECRET = "SECRET"\n'
        'OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"\n'
    )

    ctx = RepositoryContext(project_path=str(tmp_path))
    detector = SecretDetector()
    findings = detector.detect(ctx)

    assert len(findings) == 1
    assert findings[0].title == "Hardcoded OpenAI API Key"
