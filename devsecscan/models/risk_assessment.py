from enum import Enum
from pydantic import BaseModel, Field

_DEPLOYMENT_ORDER = {"SAFE": 0, "PROCEED_WITH_CAUTION": 1, "DO_NOT_DEPLOY": 2}


class DeploymentStatus(str, Enum):
    """Final deployment recommendation for a repository."""
    SAFE = "SAFE"
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"
    DO_NOT_DEPLOY = "DO_NOT_DEPLOY"

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return _DEPLOYMENT_ORDER[self.value] < _DEPLOYMENT_ORDER[other.value]
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return _DEPLOYMENT_ORDER[self.value] > _DEPLOYMENT_ORDER[other.value]
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return _DEPLOYMENT_ORDER[self.value] <= _DEPLOYMENT_ORDER[other.value]
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return _DEPLOYMENT_ORDER[self.value] >= _DEPLOYMENT_ORDER[other.value]
        return NotImplemented

    def __str__(self):
        return self.value


class RiskAssessment(BaseModel):
    """Maps a single Finding to its business-level risk assessment."""
    finding_id: str
    risk_type: str
    likelihood: str
    impact: str
    business_consequence: str
    recommendation: str
    deployment_status: DeploymentStatus
    confidence: float = 0.0


class RepositoryRiskSummary(BaseModel):
    """Aggregated risk summary for the entire repository."""
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    deployment_status: DeploymentStatus = DeploymentStatus.SAFE
    assessments: list[RiskAssessment] = Field(default_factory=list)
