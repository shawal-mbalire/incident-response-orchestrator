from abc import ABC, abstractmethod

from incident_response.domain.events.base import DomainEvent


class EventPublisherPort(ABC):
    """Port: what the domain needs to publish domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        ...

    @abstractmethod
    async def publish_many(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        ...
