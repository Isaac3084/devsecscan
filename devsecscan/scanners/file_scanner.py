import os
from pathlib import Path
from typing import Iterator, Tuple

from .ignore_manager import IgnoreManager


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

    def scan(self, repo_path: Path) -> Iterator[Tuple[Path, int, str]]:
        """
        Yields (file_path, line_number, line_content) for all valid files in the repository.
        Respects .devsecscanignore and default ignore rules.
        """
        if not repo_path.exists() or not repo_path.is_dir():
            return

        ignore_mgr = IgnoreManager(repo_path)

        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Ignore standard non-source directories (fast path)
            if any(ignored in file_path.parts for ignored in (".git", "node_modules", "venv", "__pycache__", ".venv", "target", "build", "dist")):
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
