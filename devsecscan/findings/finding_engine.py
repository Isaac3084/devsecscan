import logging
from ..detectors.base_detector import BaseDetector
from ..models.domain import RepositoryContext
from ..models.finding import Finding
from .finding_aggregator import FindingAggregator

logger = logging.getLogger(__name__)

class FindingEngine:
    def __init__(self):
        self._detectors: list[BaseDetector] = []

    def register(self, detector: BaseDetector):
        """Registers a new security detector to the engine."""
        self._detectors.append(detector)

    def run(self, context: RepositoryContext) -> list[Finding]:
        """
        Executes all registered detectors against the repository context.
        Aggregates, deduplicates, and sorts the findings.
        Gracefully handles detector crashes.
        """
        aggregator = FindingAggregator()

        for detector in self._detectors:
            try:
                findings = detector.detect(context)
                if findings:
                    aggregator.add(findings)
            except Exception as e:
                # Log failure but do not crash the engine
                detector_name = detector.__class__.__name__
                logger.error(f"Detector {detector_name} crashed during execution: {e}")

        return aggregator.sort()
