from abc import ABC, abstractmethod
from ..models.analysis import AnalysisResult

class BaseReporter(ABC):
    @abstractmethod
    def report(self, result: AnalysisResult) -> str:
        """Generates a report from the analysis result."""
        pass
