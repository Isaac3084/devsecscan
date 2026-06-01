from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="Stripe Secret Key",
        description="Potential Stripe secret key detected.",
        pattern=r"sk_(live|test)_[0-9a-zA-Z]{24}",
        severity=Severity.CRITICAL,
        confidence=0.99
    )
]
