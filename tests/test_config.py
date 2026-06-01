import pytest
import os
from devsecscan.config import load_config

def test_load_config_default_no_file():
    # When file doesn't exist, it should return default
    config = load_config("nonexistent.yml")
    assert config.analysis_mode == "efficient"
    assert config.provider.name == "claude"

def test_load_config_with_file(tmp_path):
    config_file = tmp_path / "test.yml"
    config_file.write_text("analysis_mode: full\nprovider:\n  name: openai\nlocal_scanning: false")
    
    config = load_config(str(config_file))
    assert config.analysis_mode == "full"
    assert config.provider.name == "openai"
    assert config.local_scanning is False
