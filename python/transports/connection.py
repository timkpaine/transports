from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Type
from .transport import Transport
from .update import Update


class Connection(ABC):
    _transport: Transport
    _transport_type: Type
    _client_id: str

    @contextmanager
    def handleDisconnect(self):
        """Should be overloaded like so by specific client implementations:

        @contextmanager
        def handleDisconnect(self):
            with super().handleDisconnect():
                try:
                    yield
                except (ServerFrameworkSpecificExceptions...):
                    ...
        """
        try:
            yield
        except (KeyboardInterrupt,):
            ...

    async def receiver(self) -> None:
        with self.handleDisconnect():
            while True:
                # grab from client
                update: Update = await self.receive()

                # send to transport to be sent to models
                await self._transport.receive(client_id=self._client_id, update=update)

    async def sender(self) -> None:
        """An infinite async generator that should"""
        with self.handleDisconnect():
            while True:
                # get update from transport derived from models
                update: Update = await self._transport.send(client_id=self._client_id)

                # send to client
                await self.send(update)

    @abstractmethod
    async def connect(self, client_id: Optional[str] = None) -> str:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def receive(self) -> Update:
        ...

    @abstractmethod
    async def send(self, update: Update) -> None:
        ...
