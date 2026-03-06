import json
from collections import defaultdict
from typing import Any

from app.core.config import Settings


class MemoryEventBus:
    def __init__(self) -> None:
        self.events: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        self.events[topic].append(payload)


class NATSEventBus:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._nc = None

    async def _connect(self):
        if self._nc is None:
            from nats.aio.client import Client

            self._nc = Client()
            await self._nc.connect(servers=[self.settings.nats_url])

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        await self._connect()
        await self._nc.publish(topic, json.dumps(payload).encode())


def get_event_bus(settings: Settings):
    if settings.event_bus_backend == "nats":
        return NATSEventBus(settings)
    return MemoryEventBus()
