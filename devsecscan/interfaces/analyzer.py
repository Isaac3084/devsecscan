from abc import ABC, abstractmethod
from ..models.domain import RepositoryContext

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, path: str) -> RepositoryContext:
        """Analyzes a repository and extracts its context (framework, language, etc)."""
        pass
