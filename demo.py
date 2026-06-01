from devsecscan.analyzers.repository_analyzer import RepositoryAnalyzer
from devsecscan.findings.finding_engine import FindingEngine
from devsecscan.security_detectors.secret_detector import SecretDetector
from devsecscan.risk_engine.risk_classifier import RiskClassifier
from devsecscan.risk_engine.deployment_gate import DeploymentGate

def main():
    # 1. Analyze the target repository
    print("Analyzing repository...")
    analyzer = RepositoryAnalyzer()
    context = analyzer.analyze(".")

    print(f"Project: {context.primary_language} | Framework: {context.framework or 'None'}")

    # 2. Detect secrets
    engine = FindingEngine()
    engine.register(SecretDetector())

    print("\nScanning for secrets...")
    findings = engine.run(context)

    # 3. Classify risks
    classifier = RiskClassifier()
    assessments = classifier.classify_all(findings)

    # 4. Deployment gate
    gate = DeploymentGate()
    summary = gate.evaluate(findings, assessments)

    # 5. Output
    print(f"\n{'='*55}")
    print(f"  REPOSITORY RISK SUMMARY")
    print(f"{'='*55}")
    print(f"  Total Findings:  {summary.total_findings}")
    print(f"  Critical:        {summary.critical}")
    print(f"  High:            {summary.high}")
    print(f"  Medium:          {summary.medium}")
    print(f"  Low:             {summary.low}")
    print(f"  Info:            {summary.info}")
    print(f"{'='*55}")
    print(f"  DEPLOYMENT RECOMMENDATION: {summary.deployment_status.value}")
    print(f"{'='*55}\n")

    if assessments:
        print("Top Risks:")
        seen = set()
        for a in assessments:
            if a.risk_type not in seen:
                seen.add(a.risk_type)
                print(f"  • {a.risk_type} — {a.impact}")
        print()

    for f in findings:
        sev = f.severity.name if hasattr(f.severity, 'name') else f.severity
        print(f"[{sev}] {f.title}")
        print(f"  File: {f.file_path}:{f.line_number}")
        print(f"  Snippet: {f.code_snippet}")
        print("-" * 50)

if __name__ == "__main__":
    main()
