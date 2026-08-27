from abc import ABC, abstractmethod
from typing import Any


class StateStorePort(ABC):
    """Port: what the domain needs from a persistent state store."""

    @abstractmethod
    async def save(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        """Persist a document."""
        ...

    @abstractmethod
    async def load(self, collection: str, document_id: str) -> dict[str, Any] | None:
        """Retrieve a document by ID."""
        ...

    @abstractmethod
    async def list_collection(self, collection: str, limit: int = 100) -> list[dict[str, Any]]:
        """List documents in a collection."""
        ...
