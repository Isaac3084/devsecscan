from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="Generic Secret",
        description="Generic secret, password, or key detected.",
        # Looks for var assignments like password = "..." or API_KEY : "..."
        pattern=r"(?i)(password|secret|token|api_key|access_key|private_key|client_secret|jwt_secret)\s*[:=]\s*['\"]([^'\"]+)['\"]",
        severity=Severity.MEDIUM,
        confidence=0.50
    )
]
