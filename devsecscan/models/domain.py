from pydantic import BaseModel, Field

class Risk(BaseModel):
    name: str
    description: str

class Finding(BaseModel):
    issue: str
    potential_consequences: str
    likelihood: str
    severity: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    
class RepositoryContext(BaseModel):
    path: str
    framework: str | None = None
    language: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    file_count: int = 0
    structure_summary: str | None = None

class DeploymentRecommendation(BaseModel):
    risk: str
    likelihood: str
    impact: str
    recommendation_text: str
    safe_to_deploy: bool
