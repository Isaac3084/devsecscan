import re
from pathlib import Path
from ..detectors.base_detector import BaseDetector
from ..models.domain import RepositoryContext
from ..models.finding import Finding
from ..findings.categories import Category
from ..scanners.file_scanner import FileScanner
from ..secret_rules import RuleRegistry
from ..models.secret_rule import SecretRule

class SecretDetector(BaseDetector):
    def __init__(self):
        self.registry = RuleRegistry()
        self.scanner = FileScanner()

    def _mask_secret(self, secret: str) -> str:
        """
        Masks the secret for safe reporting.
        e.g. sk-1234567890abcdefghijk -> sk-1234************hijk
        """
        length = len(secret)
        if length <= 8:
            return "***" # Too short to safely show parts
        
        # Keep first 7 characters, and last 4 characters, mask the middle
        visible_start = min(7, length // 3)
        visible_end = min(4, length // 3)
        
        start = secret[:visible_start]
        end = secret[-visible_end:]
        mask = "*" * (length - visible_start - visible_end)
        
        return f"{start}{mask}{end}"

    def _adjust_confidence(self, rule: SecretRule, line_content: str) -> float:
        """
        Adjusts the base confidence of a rule based on contextual keywords.
        """
        confidence = rule.confidence
        lower_line = line_content.lower()
        
        # Increase confidence if it looks like an assignment or key
        if any(keyword in lower_line for keyword in ["api_key", "secret", "token", "password", "key="]):
            confidence = min(1.0, confidence + 0.1)
            
        # Decrease confidence if it looks like a test or example
        if any(keyword in lower_line for keyword in ["test", "example", "dummy", "placeholder", "foo", "bar"]):
            confidence = max(0.0, confidence - 0.3)
            
        return round(confidence, 2)

    def detect(self, context: RepositoryContext) -> list[Finding]:
        """
        Scans the repository for secrets using registered rules.
        """
        findings = []
        rules = self.registry.get_all()
        repo_path = Path(context.project_path)

        for file_path, line_number, line_content in self.scanner.scan(repo_path):
            for rule in rules:
                # Compile regex on the fly, or could optimize by pre-compiling
                try:
                    matches = re.finditer(rule.pattern, line_content)
                    for match in matches:
                        # Extract the actual secret. If it's a generic rule, group(2) might hold the secret
                        if rule.name == "Generic Secret" and len(match.groups()) >= 2:
                            raw_secret = match.group(2)
                        else:
                            raw_secret = match.group(0)
                            
                        masked = self._mask_secret(raw_secret)
                        confidence = self._adjust_confidence(rule, line_content)
                        
                        # Only report if confidence is above a threshold
                        if confidence > 0.3:
                            finding = Finding(
                                title=f"Hardcoded {rule.name}",
                                description=f"Potential {rule.name} detected.",
                                category=Category.SECRET,
                                severity=rule.severity,
                                confidence=confidence,
                                file_path=str(file_path.relative_to(repo_path)),
                                line_number=line_number,
                                code_snippet=f"{match.group(0).replace(raw_secret, masked)}",
                                recommendation="Move this secret to a secure environment variable or secrets manager.",
                                detector_name="SecretDetector"
                            )
                            findings.append(finding)
                except re.error:
                    continue # Skip broken regex rules gracefully

        return findings
