"""
Recommendation Engine: Generates human-readable remediation advice for findings.
"""

from ..findings.categories import Category


# Category-specific recommendation templates
_RECOMMENDATIONS: dict[str, str] = {
    Category.SECRET: (
        "Remove the hardcoded secret from source code immediately. "
        "Store it in environment variables, a .env file excluded from version control, "
        "or a dedicated secrets manager (e.g. AWS Secrets Manager, HashiCorp Vault). "
        "Rotate the exposed credential as soon as possible."
    ),
    Category.AUTHENTICATION: (
        "Review the authentication implementation. "
        "Ensure all endpoints require proper authentication, "
        "use secure session management, and enforce strong password policies."
    ),
    Category.AUTHORIZATION: (
        "Implement proper role-based access control (RBAC). "
        "Ensure sensitive routes check user permissions before granting access. "
        "Follow the principle of least privilege."
    ),
    Category.CONFIGURATION: (
        "Review application configuration for security best practices. "
        "Disable debug mode in production, set secure HTTP headers, "
        "and avoid exposing internal error details to end users."
    ),
    Category.DEPENDENCY: (
        "Audit and update vulnerable dependencies. "
        "Use a lockfile, pin dependency versions, and run automated vulnerability scans regularly."
    ),
    Category.INFRASTRUCTURE: (
        "Review cloud and infrastructure configuration. "
        "Ensure storage buckets are private, ports are restricted, "
        "and infrastructure-as-code follows security baselines."
    ),
    Category.API_SECURITY: (
        "Protect API endpoints with authentication and rate limiting. "
        "Validate all input, use HTTPS, and avoid exposing sensitive data in responses."
    ),
    Category.DEPLOYMENT: (
        "Review deployment configuration for hardcoded secrets, exposed ports, "
        "and insecure environment settings before shipping to production."
    ),
}

_DEFAULT_RECOMMENDATION = (
    "Review this finding carefully and consult your security team. "
    "Address the issue before deploying to production."
)


class RecommendationEngine:
    """Generates actionable, human-readable recommendations for findings."""

    def recommend(self, category: str) -> str:
        """
        Returns a recommendation string for the given finding category.
        Falls back to a generic recommendation for unknown categories.
        """
        return _RECOMMENDATIONS.get(category, _DEFAULT_RECOMMENDATION)
