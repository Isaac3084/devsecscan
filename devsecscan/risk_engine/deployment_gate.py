"""
Deployment Gate: Evaluates all RiskAssessments and produces a final
RepositoryRiskSummary with a deployment recommendation.
"""

from ..models.finding import Finding
from ..models.risk_assessment import (
    DeploymentStatus,
    RiskAssessment,
    RepositoryRiskSummary,
)
from ..findings.severity import Severity


class DeploymentGate:
    """
    Configurable gate that decides whether a repository is safe to deploy
    based on the number and severity of findings.
    """

    def __init__(
        self,
        critical_threshold: int = 1,
        high_threshold: int = 3,
        medium_threshold: int = 10,
    ):
        """
        :param critical_threshold: Any CRITICAL count >= this → DO_NOT_DEPLOY
        :param high_threshold: Any HIGH count >= this → DO_NOT_DEPLOY
        :param medium_threshold: Any MEDIUM count >= this → PROCEED_WITH_CAUTION
        """
        self.critical_threshold = critical_threshold
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def evaluate(
        self,
        findings: list[Finding],
        assessments: list[RiskAssessment],
    ) -> RepositoryRiskSummary:
        """
        Produce a RepositoryRiskSummary from the given findings and their
        corresponding risk assessments.
        """
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for f in findings:
            sev = f.severity
            if isinstance(sev, str):
                try:
                    sev = Severity[sev.upper()]
                except KeyError:
                    sev = Severity.INFO

            if sev == Severity.CRITICAL:
                counts["critical"] += 1
            elif sev == Severity.HIGH:
                counts["high"] += 1
            elif sev == Severity.MEDIUM:
                counts["medium"] += 1
            elif sev == Severity.LOW:
                counts["low"] += 1
            else:
                counts["info"] += 1

        # Determine deployment status based on thresholds
        if counts["critical"] >= self.critical_threshold:
            status = DeploymentStatus.DO_NOT_DEPLOY
        elif counts["high"] >= self.high_threshold:
            status = DeploymentStatus.DO_NOT_DEPLOY
        elif counts["medium"] >= self.medium_threshold or counts["high"] >= 1:
            status = DeploymentStatus.PROCEED_WITH_CAUTION
        else:
            status = DeploymentStatus.SAFE

        return RepositoryRiskSummary(
            total_findings=len(findings),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            info=counts["info"],
            deployment_status=status,
            assessments=assessments,
        )
