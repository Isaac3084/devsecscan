from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="AWS Access Key ID",
        description="Potential AWS Access Key ID detected.",
        pattern=r"(?<![A-Z0-9])AKIA[A-Z0-9]{16}(?![A-Z0-9])",
        severity=Severity.HIGH,
        confidence=0.90
    )
]
