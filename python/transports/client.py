from asyncio import gather
from typing import Optional, Type
from .connection import Connection
from .model import BaseModel
from .transport import Transport


class Client(Connection):
    _transport: Transport
    _transport_type: Type
    _model: BaseModel
    _client_id: str = ""

    def __init__(
        self,
        transport: Transport,
        client_id: Optional[str] = None,
        **kwargs,
    ):
        self._transport = transport
        self._transport_type = transport.type
        self._client_id = client_id or ""

    async def open(self) -> BaseModel:
        # wait for client connection
        await self.connect(client_id=self._client_id)

        # Notify transport of connection
        await self._transport.connect()

        # receive initial
        initial = await self.receive()

        # register and return
        return await self._transport.onInitial(initial)

    async def close(self):
        # Notify transport of connection
        await self._transport.disconnect()
        await self.disconnect()

    async def initial(self) -> BaseModel:
        # run the open routing
        return await self.open()

    async def handle(self) -> None:
        try:
            # Now enter an infinite loop listening for updates from client/server forever
            await gather(self.sender(), self.receiver(), return_exceptions=True)
        except:
            raise
        finally:
            # run the on close routing
            await self.close()
