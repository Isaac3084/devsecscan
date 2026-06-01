from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="JSON Web Token (JWT)",
        description="Potential JWT token detected.",
        pattern=r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        severity=Severity.HIGH,
        confidence=0.85
    )
]
