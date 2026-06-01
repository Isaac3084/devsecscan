"""
Risk Registry: Maps (Category, Severity) pairs to risk metadata.

Adding a new risk type only requires adding a new entry to RISK_MAP.
No other module needs to change — Open/Closed Principle.
"""

from ..findings.severity import Severity
from ..findings.categories import Category
from ..models.risk_assessment import DeploymentStatus


class RiskMapping:
    """A single risk mapping entry."""
    def __init__(
        self,
        risk_type: str,
        likelihood: str,
        impact: str,
        business_consequence: str,
        deployment_status: DeploymentStatus,
    ):
        self.risk_type = risk_type
        self.likelihood = likelihood
        self.impact = impact
        self.business_consequence = business_consequence
        self.deployment_status = deployment_status


# ---------- Central Risk Map ----------
# Key: (Category value, Severity value)
# Value: RiskMapping
RISK_MAP: dict[tuple[str, int], RiskMapping] = {
    # ---- SECRET ----
    (Category.SECRET, Severity.CRITICAL): RiskMapping(
        risk_type="Credential Exposure",
        likelihood="HIGH",
        impact="Full account takeover or unauthorized API usage",
        business_consequence="Third parties can use paid APIs, leading to unexpected billing charges and data breaches.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    (Category.SECRET, Severity.HIGH): RiskMapping(
        risk_type="Credential Exposure",
        likelihood="HIGH",
        impact="Unauthorized access to cloud resources",
        business_consequence="Attackers can access cloud infrastructure, steal data, or rack up compute costs.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    (Category.SECRET, Severity.MEDIUM): RiskMapping(
        risk_type="Service Abuse",
        likelihood="MEDIUM",
        impact="Potential misuse of exposed credentials",
        business_consequence="Exposed tokens or passwords may allow limited unauthorized access.",
        deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
    ),
    (Category.SECRET, Severity.LOW): RiskMapping(
        risk_type="Data Exposure",
        likelihood="LOW",
        impact="Low-sensitivity information leak",
        business_consequence="Minor information disclosure that may aid future attacks.",
        deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
    ),
    # ---- AUTHENTICATION ----
    (Category.AUTHENTICATION, Severity.CRITICAL): RiskMapping(
        risk_type="Account Takeover",
        likelihood="HIGH",
        impact="Authentication bypass",
        business_consequence="Users can access accounts without credentials.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    (Category.AUTHENTICATION, Severity.HIGH): RiskMapping(
        risk_type="Account Takeover",
        likelihood="HIGH",
        impact="Weak authentication controls",
        business_consequence="Brute-force or session hijacking attacks become feasible.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    # ---- AUTHORIZATION ----
    (Category.AUTHORIZATION, Severity.CRITICAL): RiskMapping(
        risk_type="Privilege Escalation",
        likelihood="HIGH",
        impact="Unauthorized access to admin functionality",
        business_consequence="Any user can access administrative operations, leading to data manipulation or deletion.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    (Category.AUTHORIZATION, Severity.HIGH): RiskMapping(
        risk_type="Unauthorized Access",
        likelihood="MEDIUM",
        impact="Inadequate role-based access control",
        business_consequence="Users may access resources beyond their intended privileges.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    # ---- CONFIGURATION ----
    (Category.CONFIGURATION, Severity.HIGH): RiskMapping(
        risk_type="Configuration Risk",
        likelihood="MEDIUM",
        impact="Insecure application configuration",
        business_consequence="Debug modes, verbose errors, or insecure defaults may expose internal details.",
        deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
    ),
    # ---- DEPENDENCY ----
    (Category.DEPENDENCY, Severity.HIGH): RiskMapping(
        risk_type="Dependency Risk",
        likelihood="MEDIUM",
        impact="Known vulnerabilities in dependencies",
        business_consequence="Attackers can exploit known CVEs in third-party packages.",
        deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
    ),
    # ---- INFRASTRUCTURE ----
    (Category.INFRASTRUCTURE, Severity.CRITICAL): RiskMapping(
        risk_type="Infrastructure Misconfiguration",
        likelihood="HIGH",
        impact="Open ports, public buckets, or insecure cloud config",
        business_consequence="Direct access to infrastructure leading to data breaches or compute hijacking.",
        deployment_status=DeploymentStatus.DO_NOT_DEPLOY,
    ),
    # ---- API_SECURITY ----
    (Category.API_SECURITY, Severity.HIGH): RiskMapping(
        risk_type="Unauthorized Access",
        likelihood="MEDIUM",
        impact="Unprotected API endpoints",
        business_consequence="Sensitive data or operations exposed without authentication.",
        deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
    ),
}

# Default mapping for unknown (Category, Severity) combinations
DEFAULT_RISK = RiskMapping(
    risk_type="Unknown Risk",
    likelihood="UNKNOWN",
    impact="Unclassified security concern",
    business_consequence="This issue has not been classified. Manual review is recommended.",
    deployment_status=DeploymentStatus.PROCEED_WITH_CAUTION,
)


class RiskRegistry:
    """Looks up risk metadata for a given (Category, Severity) pair."""

    def __init__(self):
        self._map = dict(RISK_MAP)

    def lookup(self, category: str, severity) -> RiskMapping:
        """
        Returns the RiskMapping for the given category and severity.
        Falls back to DEFAULT_RISK if no match is found.
        """
        # Normalise severity to enum
        if isinstance(severity, str):
            try:
                severity = Severity[severity.upper()]
            except KeyError:
                return DEFAULT_RISK

        # Normalise category to enum
        if isinstance(category, str):
            try:
                category = Category(category.upper())
            except ValueError:
                return DEFAULT_RISK

        return self._map.get((category, severity), DEFAULT_RISK)
