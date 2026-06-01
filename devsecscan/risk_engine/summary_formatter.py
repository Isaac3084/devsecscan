from collections import Counter

from ..models.risk_assessment import RepositoryRiskSummary


def get_top_risks(
    summary: RepositoryRiskSummary,
    limit: int = 5,
) -> list[str]:
    """Return the most common risk types in a stable display order."""
    if limit <= 0:
        return []

    counts = Counter(a.risk_type for a in summary.assessments)
    return [
        risk_type
        for risk_type, _ in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]
    ]


def format_repository_risk_summary(
    summary: RepositoryRiskSummary,
    top_risks_limit: int = 5,
) -> str:
    """Format a RepositoryRiskSummary for terminal preview output."""
    lines = [
        "Repository Risk Summary",
        "",
        f"Total Findings: {summary.total_findings}",
        f"Critical Issues: {summary.critical}",
        f"High Issues: {summary.high}",
        f"Medium Issues: {summary.medium}",
        f"Low Issues: {summary.low}",
        f"Info Issues: {summary.info}",
        "",
        "Deployment Recommendation:",
        summary.deployment_status.value,
        "",
        "Top Risks:",
    ]

    top_risks = get_top_risks(summary, top_risks_limit)
    if not top_risks:
        lines.append("None")
    else:
        for index, risk_type in enumerate(top_risks, start=1):
            lines.append(f"{index}. {risk_type}")

    return "\n".join(lines)
