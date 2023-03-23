from contextlib import contextmanager
from starlette.websockets import WebSocket, WebSocketDisconnect
from typing import Type
from ..server import Server
from ..model import BaseModel
from ..json import JSONTransport


class StarletteWebSocketServer(Server):
    _transport: JSONTransport
    _transport_type: Type = str

    _websocket: WebSocket
    _client_header: str

    def __init__(
        self,
        websocket: WebSocket,
        transport: JSONTransport,
        model: BaseModel,
        shared: bool = True,
        readonly: bool = False,
        client_header: str = "client-id",
        **kwargs,
    ):
        super().__init__(transport=transport, model=model, shared=shared, readonly=readonly, **kwargs)
        self._websocket = websocket
        self._client_header = client_header

    async def connect(self):
        # on open, receive data from websocket
        # connect to websocket
        await self._websocket.accept()

        # graph client information from websocket,
        # if null or empty will be autoassigned
        return self._websocket.headers.get(self._client_header, "")

    @contextmanager
    def handleDisconnect(self):
        with super().handleDisconnect():
            try:
                yield
            except (WebSocketDisconnect,):
                ...

    async def receive(self) -> str:  # type: ignore[override]
        # grab from client
        return await self._websocket.receive_text()

    async def send(self, update: str):  # type: ignore[override]
        # send to client
        await self._websocket.send_text(update)

    async def disconnect(self) -> None:
        try:
            await self._websocket.close()
        except RuntimeError:
            # ignore if websocket already closed
            ...

    # Use common docstring
    __init__.__doc__ = Server.__init__.__doc__
