from pydantic import BaseModel, Field

class Risk(BaseModel):
    name: str
    description: str


class RepositoryAnalysisError(Exception):
    """Raised when repository analysis fails (e.g. path does not exist)."""
    pass

class RepositoryContext(BaseModel):
    project_name: str | None = None
    project_path: str
    primary_language: str | None = None
    detected_languages: dict[str, float] = Field(default_factory=dict)
    framework: str | None = None
    package_manager: str | None = None
    dependency_files: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    total_files: int = 0
    source_directories: list[str] = Field(default_factory=list)

class DeploymentRecommendation(BaseModel):
    risk: str
    likelihood: str
    impact: str
    recommendation_text: str
    safe_to_deploy: bool
