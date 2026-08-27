from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    environment: str = "development"
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    agent_model: str = "gemini-3.5-flash"
    log_level: str = "INFO"

    model_config = {"env_prefix": "AGENT_", "env_file": ".env"}
