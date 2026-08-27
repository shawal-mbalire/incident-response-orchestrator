from typing import Any

from google.cloud import firestore

from incident_response.domain.ports.outbound.state_store import StateStorePort


class FirestoreStateStoreAdapter(StateStorePort):
    """Outbound adapter: wraps Google Firestore for persistent state."""

    def __init__(self, project_id: str) -> None:
        self._client = firestore.Client(project=project_id)

    async def save(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        doc_ref = self._client.collection(collection).document(document_id)
        doc_ref.set(data)

    async def load(self, collection: str, document_id: str) -> dict[str, Any] | None:
        doc_ref = self._client.collection(collection).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def list_collection(self, collection: str, limit: int = 100) -> list[dict[str, Any]]:
        docs = self._client.collection(collection).limit(limit).stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
