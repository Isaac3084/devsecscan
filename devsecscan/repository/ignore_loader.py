from fnmatch import fnmatch
from pathlib import Path


class IgnoreLoader:
    """Loads .devsecscanignore patterns for scan planning."""

    def load(self, repo_path: Path) -> list[str]:
        ignore_path = repo_path / ".devsecscanignore"
        if not ignore_path.exists():
            return []

        patterns: list[str] = []
        try:
            with open(ignore_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    pattern = line.strip()
                    if pattern and not pattern.startswith("#"):
                        patterns.append(pattern.replace("\\", "/"))
        except OSError:
            return []

        return patterns

    def matches(self, path: str, patterns: list[str]) -> bool:
        normalized = path.replace("\\", "/").strip("/")
        name = normalized.rsplit("/", 1)[-1]

        for pattern in patterns:
            normalized_pattern = pattern.strip().replace("\\", "/")
            if not normalized_pattern:
                continue

            if normalized_pattern.endswith("/"):
                normalized_pattern = normalized_pattern.rstrip("/")
                if normalized == normalized_pattern or normalized.startswith(f"{normalized_pattern}/"):
                    return True

            if fnmatch(normalized, normalized_pattern) or fnmatch(name, normalized_pattern):
                return True

        return False
