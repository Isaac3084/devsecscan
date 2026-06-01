import uuid
from pydantic import BaseModel, Field
from ..findings.severity import Severity
from ..findings.categories import Category

class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: Category | str
    severity: Severity | str
    confidence: float = 0.0
    file_path: str | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str | None = None
    detector_name: str | None = None
    metadata: dict = Field(default_factory=dict)
