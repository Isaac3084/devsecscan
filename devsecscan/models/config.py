from pydantic import BaseModel, Field

from typing import Literal

class ProviderConfig(BaseModel):
    name: Literal["openai", "claude", "gemini", "deepseek", "qwen", "nvidia_nim", "ollama", "ollama_cloud"] = "claude"
    api_key: str | None = None
    model_name: str | None = None

class UserConfig(BaseModel):
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    analysis_mode: str = "efficient"
    local_scanning: bool = True
    cloud_features: bool = False
