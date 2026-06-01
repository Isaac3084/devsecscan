import argparse

from ..analyzers.repository_analyzer import RepositoryAnalyzer
from ..findings.finding_engine import FindingEngine
from ..risk_engine.deployment_gate import DeploymentGate
from ..risk_engine.risk_classifier import RiskClassifier
from ..risk_engine.summary_formatter import format_repository_risk_summary
from ..security_detectors.secret_detector import SecretDetector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devsecscan",
        description="Scan a repository for local security findings and deployment risk.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to scan. Defaults to the current directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    analyzer = RepositoryAnalyzer()
    context = analyzer.analyze(args.path)

    finding_engine = FindingEngine()
    finding_engine.register(SecretDetector())
    findings = finding_engine.run(context)

    classifier = RiskClassifier()
    assessments = classifier.classify_all(findings)

    gate = DeploymentGate()
    summary = gate.evaluate(findings, assessments)

    print(format_repository_risk_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
