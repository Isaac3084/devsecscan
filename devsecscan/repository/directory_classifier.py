from ..models.repository_structure import DirectoryType


KNOWN_DIRECTORIES: dict[str, DirectoryType] = {
    "src": DirectoryType.SOURCE_CODE,
    "app": DirectoryType.SOURCE_CODE,
    "api": DirectoryType.SOURCE_CODE,
    "lib": DirectoryType.SOURCE_CODE,
    "server": DirectoryType.SOURCE_CODE,
    "client": DirectoryType.SOURCE_CODE,
    "tests": DirectoryType.TEST_CODE,
    "test": DirectoryType.TEST_CODE,
    "spec": DirectoryType.TEST_CODE,
    "specs": DirectoryType.TEST_CODE,
    "node_modules": DirectoryType.DEPENDENCIES,
    "vendor": DirectoryType.DEPENDENCIES,
    "venv": DirectoryType.ENVIRONMENT,
    ".venv": DirectoryType.ENVIRONMENT,
    "env": DirectoryType.ENVIRONMENT,
    ".git": DirectoryType.METADATA,
    ".github": DirectoryType.CONFIGURATION,
    "__pycache__": DirectoryType.CACHE,
    ".pytest_cache": DirectoryType.CACHE,
    ".mypy_cache": DirectoryType.CACHE,
    "coverage": DirectoryType.CACHE,
    "build": DirectoryType.BUILD_OUTPUT,
    "dist": DirectoryType.BUILD_OUTPUT,
    "target": DirectoryType.BUILD_OUTPUT,
    ".next": DirectoryType.BUILD_OUTPUT,
    ".nuxt": DirectoryType.BUILD_OUTPUT,
    "docs": DirectoryType.DOCUMENTATION,
    "doc": DirectoryType.DOCUMENTATION,
    "config": DirectoryType.CONFIGURATION,
    "configs": DirectoryType.CONFIGURATION,
}

DIRECTORY_PRIORITIES: dict[DirectoryType, int] = {
    DirectoryType.SOURCE_CODE: 100,
    DirectoryType.CONFIGURATION: 90,
    DirectoryType.TEST_CODE: 40,
    DirectoryType.DOCUMENTATION: 10,
    DirectoryType.UNKNOWN: 20,
    DirectoryType.ENVIRONMENT: 0,
    DirectoryType.DEPENDENCIES: 0,
    DirectoryType.CACHE: 0,
    DirectoryType.BUILD_OUTPUT: 0,
    DirectoryType.METADATA: 0,
}


class DirectoryClassifier:
    """Classifies repository directories without inspecting their contents."""

    def __init__(self, registry: dict[str, DirectoryType] | None = None):
        self._registry = dict(KNOWN_DIRECTORIES)
        if registry:
            self._registry.update({name.lower(): dtype for name, dtype in registry.items()})

    def classify(self, directory_name: str) -> DirectoryType:
        return self._registry.get(directory_name.lower(), DirectoryType.UNKNOWN)

    def priority_for(self, directory_type: DirectoryType) -> int:
        return DIRECTORY_PRIORITIES.get(directory_type, 0)
