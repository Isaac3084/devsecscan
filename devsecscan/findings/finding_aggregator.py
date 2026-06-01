from collections import defaultdict
from ..models.finding import Finding
from .severity import Severity

class FindingAggregator:
    def __init__(self):
        self._findings: list[Finding] = []

    def add(self, findings: list[Finding]):
        """Adds findings to the aggregator."""
        self._findings.extend(findings)

    def get_all(self) -> list[Finding]:
        """Returns all aggregated findings without processing."""
        return self._findings

    def deduplicate(self) -> list[Finding]:
        """
        Removes duplicates based on detector_name, file_path, line_number, and title.
        Returns a deduplicated list of findings.
        """
        seen = set()
        unique = []
        for f in self._findings:
            # We use a tuple of identifying traits to detect uniqueness
            ident = (f.detector_name, f.file_path, f.line_number, f.title)
            if ident not in seen:
                seen.add(ident)
                unique.append(f)
        return unique

    def sort(self, deduplicate: bool = True) -> list[Finding]:
        """
        Sorts findings by severity (CRITICAL first).
        """
        findings = self.deduplicate() if deduplicate else list(self._findings)
        
        def severity_key(f: Finding):
            # Parse severity if it's a string, otherwise use the enum
            sev = f.severity
            if isinstance(sev, str):
                try:
                    sev = Severity[sev.upper()]
                except KeyError:
                    sev = Severity.INFO
            return sev
            
        # Sort descending (highest severity first)
        return sorted(findings, key=severity_key, reverse=True)

    def group_by_category(self, deduplicate: bool = True) -> dict[str, list[Finding]]:
        """
        Groups findings by their category.
        """
        findings = self.deduplicate() if deduplicate else list(self._findings)
        grouped = defaultdict(list)
        for f in findings:
            cat = str(f.category)
            grouped[cat].append(f)
        return dict(grouped)
