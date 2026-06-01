"""
1. Purpose of file:
This file contains tests for the core interface abstractions of the DevSecScan architecture.
It ensures that the multi-provider system enforces contracts across all implementations.

2. Test strategy:
We utilize pytest to verify standard OOP abstract base class behaviors:
- Abstract Instantiation: Ensures that interfaces cannot be directly instantiated.
- Missing Methods: Ensures that if a developer implements a provider but forgets a core method, it fails at runtime.
- Proper Implementation: Verifies that a correctly implemented subclass passes without issue.

4. Explanation of each test is provided as a docstring within the test functions.
"""

import pytest
from devsecscan.interfaces import (
    BaseAIProvider,
    BaseAnalyzer,
    BaseScanner,
    BaseReporter,
    BaseRiskEngine
)
from devsecscan.models.analysis import AnalysisRequest, AnalysisResult
from devsecscan.models.domain import RepositoryContext, Finding, DeploymentRecommendation

def test_interfaces_are_abstract():
    """
    Why: Validates that foundation interfaces are truly abstract.
    Assumption: Python's abc.ABC combined with @abstractmethod prevents direct instantiation.
    Bug prevented: Prevents developers from attempting to use a raw interface instead of a concrete provider.
    """
    with pytest.raises(TypeError):
        BaseAIProvider()
    with pytest.raises(TypeError):
        BaseAnalyzer()
    with pytest.raises(TypeError):
        BaseScanner()
    with pytest.raises(TypeError):
        BaseReporter()
    with pytest.raises(TypeError):
        BaseRiskEngine()

def test_missing_methods_cause_failure():
    """
    Why: Ensures strict contract enforcement for third-party or future implementations.
    Assumption: Subclasses failing to implement abstract methods will raise a TypeError upon instantiation.
    Bug prevented: Prevents partial implementations (e.g., an AI Provider missing the analyze() method) from crashing the engine midway.
    """
    class IncompleteProvider(BaseAIProvider):
        # Missing def analyze(self, request)
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()

def test_proper_provider_implementation():
    """
    Why: Validates that a correctly implemented provider works as expected.
    Assumption: A subclass implementing all abstract methods can be instantiated and executed.
    Bug prevented: Validates the architecture allows for the future addition of OpenAI, DeepSeek, etc.
    """
    class MockProvider(BaseAIProvider):
        def analyze(self, request: AnalysisRequest) -> AnalysisResult:
            rec = DeploymentRecommendation(
                risk="Test", likelihood="Low", impact="Low", recommendation_text="Test", safe_to_deploy=True
            )
            return AnalysisResult(recommendation=rec, raw_provider_response="Success")
            
    provider = MockProvider()
    ctx = RepositoryContext(project_path="/")
    req = AnalysisRequest(context=ctx)
    result = provider.analyze(req)
    
    assert result.raw_provider_response == "Success"
    assert result.recommendation.safe_to_deploy is True
