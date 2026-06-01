"""
Risk Classifier: Transforms raw Findings into business-level RiskAssessments.
"""

from ..models.finding import Finding
from ..models.risk_assessment import RiskAssessment
from .risk_registry import RiskRegistry
from .recommendation_engine import RecommendationEngine


class RiskClassifier:
    """
    Takes a list of Findings and produces a list of RiskAssessments
    by consulting the RiskRegistry and RecommendationEngine.
    """

    def __init__(self):
        self._registry = RiskRegistry()
        self._recommender = RecommendationEngine()

    def classify(self, finding: Finding) -> RiskAssessment:
        """Classify a single finding into a RiskAssessment."""
        mapping = self._registry.lookup(finding.category, finding.severity)

        return RiskAssessment(
            finding_id=finding.id,
            risk_type=mapping.risk_type,
            likelihood=mapping.likelihood,
            impact=mapping.impact,
            business_consequence=mapping.business_consequence,
            recommendation=self._recommender.recommend(finding.category),
            deployment_status=mapping.deployment_status,
            confidence=finding.confidence,
        )

    def classify_all(self, findings: list[Finding]) -> list[RiskAssessment]:
        """Classify a batch of findings."""
        return [self.classify(f) for f in findings]
