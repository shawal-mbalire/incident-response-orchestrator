import time
from typing import Any

from incident_response.domain.ports.outbound.state_store import StateStorePort


class InMemoryStateStoreAdapter(StateStorePort):
    """Outbound adapter: in-memory mock with TTL support for testing."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._store: dict[str, dict[str, dict[str, Any]]] = {}
        self._timestamps: dict[str, dict[str, float]] = {}
        self._ttl_seconds = ttl_seconds

    def _evict_expired(self, collection: str) -> None:
        if collection not in self._timestamps:
            return
        now = time.time()
        expired = [
            doc_id
            for doc_id, ts in self._timestamps[collection].items()
            if now - ts > self._ttl_seconds
        ]
        for doc_id in expired:
            self._store.get(collection, {}).pop(doc_id, None)
            self._timestamps[collection].pop(doc_id, None)

    async def save(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        if collection not in self._store:
            self._store[collection] = {}
            self._timestamps[collection] = {}
        self._store[collection][document_id] = data
        self._timestamps[collection][document_id] = time.time()

    async def load(self, collection: str, document_id: str) -> dict[str, Any] | None:
        self._evict_expired(collection)
        return self._store.get(collection, {}).get(document_id)

    async def list_collection(self, collection: str, limit: int = 100) -> list[dict[str, Any]]:
        self._evict_expired(collection)
        docs = list(self._store.get(collection, {}).values())[:limit]
        return docs
