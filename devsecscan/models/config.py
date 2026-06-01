from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    name: str = "claude"
    api_key: str | None = None
    model_name: str | None = None

class UserConfig(BaseModel):
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    analysis_mode: str = "efficient"
    local_scanning: bool = True
    cloud_features: bool = False
