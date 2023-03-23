from aiohttp import ClientSession, ClientWebSocketResponse
from typing import Optional, Type
from ..client import Client
from ..json import JSONTransport


class AioHttpWebSocketClient(Client):
    _transport: JSONTransport
    _transport_type: Type = str

    _url: str
    _session: ClientSession
    _websocket: ClientWebSocketResponse
    _client_header: str

    def __init__(
        self,
        url: str,
        transport: JSONTransport,
        client_id: Optional[str] = None,
        client_header: str = "client-id",
        **kwargs,
    ):
        super().__init__(transport=transport, client_id=client_id)
        self._url = url
        self._client_header = client_header

    async def connect(self, client_id: Optional[str] = None):
        self._session = ClientSession()
        self._websocket = await self._session.ws_connect(
            self._url, headers={self._client_header: self._client_id} if self._client_id else None
        ).__aenter__()

    async def disconnect(self) -> None:
        await self._websocket.close()

    async def receive(self) -> str:  # type: ignore[override]
        return await self._websocket.receive_str()

    async def send(self, update: str) -> None:  # type: ignore[override]
        await self._websocket.send_str(update)
