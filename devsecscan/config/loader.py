import yaml
import os
from ..models.config import UserConfig

def load_config(path: str = "devsecscan.yml") -> UserConfig:
    """Loads the user configuration from a YAML file."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                return UserConfig(**data)
    return UserConfig()
