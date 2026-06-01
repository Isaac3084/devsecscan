from devsecscan.findings.categories import Category
from devsecscan.findings.severity import Severity
from devsecscan.models.finding import Finding
from devsecscan.models.risk_assessment import DeploymentStatus, RepositoryRiskSummary
from devsecscan.risk_engine.deployment_gate import DeploymentGate
from devsecscan.risk_engine.risk_classifier import RiskClassifier
from devsecscan.risk_engine.summary_formatter import (
    format_repository_risk_summary,
    get_top_risks,
)


def test_get_top_risks_orders_by_frequency_then_name():
    classifier = RiskClassifier()
    findings = [
        Finding(title="A", description="a", category=Category.SECRET, severity=Severity.CRITICAL),
        Finding(title="B", description="b", category=Category.SECRET, severity=Severity.HIGH),
        Finding(title="C", description="c", category=Category.AUTHORIZATION, severity=Severity.HIGH),
    ]
    assessments = classifier.classify_all(findings)
    summary = RepositoryRiskSummary(assessments=assessments)

    assert get_top_risks(summary) == ["Credential Exposure", "Unauthorized Access"]
    assert get_top_risks(summary, limit=1) == ["Credential Exposure"]
    assert get_top_risks(summary, limit=0) == []


def test_format_repository_risk_summary_includes_counts_status_and_top_risks():
    findings = [
        Finding(title="A", description="a", category=Category.SECRET, severity=Severity.CRITICAL),
        Finding(title="B", description="b", category=Category.AUTHORIZATION, severity=Severity.HIGH),
    ]
    assessments = RiskClassifier().classify_all(findings)
    summary = DeploymentGate().evaluate(findings, assessments)

    output = format_repository_risk_summary(summary)

    assert "Repository Risk Summary" in output
    assert "Total Findings: 2" in output
    assert "Critical Issues: 1" in output
    assert "High Issues: 1" in output
    assert "Deployment Recommendation:\nDO_NOT_DEPLOY" in output
    assert "1. Credential Exposure" in output
    assert "2. Unauthorized Access" in output


def test_format_repository_risk_summary_handles_no_risks():
    summary = RepositoryRiskSummary(deployment_status=DeploymentStatus.SAFE)

    output = format_repository_risk_summary(summary)

    assert "Total Findings: 0" in output
    assert "Deployment Recommendation:\nSAFE" in output
    assert "Top Risks:\nNone" in output
