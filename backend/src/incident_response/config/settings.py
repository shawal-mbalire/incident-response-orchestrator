from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    environment: str = "development"
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    agent_model: str = "gemini-3.5-flash"
    log_level: str = "INFO"
    max_cache_size: int = 1000
    cache_ttl_seconds: int = 300
    monitored_services: str = "incident-response-backend,incident-response-frontend"

    model_config = {"env_prefix": "AGENT_", "env_file": ".env"}

    @property
    def services_list(self) -> list[str]:
        return [s.strip() for s in self.monitored_services.split(",") if s.strip()]
