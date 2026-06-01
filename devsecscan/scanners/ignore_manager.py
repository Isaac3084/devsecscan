"""
IgnoreManager: Reads .devsecscanignore and provides a fast lookup
to decide whether a given file path should be excluded from scanning.
"""

from pathlib import Path
from fnmatch import fnmatch


# Directories that are ALWAYS ignored regardless of .devsecscanignore
DEFAULT_IGNORES = [
    "tests/",
    "test/",
    "node_modules/",
    ".git/",
    "coverage/",
    "dist/",
    "build/",
    "__pycache__/",
    ".venv/",
    "venv/",
    ".pytest_cache/",
    ".mypy_cache/",
    "target/",
]


class IgnoreManager:
    """
    Manages ignore rules from a .devsecscanignore file plus
    built-in defaults.
    """

    def __init__(self, repo_path: Path):
        self._patterns: list[str] = list(DEFAULT_IGNORES)
        self._load_ignore_file(repo_path / ".devsecscanignore")

    def _load_ignore_file(self, ignore_path: Path):
        """Load patterns from .devsecscanignore if it exists."""
        if not ignore_path.exists():
            return
        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self._patterns.append(line)
        except OSError:
            pass  # Gracefully skip unreadable files

    def should_ignore(self, file_path: Path, repo_root: Path) -> bool:
        """
        Returns True if the file should be excluded from scanning.
        Checks against both default ignores and user-defined patterns.
        """
        try:
            rel = file_path.relative_to(repo_root)
        except ValueError:
            return False

        rel_str = str(rel).replace("\\", "/")
        parts = rel.parts

        for pattern in self._patterns:
            # Directory pattern (ends with /)
            if pattern.endswith("/"):
                dirname = pattern.rstrip("/")
                if dirname in parts:
                    return True
            else:
                # Glob-style file pattern
                if fnmatch(rel_str, pattern) or fnmatch(rel.name, pattern):
                    return True

        return False
