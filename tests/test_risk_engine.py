import pytest
from devsecscan.models.risk_assessment import (
    DeploymentStatus,
    RiskAssessment,
    RepositoryRiskSummary,
)
from devsecscan.models.finding import Finding
from devsecscan.findings.severity import Severity
from devsecscan.findings.categories import Category
from devsecscan.risk_engine.risk_registry import RiskRegistry
from devsecscan.risk_engine.recommendation_engine import RecommendationEngine
from devsecscan.risk_engine.risk_classifier import RiskClassifier
from devsecscan.risk_engine.deployment_gate import DeploymentGate


# ──────────────────── Model Tests ────────────────────

class TestDeploymentStatus:
    def test_comparison(self):
        assert DeploymentStatus.DO_NOT_DEPLOY > DeploymentStatus.PROCEED_WITH_CAUTION
        assert DeploymentStatus.PROCEED_WITH_CAUTION > DeploymentStatus.SAFE

    def test_serialization(self):
        assert str(DeploymentStatus.DO_NOT_DEPLOY) == "DO_NOT_DEPLOY"


class TestRiskAssessment:
    def test_creation(self):
        ra = RiskAssessment(
            finding_id="abc-123",
            risk_type="Credential Exposure",
            likelihood="HIGH",
            impact="Unexpected Billing",
            business_consequence="Third parties use paid APIs.",
            recommendation="Move key to env vars.",
            deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
            confidence=0.95,
        )
        assert ra.risk_type == "Credential Exposure"
        assert ra.deployment_status == DeploymentStatus.DO_NOT_DEPLOY

    def test_json_serialization(self):
        ra = RiskAssessment(
            finding_id="x",
            risk_type="Test",
            likelihood="LOW",
            impact="None",
            business_consequence="None",
            recommendation="None",
            deployment_status=DeploymentStatus.SAFE,
        )
        data = ra.model_dump()
        assert data["deployment_status"] == "SAFE"


class TestRepositoryRiskSummary:
    def test_defaults(self):
        summary = RepositoryRiskSummary()
        assert summary.total_findings == 0
        assert summary.deployment_status == DeploymentStatus.SAFE
        assert summary.assessments == []


# ──────────────────── Registry Tests ────────────────────

class TestRiskRegistry:
    def test_known_mapping(self):
        registry = RiskRegistry()
        mapping = registry.lookup(Category.SECRET, Severity.CRITICAL)
        assert mapping.risk_type == "Credential Exposure"
        assert mapping.deployment_status == DeploymentStatus.DO_NOT_DEPLOY

    def test_unknown_mapping_fallback(self):
        registry = RiskRegistry()
        mapping = registry.lookup("TOTALLY_FAKE", Severity.LOW)
        assert mapping.risk_type == "Unknown Risk"

    def test_string_severity(self):
        registry = RiskRegistry()
        mapping = registry.lookup("SECRET", "CRITICAL")
        assert mapping.risk_type == "Credential Exposure"


# ──────────────────── Recommendation Engine Tests ────────────────────

class TestRecommendationEngine:
    def test_known_category(self):
        engine = RecommendationEngine()
        rec = engine.recommend(Category.SECRET)
        assert "environment variables" in rec

    def test_unknown_category(self):
        engine = RecommendationEngine()
        rec = engine.recommend("DOES_NOT_EXIST")
        assert "security team" in rec


# ──────────────────── Risk Classifier Tests ────────────────────

class TestRiskClassifier:
    def test_classify_known_finding(self):
        classifier = RiskClassifier()
        finding = Finding(
            title="Hardcoded OpenAI API Key",
            description="Found sk-...",
            category=Category.SECRET,
            severity=Severity.CRITICAL,
            confidence=0.98,
        )
        assessment = classifier.classify(finding)
        assert assessment.risk_type == "Credential Exposure"
        assert assessment.deployment_status == DeploymentStatus.DO_NOT_DEPLOY
        assert assessment.confidence == 0.98

    def test_classify_unknown_finding(self):
        classifier = RiskClassifier()
        finding = Finding(
            title="Unknown Issue",
            description="Something weird",
            category="WEIRD_CATEGORY",
            severity="WEIRD_SEVERITY",
        )
        assessment = classifier.classify(finding)
        assert assessment.risk_type == "Unknown Risk"
        assert assessment.deployment_status == DeploymentStatus.PROCEED_WITH_CAUTION

    def test_classify_all(self):
        classifier = RiskClassifier()
        findings = [
            Finding(title="A", description="a", category=Category.SECRET, severity=Severity.CRITICAL),
            Finding(title="B", description="b", category=Category.AUTHORIZATION, severity=Severity.HIGH),
        ]
        assessments = classifier.classify_all(findings)
        assert len(assessments) == 2


# ──────────────────── Deployment Gate Tests ────────────────────

class TestDeploymentGate:
    def _make_finding(self, severity):
        return Finding(title="T", description="d", category=Category.SECRET, severity=severity)

    def test_safe_when_no_findings(self):
        gate = DeploymentGate()
        summary = gate.evaluate([], [])
        assert summary.deployment_status == DeploymentStatus.SAFE
        assert summary.total_findings == 0

    def test_do_not_deploy_on_critical(self):
        gate = DeploymentGate()
        findings = [self._make_finding(Severity.CRITICAL)]
        summary = gate.evaluate(findings, [])
        assert summary.deployment_status == DeploymentStatus.DO_NOT_DEPLOY
        assert summary.critical == 1

    def test_caution_on_high(self):
        gate = DeploymentGate()
        findings = [self._make_finding(Severity.HIGH)]
        summary = gate.evaluate(findings, [])
        assert summary.deployment_status == DeploymentStatus.PROCEED_WITH_CAUTION

    def test_do_not_deploy_on_many_highs(self):
        gate = DeploymentGate(high_threshold=2)
        findings = [self._make_finding(Severity.HIGH) for _ in range(3)]
        summary = gate.evaluate(findings, [])
        assert summary.deployment_status == DeploymentStatus.DO_NOT_DEPLOY

    def test_safe_on_only_lows(self):
        gate = DeploymentGate()
        findings = [self._make_finding(Severity.LOW) for _ in range(5)]
        summary = gate.evaluate(findings, [])
        assert summary.deployment_status == DeploymentStatus.SAFE

    def test_counts_are_correct(self):
        gate = DeploymentGate()
        findings = [
            self._make_finding(Severity.CRITICAL),
            self._make_finding(Severity.HIGH),
            self._make_finding(Severity.MEDIUM),
            self._make_finding(Severity.LOW),
            self._make_finding(Severity.INFO),
        ]
        summary = gate.evaluate(findings, [])
        assert summary.critical == 1
        assert summary.high == 1
        assert summary.medium == 1
        assert summary.low == 1
        assert summary.info == 1
        assert summary.total_findings == 5
