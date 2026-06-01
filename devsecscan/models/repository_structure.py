from enum import Enum

from pydantic import BaseModel, Field


class DirectoryType(str, Enum):
    SOURCE_CODE = "SOURCE_CODE"
    TEST_CODE = "TEST_CODE"
    DEPENDENCIES = "DEPENDENCIES"
    ENVIRONMENT = "ENVIRONMENT"
    BUILD_OUTPUT = "BUILD_OUTPUT"
    CACHE = "CACHE"
    DOCUMENTATION = "DOCUMENTATION"
    CONFIGURATION = "CONFIGURATION"
    METADATA = "METADATA"
    UNKNOWN = "UNKNOWN"


class RepositoryStructure(BaseModel):
    """Fast top-level map of a repository before security scanning begins."""
    project_path: str
    directories: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    directory_types: dict[str, DirectoryType] = Field(default_factory=dict)
