from typing import Any

from incident_response.domain.ports.outbound.state_store import StateStorePort


class InMemoryStateStoreAdapter(StateStorePort):
    """Outbound adapter: in-memory mock for testing and local dev."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, dict[str, Any]]] = {}

    async def save(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        if collection not in self._store:
            self._store[collection] = {}
        self._store[collection][document_id] = data

    async def load(self, collection: str, document_id: str) -> dict[str, Any] | None:
        return self._store.get(collection, {}).get(document_id)

    async def list_collection(self, collection: str, limit: int = 100) -> list[dict[str, Any]]:
        docs = list(self._store.get(collection, {}).values())[:limit]
        return docs
