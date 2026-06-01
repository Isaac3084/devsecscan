from pydantic import BaseModel, Field
from .domain import RepositoryContext, DeploymentRecommendation
from .finding import Finding

class AnalysisRequest(BaseModel):
    context: RepositoryContext
    local_findings: list[Finding] = Field(default_factory=list)
    mode: str = "efficient"
    
class AnalysisResult(BaseModel):
    recommendation: DeploymentRecommendation
    additional_findings: list[Finding] = Field(default_factory=list)
    raw_provider_response: str | None = None
