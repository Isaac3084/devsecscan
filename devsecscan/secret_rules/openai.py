from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="OpenAI API Key",
        description="Potential OpenAI API key detected.",
        pattern=r"sk-[A-Za-z0-9]{20,}",
        severity=Severity.CRITICAL,
        confidence=0.98
    )
]
