from ..models.secret_rule import SecretRule
from ..findings.severity import Severity

RULES = [
    SecretRule(
        name="GitHub Personal Access Token",
        description="Potential GitHub personal access token detected.",
        pattern=r"ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",
        severity=Severity.CRITICAL,
        confidence=0.95
    )
]
