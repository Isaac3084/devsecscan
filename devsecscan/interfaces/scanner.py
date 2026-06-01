from abc import ABC, abstractmethod
from ..models.finding import Finding

class BaseScanner(ABC):
    @abstractmethod
    def scan(self, path: str) -> list[Finding]:
        """Scans a path and returns a list of local findings."""
        pass
