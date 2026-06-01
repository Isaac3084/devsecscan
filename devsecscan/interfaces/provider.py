from abc import ABC, abstractmethod
from ..models.analysis import AnalysisRequest, AnalysisResult

class BaseAIProvider(ABC):
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Sends the context and findings to the AI provider and returns the result."""
        pass
