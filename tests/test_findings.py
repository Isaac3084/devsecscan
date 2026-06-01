import pytest
from devsecscan.findings.severity import Severity
from devsecscan.findings.categories import Category
from devsecscan.models.finding import Finding
from devsecscan.findings.finding_aggregator import FindingAggregator
from devsecscan.findings.finding_engine import FindingEngine
from devsecscan.detectors.base_detector import BaseDetector
from devsecscan.models.domain import RepositoryContext

def test_severity_comparison():
    assert Severity.CRITICAL > Severity.HIGH
    assert Severity.HIGH > Severity.MEDIUM
    assert Severity.MEDIUM > Severity.LOW
    assert Severity.LOW > Severity.INFO
    assert Severity.CRITICAL > Severity.INFO

def test_category_enum():
    assert str(Category.SECRET) == "SECRET"
    assert Category.AUTHENTICATION == "AUTHENTICATION"

def test_finding_model_defaults():
    finding = Finding(
        title="Test",
        description="Desc",
        category=Category.SECRET,
        severity=Severity.HIGH
    )
    assert finding.id is not None
    assert finding.confidence == 0.0
    assert finding.metadata == {}

def test_finding_aggregator_deduplication():
    aggregator = FindingAggregator()
    f1 = Finding(title="Duplicate", description="1", category="SECRET", severity="HIGH", file_path="main.py", line_number=10, detector_name="TestDetector")
    f2 = Finding(title="Duplicate", description="2", category="SECRET", severity="HIGH", file_path="main.py", line_number=10, detector_name="TestDetector")
    f3 = Finding(title="Unique", description="3", category="SECRET", severity="HIGH", file_path="main.py", line_number=11, detector_name="TestDetector")
    
    aggregator.add([f1, f2, f3])
    deduped = aggregator.deduplicate()
    
    assert len(deduped) == 2
    titles = [f.title for f in deduped]
    assert "Duplicate" in titles
    assert "Unique" in titles

def test_finding_aggregator_sorting():
    aggregator = FindingAggregator()
    f1 = Finding(title="Low", description="1", category="SECRET", severity=Severity.LOW)
    f2 = Finding(title="Critical", description="2", category="SECRET", severity=Severity.CRITICAL)
    f3 = Finding(title="High", description="3", category="SECRET", severity=Severity.HIGH)
    f4 = Finding(title="Medium", description="4", category="SECRET", severity="MEDIUM") # string severity fallback test
    
    aggregator.add([f1, f2, f3, f4])
    sorted_findings = aggregator.sort(deduplicate=False)
    
    assert sorted_findings[0].title == "Critical"
    assert sorted_findings[1].title == "High"
    assert sorted_findings[2].title == "Medium"
    assert sorted_findings[3].title == "Low"

def test_finding_aggregator_grouping():
    aggregator = FindingAggregator()
    f1 = Finding(title="1", description="1", category=Category.SECRET, severity=Severity.LOW)
    f2 = Finding(title="2", description="2", category=Category.AUTHORIZATION, severity=Severity.HIGH)
    
    aggregator.add([f1, f2])
    grouped = aggregator.group_by_category(deduplicate=False)
    
    assert len(grouped["SECRET"]) == 1
    assert len(grouped["AUTHORIZATION"]) == 1

class MockDetectorPass(BaseDetector):
    def detect(self, context: RepositoryContext) -> list[Finding]:
        return [Finding(title="Found 1", description="desc", category=Category.SECRET, severity=Severity.HIGH)]

class MockDetectorFail(BaseDetector):
    def detect(self, context: RepositoryContext) -> list[Finding]:
        raise ValueError("Simulated crash")

def test_finding_engine_error_handling(caplog):
    engine = FindingEngine()
    engine.register(MockDetectorFail())
    engine.register(MockDetectorPass())
    
    ctx = RepositoryContext(project_path="/tmp")
    findings = engine.run(ctx)
    
    # Engine should not crash, and should return the valid findings
    assert len(findings) == 1
    assert findings[0].title == "Found 1"
    
    # Check that error was logged
    assert "Detector MockDetectorFail crashed" in caplog.text
