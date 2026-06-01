from pydantic import BaseModel, Field


class ScanPlan(BaseModel):
    """Single source of truth for what scanners may inspect."""
    repository_path: str
    scan_directories: list[str] = Field(default_factory=list)
    skip_directories: list[str] = Field(default_factory=list)
    scan_files: list[str] = Field(default_factory=list)
    directory_priorities: dict[str, int] = Field(default_factory=dict)
    skip_reasons: dict[str, str] = Field(default_factory=dict)


class RepositoryScanSummary(BaseModel):
    """Human-readable scan planning summary for CLI and reports."""
    directories_found: int
    scannable_directories: list[str] = Field(default_factory=list)
    ignored_directories: list[str] = Field(default_factory=list)
    reason: str = "System, generated, and ignored directories are excluded from analysis."
    scan_plan: ScanPlan | None = None
