from pydantic import BaseModel
from ..findings.severity import Severity

class SecretRule(BaseModel):
    name: str
    description: str
    pattern: str
    severity: Severity | str
    confidence: float
