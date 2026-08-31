from incident_response.config.container import Container

_container: Container | None = None


def set_container(container: Container) -> None:
    """Set the global container for dependency injection."""
    global _container
    _container = container


def get_container() -> Container:
    """Get the global container."""
    if _container is None:
        raise RuntimeError("Container not initialized. Call set_container() first.")
    return _container


def get_analysis_service():
    """FastAPI dependency: get the incident analysis service."""
    return get_container().incident_service
