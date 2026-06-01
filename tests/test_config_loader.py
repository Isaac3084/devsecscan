"""
1. Purpose of file:
This file contains the test suite for the Configuration Loader module.
It ensures that YAML user configuration files are safely and correctly loaded into Pydantic models.

2. Test strategy:
We utilize pytest and `tmp_path` to simulate various configuration file states on disk:
- Valid Configuration: Ensures standard configuration applies correctly.
- Missing Fields: Verifies that omitted YAML fields result in the correct safe defaults.
- Invalid Provider: Ensures strict Pydantic validation catches unsupported AI providers.
- Malformed YAML: Tests that syntax errors in YAML are caught and raised as graceful ConfigErrors.
- Missing File: Verifies that running without a configuration file defaults to a safe, working state.

4. Explanation of each test is provided as a docstring within the test functions.
"""

import pytest
from pydantic import ValidationError
from devsecscan.config.loader import load_config, ConfigError

def test_valid_configuration(tmp_path):
    """
    Why: Validates the happy path where a user supplies a completely correct config file.
    Assumption: The loader reads the YAML and correctly maps nested provider dicts to ProviderConfig.
    Bug prevented: Prevents issues where users cannot override defaults via the YAML file.
    """
    config_file = tmp_path / "valid.yml"
    config_file.write_text("provider:\n  name: openai\nanalysis_mode: efficient\n")
    
    config = load_config(str(config_file))
    assert config.provider.name == "openai"
    assert config.analysis_mode == "efficient"

def test_missing_fields_configuration(tmp_path):
    """
    Why: Tests that incomplete configurations gracefully fallback to defaults.
    Assumption: A user might only specify the provider, leaving `analysis_mode` empty.
    Bug prevented: Prevents NoneType errors in the engine if fields are missing from the config.
    """
    config_file = tmp_path / "missing.yml"
    config_file.write_text("provider:\n  name: gemini\n")
    
    config = load_config(str(config_file))
    assert config.provider.name == "gemini"
    # analysis_mode falls back to default
    assert config.analysis_mode == "efficient"

def test_invalid_provider_configuration(tmp_path):
    """
    Why: Validates that invalid providers are immediately caught before the scan starts.
    Assumption: Pydantic's ValidationError will bubble up when parsing the config file.
    Bug prevented: Prevents the auditor from running for minutes only to fail when calling the AI API.
    """
    config_file = tmp_path / "invalid_provider.yml"
    config_file.write_text("provider:\n  name: banana\n")
    
    with pytest.raises(ValidationError) as exc_info:
        load_config(str(config_file))
    assert "Input should be" in str(exc_info.value)

def test_malformed_yaml_configuration(tmp_path):
    """
    Why: Ensures syntax errors in the user's YAML file do not cause confusing stack traces.
    Assumption: yaml.safe_load raises YAMLError which we wrap in a graceful ConfigError.
    Bug prevented: Avoids poor user experience where users get unhandled internal exceptions for simple typos.
    """
    config_file = tmp_path / "broken.yml"
    config_file.write_text("provider:\n  name: claude\n broke\n  - syntax")
    
    with pytest.raises(ConfigError) as exc_info:
        load_config(str(config_file))
    assert "Malformed YAML" in str(exc_info.value)

def test_missing_file_configuration():
    """
    Why: Validates that the platform can function fully offline without any configuration file.
    Assumption: `os.path.exists` handles the missing file and returns a default UserConfig instance.
    Bug prevented: Prevents fatal crashes for new users running `devsecscan audit` out of the box.
    """
    config = load_config("nonexistent_path_that_definitely_does_not_exist.yml")
    assert config.analysis_mode == "efficient"
    assert config.provider.name == "claude"
