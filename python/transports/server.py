from asyncio import gather
from typing import Type
from .connection import Connection
from .model import BaseModel
from .transport import Transport


class Server(Connection):
    _transport: Transport
    _transport_type: Type
    _model: BaseModel
    _client_id: str
    _shared: bool
    _readonly: bool

    def __init__(
        self,
        transport: Transport,
        model: BaseModel,
        shared: bool = True,
        readonly: bool = False,
        **kwargs,
    ):
        self._transport = transport
        self._transport_type = transport.type
        self._model = model
        self._client_id = ""
        self._shared = shared
        self._readonly = readonly

    async def onOpen(self):
        # wait for client connection
        self._client_id = await self.connect() or ""

        # Notify transport of connection
        self._client_id = await self._transport.onConnect(client_id=self._client_id)

        # Host model
        await self._transport.host(model=self._model, client_id=self._client_id, shared=self._shared, readonly=self._readonly)

        # send initial
        initial = self._transport.initial(client_id=self._client_id)

        # send to client
        await self.send(initial)

    async def onClose(self):
        # Notify transport of connection
        await self._transport.onDisconnect(model=self._model, client_id=self._client_id)
        # await self.disconnect()

    async def handle(self) -> None:
        try:
            # run the open routing
            await self.onOpen()

            # Now enter an infinite loop listening for updates from client/server forever
            await gather(self.sender(), self.receiver(), return_exceptions=True)
        except:
            raise
        finally:
            # run the on close routing
            await self.onClose()
