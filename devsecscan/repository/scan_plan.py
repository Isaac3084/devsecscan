from ..models.scan_plan import RepositoryScanSummary


def format_repository_scan_summary(summary: RepositoryScanSummary) -> str:
    """Render a repository scan planning summary."""
    lines = [
        "Repository Scan Summary",
        "",
        f"Directories Found: {summary.directories_found}",
        "",
        "Scannable Directories:",
    ]

    if summary.scannable_directories:
        lines.extend(f"* {directory}" for directory in summary.scannable_directories)
    else:
        lines.append("* None")

    lines.extend(["", "Ignored Directories:"])
    if summary.ignored_directories:
        lines.extend(f"* {directory}" for directory in summary.ignored_directories)
    else:
        lines.append("* None")

    lines.extend(["", "Reason:", summary.reason])
    return "\n".join(lines)
