import pytest
from pydantic import ValidationError
from devsecscan.models import UserConfig, ProviderConfig, Risk, Finding, RepositoryContext, AnalysisRequest, AnalysisResult, DeploymentRecommendation

def test_provider_config_defaults():
    config = ProviderConfig()
    assert config.name == "claude"
    assert config.api_key is None

def test_user_config_defaults():
    config = UserConfig()
    assert config.analysis_mode == "efficient"
    assert config.local_scanning is True
    assert config.cloud_features is False
    assert config.provider.name == "claude"

def test_finding_creation():
    finding = Finding(
        issue="Hardcoded Key",
        potential_consequences="Abuse",
        likelihood="High"
    )
    assert finding.issue == "Hardcoded Key"
    assert finding.severity is None

def test_repository_context():
    ctx = RepositoryContext(path="/tmp/test", file_count=5)
    assert ctx.path == "/tmp/test"
    assert ctx.file_count == 5
    assert ctx.dependencies == []

def test_deployment_recommendation():
    rec = DeploymentRecommendation(
        risk="High",
        likelihood="High",
        impact="High",
        recommendation_text="Do not deploy",
        safe_to_deploy=False
    )
    assert rec.safe_to_deploy is False

def test_analysis_request():
    ctx = RepositoryContext(path="/tmp")
    req = AnalysisRequest(context=ctx)
    assert req.mode == "efficient"
    assert req.local_findings == []
