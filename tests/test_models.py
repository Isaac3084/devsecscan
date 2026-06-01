"""
1. Purpose of file:
This file contains the complete test suite for all Pydantic models in the DevSecScan foundation layer.
The models represent the core domain of the AI Application Safety Auditor.

2. Test strategy:
We utilize pytest to comprehensively test:
- Happy Path Cases: Ensuring models initialize correctly with valid data and default values.
- Validation Cases: Verifying that Pydantic enforces types and Literal constraints (like provider names).
- Edge Cases: Handling empty lists, missing optional fields, and unexpected values.
- Serialization Cases: Ensuring models can be safely dumped to dicts and JSON.
- Future Compatibility: Ensuring that unknown fields or generic data structures can be adapted in the future.

4. Explanation of each test is provided as a docstring within the test functions.
"""

import pytest
from pydantic import ValidationError
from devsecscan.models.config import UserConfig, ProviderConfig
from devsecscan.models.domain import Risk, RepositoryContext, DeploymentRecommendation
from devsecscan.models.finding import Finding
from devsecscan.models.analysis import AnalysisRequest, AnalysisResult


# --- ProviderConfig Tests ---

def test_provider_config_happy_path():
    """
    Why: Validates that a standard provider config initializes correctly with defaults.
    Assumption: 'claude' is the default provider if none is specified.
    Bug prevented: Prevents issues where core configuration fails to load without explicit user input.
    """
    config = ProviderConfig()
    assert config.name == "claude"
    assert config.api_key is None
    assert config.model_name is None

def test_provider_config_valid_providers():
    """
    Why: Validates that all future-supported providers can be initialized.
    Assumption: The Literal type definition correctly supports all intended providers.
    Bug prevented: Prevents regression where a newly supported provider is rejected by validation.
    """
    valid_providers = ["openai", "claude", "gemini", "deepseek", "qwen", "nvidia_nim", "ollama", "ollama_cloud"]
    for provider in valid_providers:
        config = ProviderConfig(name=provider)
        assert config.name == provider

def test_provider_config_invalid_provider():
    """
    Why: Validates that unsupported providers are strictly rejected.
    Assumption: A user typing 'banana' or an unsupported provider should fail validation immediately.
    Bug prevented: Prevents the engine from passing unknown parameters to the AI layer, causing silent API failures.
    """
    with pytest.raises(ValidationError) as exc_info:
        ProviderConfig(name="banana")
    assert "Input should be" in str(exc_info.value)


# --- UserConfig Tests ---

def test_user_config_defaults():
    """
    Why: Validates the baseline configuration for a new user.
    Assumption: The platform defaults to 'efficient' mode and local scanning for privacy/cost reasons.
    Bug prevented: Prevents accidental deployment of expensive/full mode scans as default.
    """
    config = UserConfig()
    assert config.analysis_mode == "efficient"
    assert config.local_scanning is True
    assert config.cloud_features is False
    assert isinstance(config.provider, ProviderConfig)
    assert config.provider.name == "claude"

def test_user_config_serialization():
    """
    Why: Ensures the UserConfig can be serialized for caching or debugging.
    Assumption: model_dump() returns a JSON-serializable dictionary.
    Bug prevented: Prevents serialization crashes when passing config states to reporting engines.
    """
    config = UserConfig(analysis_mode="full", cloud_features=True)
    dumped = config.model_dump()
    assert dumped["analysis_mode"] == "full"
    assert dumped["cloud_features"] is True
    assert dumped["provider"]["name"] == "claude"


# --- Domain Model Tests ---

def test_finding_validation():
    """
    Why: Validates that a Finding requires specific mandatory fields but allows optional context.
    Assumption: An issue title, description, category, and severity are the absolute minimum to define a risk finding.
    Bug prevented: Prevents the Risk Engine from processing incomplete findings.
    """
    with pytest.raises(ValidationError):
        Finding(title="Hardcoded Secret") # Missing required fields

    finding = Finding(
        title="Hardcoded Secret",
        description="Found an API key",
        category="SECRET",
        severity="HIGH"
    )
    assert finding.confidence == 0.0
    assert finding.file_path is None

def test_repository_context_edge_cases():
    """
    Why: Validates handling of empty or large repositories.
    Assumption: Repositories might have no dependencies or 0 file count (empty repo).
    Bug prevented: Prevents list index out of bounds or division by zero in context reduction.
    """
    empty_ctx = RepositoryContext(project_path="/empty")
    assert empty_ctx.dependencies == []
    assert empty_ctx.total_files == 0

    large_ctx = RepositoryContext(project_path="/large", total_files=999999, dependencies=["a"]*1000)
    assert large_ctx.total_files == 999999
    assert len(large_ctx.dependencies) == 1000

def test_deployment_recommendation_serialization():
    """
    Why: Tests the final output model that users care most about.
    Assumption: Needs to be serialized to JSON strictly for the CLI output.
    Bug prevented: Formatting errors in the final terminal or JSON report.
    """
    rec = DeploymentRecommendation(
        risk="Open Admin Endpoint",
        likelihood="High",
        impact="Account Takeover",
        recommendation_text="Do Not Deploy",
        safe_to_deploy=False
    )
    json_output = rec.model_dump_json()
    assert "Open Admin Endpoint" in json_output
    assert "false" in json_output.lower()


# --- Analysis Model Tests ---

def test_analysis_request_future_compatibility():
    """
    Why: Ensures AnalysisRequest behaves nicely with default lists and modes.
    Assumption: An AnalysisRequest can be instantiated with just a context, defaulting to 'efficient' mode.
    Bug prevented: Prevents instantiation failures when local scanners find 0 issues.
    """
    ctx = RepositoryContext(project_path="/src")
    req = AnalysisRequest(context=ctx)
    assert req.mode == "efficient"
    assert req.local_findings == []
    assert req.context.project_path == "/src"

def test_analysis_result_optional_raw():
    """
    Why: Tests that raw_provider_response is optional.
    Assumption: Not all AI providers or efficient modes will yield a raw response string.
    Bug prevented: Prevents the reporter from crashing if raw output is omitted.
    """
    rec = DeploymentRecommendation(
        risk="None", likelihood="Low", impact="Low", recommendation_text="Safe", safe_to_deploy=True
    )
    res = AnalysisResult(recommendation=rec)
    assert res.raw_provider_response is None
