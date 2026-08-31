from incident_response.domain.events.base import DomainEvent
from incident_response.domain.ports.outbound.events import EventPublisherPort


class InMemoryEventPublisher(EventPublisherPort):
    """Outbound adapter: in-memory event publisher for testing."""

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)

    async def publish_many(self, events: list[DomainEvent]) -> None:
        self.published.extend(events)
