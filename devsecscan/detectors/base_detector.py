from abc import ABC, abstractmethod
from ..models.domain import RepositoryContext
from ..models.finding import Finding

class BaseDetector(ABC):
    @abstractmethod
    def detect(self, context: RepositoryContext) -> list[Finding]:
        """
        Executes the detection logic on the given repository context.
        Returns a list of standardized Findings.
        """
        pass
