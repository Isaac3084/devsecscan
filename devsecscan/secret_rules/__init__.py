from ..models.secret_rule import SecretRule
from . import openai, github, aws, stripe, jwt, generic

class RuleRegistry:
    def __init__(self):
        self._rules: list[SecretRule] = []
        self._register_defaults()
        
    def _register_defaults(self):
        """Registers all built-in rules."""
        for module in [openai, github, aws, stripe, jwt, generic]:
            if hasattr(module, "RULES"):
                for rule in module.RULES:
                    self.register(rule)

    def register(self, rule: SecretRule):
        self._rules.append(rule)

    def get_all(self) -> list[SecretRule]:
        return self._rules
