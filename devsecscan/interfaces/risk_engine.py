from abc import ABC, abstractmethod
from ..models.domain import Finding, DeploymentRecommendation

class BaseRiskEngine(ABC):
    @abstractmethod
    def assess(self, findings: list[Finding]) -> DeploymentRecommendation:
        """Assesses local findings and determines the deployment recommendation locally."""
        pass
