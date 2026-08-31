class DomainError(Exception):
    """Base domain error with error code for API mapping."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.code = code
        self.message = message
        super().__init__(message)


class ValidationError(DomainError):
    """Invalid domain data."""

    def __init__(self, message: str, field: str = ""):
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundError(DomainError):
    """Entity not found."""

    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} '{entity_id}' not found", code="NOT_FOUND")


class AdapterError(DomainError):
    """External adapter failure."""

    def __init__(self, adapter: str, message: str, cause: Exception | None = None):
        self.adapter = adapter
        self.cause = cause
        super().__init__(f"{adapter}: {message}", code="ADAPTER_ERROR")


class ConcurrencyError(DomainError):
    """Optimistic locking failure."""

    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            f"Concurrent modification of {entity} '{entity_id}'",
            code="CONCURRENCY_ERROR",
        )
