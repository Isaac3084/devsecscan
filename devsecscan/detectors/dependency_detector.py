import json
import re
from pathlib import Path
import configparser

class DependencyDetector:
    def detect(self, path: Path) -> tuple[list[str], list[str]]:
        """
        Detects dependencies and the files they were found in.
        Returns a tuple of (dependency_files, dependencies).
        """
        dependency_files = []
        dependencies = set()
        
        if not path.exists() or not path.is_dir():
            return [], []

        # 1. Parse package.json
        pkg_json_path = path / "package.json"
        if pkg_json_path.exists():
            dependency_files.append("package.json")
            try:
                with open(pkg_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    dependencies.update(deps.keys())
                    dependencies.update(dev_deps.keys())
            except (json.JSONDecodeError, OSError):
                pass # Graceful failure

        # 2. Parse pyproject.toml
        pyproject_path = path / "pyproject.toml"
        if pyproject_path.exists():
            dependency_files.append("pyproject.toml")
            try:
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # We do a basic regex parsing for pyproject.toml to avoid adding heavier TOML dependencies like `tomli`
                # unless they are already in the project (pyyaml is, tomli is not).
                # Looking for dependencies = [...] or [tool.poetry.dependencies]
                
                # Simple extraction for tool.poetry.dependencies or standard project.dependencies
                # For project.dependencies = ["fastapi", ...]
                project_deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if project_deps_match:
                    deps_str = project_deps_match.group(1)
                    # Extract string literals
                    deps = re.findall(r'[\'"]([^\'"]+)[\'"]', deps_str)
                    # Clean versions (e.g. "fastapi>=0.68.0" -> "fastapi")
                    for d in deps:
                        clean_name = re.split(r'[=<>~!]', d)[0].strip()
                        if clean_name:
                            dependencies.add(clean_name)
                
                # For poetry:
                poetry_deps_section = False
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith('[tool.poetry.dependencies]'):
                        poetry_deps_section = True
                        continue
                    elif line.startswith('['):
                        poetry_deps_section = False
                        
                    if poetry_deps_section and '=' in line and not line.startswith('#'):
                        key = line.split('=')[0].strip()
                        if key.lower() != 'python':
                            dependencies.add(key.strip('"\''))
            except OSError:
                pass # Graceful failure

        # 3. Parse requirements.txt
        req_path = path / "requirements.txt"
        if req_path.exists():
            dependency_files.append("requirements.txt")
            try:
                with open(req_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Strip versions and markers
                            clean_name = re.split(r'[=<>~!;]', line)[0].strip()
                            if clean_name:
                                dependencies.add(clean_name)
            except OSError:
                pass

        return dependency_files, sorted(list(dependencies))
