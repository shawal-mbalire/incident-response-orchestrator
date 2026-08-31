import logging
from typing import Any

from google.cloud import firestore

from incident_response.domain.exceptions import AdapterError
from incident_response.domain.ports.outbound.state_store import StateStorePort

logger = logging.getLogger(__name__)


class FirestoreStateStoreAdapter(StateStorePort):
    """Outbound adapter: wraps Google Firestore for persistent state."""

    def __init__(self, project_id: str) -> None:
        self._client = firestore.Client(project=project_id)

    async def save(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            doc_ref.set(data)
            logger.debug("saved_document", extra={"collection": collection, "doc_id": document_id})
        except Exception as e:
            logger.error(
                "save_document_error",
                extra={"collection": collection, "doc_id": document_id, "error": str(e)},
            )
            raise AdapterError("Firestore", f"Failed to save document: {e}", cause=e) from e

    async def load(self, collection: str, document_id: str) -> dict[str, Any] | None:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(
                "load_document_error",
                extra={"collection": collection, "doc_id": document_id, "error": str(e)},
            )
            raise AdapterError("Firestore", f"Failed to load document: {e}", cause=e) from e

    async def list_collection(self, collection: str, limit: int = 100) -> list[dict[str, Any]]:
        try:
            docs = self._client.collection(collection).limit(limit).stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            logger.error("list_collection_error", extra={"collection": collection, "error": str(e)})
            raise AdapterError("Firestore", f"Failed to list collection: {e}", cause=e) from e
