import pytest
from devsecscan.interfaces import BaseAIProvider, BaseAnalyzer, BaseScanner, BaseReporter, BaseRiskEngine

def test_interfaces_are_abstract():
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

def test_mock_provider():
    class MockProvider(BaseAIProvider):
        def analyze(self, request):
            return "result"
            
    provider = MockProvider()
    assert provider.analyze(None) == "result"
