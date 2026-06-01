import yaml
import os
from pydantic import ValidationError
from ..models.config import UserConfig

class ConfigError(Exception):
    """Raised when there is an issue parsing the configuration file."""
    pass

def load_config(path: str = "devsecscan.yml") -> UserConfig:
    """Loads the user configuration from a YAML file."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    return UserConfig(**data)
        except yaml.YAMLError as e:
            raise ConfigError(f"Malformed YAML in config file: {e}")
        except ValidationError as e:
            # Let ValidationError bubble up or handle it, the prompt expects 'Validation error'
            raise
    return UserConfig()
