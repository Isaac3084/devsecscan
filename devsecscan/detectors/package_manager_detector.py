from pathlib import Path

class PackageManagerDetector:
    # Maps lockfiles/indicators to their respective package managers
    INDICATORS = {
        "uv.lock": "uv",
        "poetry.lock": "poetry",
        "Pipfile.lock": "pipenv",
        "package-lock.json": "npm",
        "yarn.lock": "yarn",
        "pnpm-lock.yaml": "pnpm"
    }

    def detect(self, path: Path) -> str | None:
        """
        Detects the package manager used in the repository based on lockfiles.
        """
        if not path.exists() or not path.is_dir():
            return None

        # Check for strong lockfile indicators first
        for lockfile, manager in self.INDICATORS.items():
            if (path / lockfile).exists():
                return manager
                
        # If no specific lockfile, check for requirements.txt which usually means pip
        if (path / "requirements.txt").exists():
            return "pip"
            
        # If there's a package.json but no lockfile, it's typically npm by default
        if (path / "package.json").exists():
            return "npm"
            
        return None
