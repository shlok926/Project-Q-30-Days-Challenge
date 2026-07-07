from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DomainEventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any):
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    await handler(payload)
                except Exception as e:
                    logger.error(f"Error handling event {event_type}: {e}")

event_bus = DomainEventBus()

class EventTypes:
    EXPERIMENT_CREATED = "ExperimentCreated"
    EXPERIMENT_QUEUED = "ExperimentQueued"
    EXPERIMENT_COMPLETED = "ExperimentCompleted"
    JOB_FAILED = "JobFailed"
    PROVIDER_UNAVAILABLE = "ProviderUnavailable"
