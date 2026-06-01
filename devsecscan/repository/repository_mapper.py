from pathlib import Path

from ..models.repository_structure import RepositoryStructure
from .directory_classifier import DirectoryClassifier


class RepositoryMappingError(Exception):
    """Raised when repository mapping cannot start."""


class RepositoryMapper:
    """Builds a fast, shallow repository map."""

    def __init__(self, classifier: DirectoryClassifier | None = None):
        self._classifier = classifier or DirectoryClassifier()

    def map(self, path: str | Path) -> RepositoryStructure:
        repo_path = Path(path)
        if not repo_path.exists() or not repo_path.is_dir():
            raise RepositoryMappingError(f"Repository path does not exist or is not a directory: {path}")

        directories: list[str] = []
        files: list[str] = []
        directory_types = {}

        try:
            entries = repo_path.iterdir()
            for entry in entries:
                try:
                    if entry.is_symlink() and not entry.exists():
                        continue
                    if entry.is_dir():
                        directories.append(entry.name)
                        directory_types[entry.name] = self._classifier.classify(entry.name)
                    elif entry.is_file():
                        files.append(entry.name)
                except OSError:
                    continue
        except OSError:
            return RepositoryStructure(project_path=str(repo_path.absolute()))

        directories.sort()
        files.sort()
        return RepositoryStructure(
            project_path=str(repo_path.absolute()),
            directories=directories,
            files=files,
            directory_types=directory_types,
        )
