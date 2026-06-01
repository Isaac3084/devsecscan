from pathlib import Path

from ..models.repository_structure import DirectoryType, RepositoryStructure
from ..models.scan_plan import RepositoryScanSummary, ScanPlan
from .directory_classifier import DirectoryClassifier
from .ignore_loader import IgnoreLoader
from .repository_mapper import RepositoryMapper


SCANNABLE_DIRECTORY_TYPES = {
    DirectoryType.SOURCE_CODE,
    DirectoryType.CONFIGURATION,
    DirectoryType.UNKNOWN,
}

SKIPPED_TYPE_REASONS = {
    DirectoryType.TEST_CODE: "test fixtures are excluded from security scans",
    DirectoryType.DEPENDENCIES: "dependency directories are excluded from analysis",
    DirectoryType.ENVIRONMENT: "virtual environments are excluded from analysis",
    DirectoryType.BUILD_OUTPUT: "generated build output is excluded from analysis",
    DirectoryType.CACHE: "cache directories are excluded from analysis",
    DirectoryType.DOCUMENTATION: "documentation is low priority for security scans",
    DirectoryType.METADATA: "repository metadata is excluded from analysis",
}


class ScanPlanner:
    """Converts repository structure into a deterministic scan plan."""

    def __init__(
        self,
        mapper: RepositoryMapper | None = None,
        classifier: DirectoryClassifier | None = None,
        ignore_loader: IgnoreLoader | None = None,
    ):
        self._classifier = classifier or DirectoryClassifier()
        self._mapper = mapper or RepositoryMapper(self._classifier)
        self._ignore_loader = ignore_loader or IgnoreLoader()

    def plan(self, path: str | Path) -> ScanPlan:
        structure = self._mapper.map(path)
        return self.from_structure(structure)

    def from_structure(self, structure: RepositoryStructure) -> ScanPlan:
        repo_path = Path(structure.project_path)
        ignore_patterns = self._ignore_loader.load(repo_path)

        scan_directories: list[str] = []
        skip_directories: list[str] = []
        directory_priorities: dict[str, int] = {}
        skip_reasons: dict[str, str] = {}

        for directory in structure.directories:
            directory_type = structure.directory_types.get(
                directory,
                self._classifier.classify(directory),
            )
            priority = self._classifier.priority_for(directory_type)
            directory_priorities[directory] = priority

            if self._ignore_loader.matches(directory, ignore_patterns):
                skip_directories.append(directory)
                skip_reasons[directory] = "matched .devsecscanignore"
            elif directory_type in SCANNABLE_DIRECTORY_TYPES:
                scan_directories.append(directory)
            else:
                skip_directories.append(directory)
                skip_reasons[directory] = SKIPPED_TYPE_REASONS.get(
                    directory_type,
                    "directory is excluded from analysis",
                )

        scan_directories.sort(key=lambda d: (-directory_priorities.get(d, 0), d))
        skip_directories.sort()

        scan_files = [
            filename
            for filename in structure.files
            if not self._ignore_loader.matches(filename, ignore_patterns)
        ]

        return ScanPlan(
            repository_path=structure.project_path,
            scan_directories=scan_directories,
            skip_directories=skip_directories,
            scan_files=scan_files,
            directory_priorities=directory_priorities,
            skip_reasons=skip_reasons,
        )

    def summarize(self, plan: ScanPlan) -> RepositoryScanSummary:
        return RepositoryScanSummary(
            directories_found=len(plan.scan_directories) + len(plan.skip_directories),
            scannable_directories=plan.scan_directories,
            ignored_directories=plan.skip_directories,
            scan_plan=plan,
        )
