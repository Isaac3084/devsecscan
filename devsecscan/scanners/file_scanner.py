import os
from pathlib import Path
from typing import Iterator, Tuple

from .ignore_manager import IgnoreManager
from ..models.scan_plan import ScanPlan
from ..repository.scan_planner import ScanPlanner


class FileScanner:
    DEFAULT_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".env", ".json",
        ".yaml", ".yml", ".toml", ".txt", ".ini", ".conf", ".pem", ".key"
    }

    def __init__(self, allowed_extensions: set[str] = None, max_file_size_bytes: int = 1_000_000):
        """
        Initializes the FileScanner.
        :param allowed_extensions: Set of file extensions to scan. Defaults to a standard text-based list.
        :param max_file_size_bytes: Maximum file size to scan (default 1MB) to prevent memory exhaustion.
        """
        self.allowed_extensions = allowed_extensions if allowed_extensions is not None else self.DEFAULT_EXTENSIONS
        self.max_file_size_bytes = max_file_size_bytes

    def is_binary(self, filepath: Path) -> bool:
        """Heuristic check to see if a file is binary by looking for null bytes in a chunk."""
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True
        except OSError:
            pass
        return False

    def _iter_plan_files(self, repo_path: Path, scan_plan: ScanPlan) -> Iterator[Path]:
        for filename in scan_plan.scan_files:
            file_path = repo_path / filename
            if file_path.is_file():
                yield file_path

        for directory in scan_plan.scan_directories:
            directory_path = repo_path / directory
            if not directory_path.exists() or not directory_path.is_dir():
                continue

            try:
                for file_path in directory_path.rglob("*"):
                    if file_path.is_file():
                        yield file_path
            except OSError:
                continue

    def scan(self, repo_path: Path, scan_plan: ScanPlan | None = None) -> Iterator[Tuple[Path, int, str]]:
        """
        Yields (file_path, line_number, line_content) for all valid files in the repository.
        Respects the scan plan, .devsecscanignore, and default ignore rules.
        """
        if not repo_path.exists() or not repo_path.is_dir():
            return

        if scan_plan is None:
            scan_plan = ScanPlanner().plan(repo_path)

        ignore_mgr = IgnoreManager(repo_path)
        skipped_directories = set(scan_plan.skip_directories)

        for file_path in self._iter_plan_files(repo_path, scan_plan):
            try:
                rel_parts = file_path.relative_to(repo_path).parts
            except ValueError:
                continue

            if any(part in skipped_directories for part in rel_parts):
                continue

            # Check .devsecscanignore and default ignore rules
            if ignore_mgr.should_ignore(file_path, repo_path):
                continue

            # Check extension
            if file_path.suffix.lower() not in self.allowed_extensions and file_path.name != ".env":
                continue

            # Check file size
            try:
                if file_path.stat().st_size > self.max_file_size_bytes:
                    continue
            except OSError:
                continue

            # Check binary
            if self.is_binary(file_path):
                continue

            # Safely yield lines
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    for line_number, line_content in enumerate(f, start=1):
                        yield file_path, line_number, line_content
            except OSError:
                pass  # Gracefully skip unreadable files
