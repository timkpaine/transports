import pydantic
from asyncio import Queue
from collections import deque
from datetime import datetime
from udatetime import utcnow
from pydantic import BaseModel as PydanticBaseModel, Field, PrivateAttr  # noqa: F401
from typing import Any, Optional, TYPE_CHECKING
from uuid import uuid4
from .utils import orjson_dumps, orjson_loads


if TYPE_CHECKING:
    from .transport import Transport
    from .update import Update


class BaseModel(PydanticBaseModel):
    # Basic fields
    id: str = ""
    name: str = ""
    label: str = ""

    # date fields
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

    # internal fields
    _frozen: bool = PrivateAttr(False)

    # TODO make threadsafe
    _out_queue: Queue["Update"] = PrivateAttr(default_factory=Queue)

    @pydantic.validator("id", pre=True, always=True)
    def default_id(cls, v, *, values, **kwargs):
        return v or str(uuid4())

    @pydantic.validator("name", pre=True, always=True)
    def default_name(cls, v, *, values, **kwargs):
        return v or values["id"]

    @pydantic.validator("created", pre=True, always=True)
    def default_created(cls, v):
        return v or utcnow()

    @pydantic.validator("modified", pre=True, always=True)
    def default_modified(cls, v, *, values, **kwargs):
        return v or values["created"]

    # pydantic configuration
    class Config:
        # any types
        arbitrary_types_allowed = True

        # allow mutation (see frozen as well)
        allow_mutation = True

        # pass around models by ref
        copy_on_model_validation = "none"

        # no undeclared fields
        extra = "forbid"

        # not frozen
        # frozen = False

        # access by attr
        orm_mode = True

        # json_encoders = {}
        json_dumps = orjson_dumps
        json_loads = orjson_loads

    def __hash__(self):
        return hash(self.id)

    # disallow mutation
    def freeze(self):
        # TODO unfreeze?
        self._frozen = True

    def __setattr__(self, name, value):
        if self._frozen:
            raise TypeError(f'"{self.__class__.__name__}" is frozen and does not support item assignment')
        # attach transport if its a basemodel
        # TODO
        # if self._transport and isinstance(value, BaseModel):
        #     value.onTransport(self._transport)
        super().__setattr__(name, value)

    # overload copy to replace id
    def copy(self, clone=False, freeze=False, *args, **kwargs):
        copied = super().copy(*args, **kwargs)

        if not clone:
            # assign new unique id
            copied.id = str(uuid4())

            # overload last_updated
            copied.modified = utcnow()

            if freeze:
                # make readonly
                # NOTE: can only do if not cloning
                copied.freeze()

        return copied

    @classmethod
    def _walk_types(cls):
        for field in cls.__fields__.values():
            # TODO is this good enough?
            yield field.type_

    # transport layer
    _transport: "Transport" = PrivateAttr(default=None)

    def onTransport(self, transport: "Transport", checked: Optional[set] = None):
        """recursively attach transport"""
        # attach transport to self
        self._transport = transport

        to_check: deque[Any] = deque()
        checked = set([self] + list(checked or set()))
        to_check.extend(list(self.__dict__.values()))

        while to_check:
            # bfs
            value_to_check = to_check.popleft()

            # recurse if its a basemodel
            if isinstance(value_to_check, BaseModel):
                if value_to_check not in checked and value_to_check._transport is None:
                    value_to_check.onTransport(transport=transport, checked=checked)
                # add self to checked list
                checked.add(value_to_check)

            # try to extract if its iterable in some form
            # check if dict first to check key and value
            if isinstance(value_to_check, dict):
                to_check.extend(list(value_to_check.keys()))
                to_check.extend(list(value_to_check.values()))
            elif isinstance(value_to_check, (list, set, tuple)):
                to_check.extend((e for e in value_to_check))
            else:
                # TODO: give up?
                ...

    def onUpdate(self, other: "BaseModel", **kwargs) -> None:
        # TODO json diff OR
        # monkeypatch setattr/setitem recursively >:-)
        ...

    def update(self, model: "BaseModel", model_target: str = ""):
        from .update import Update

        self.send(Update(model=model, model_target=model_target))

    def notifyConnect(self, client_id: str) -> None:
        # TODO disallow?
        ...

    def notifyDisconnect(self, client_id: str) -> None:
        # TODO cleanup?
        ...

    def send(self, update: "Update") -> None:
        self._out_queue.put_nowait(update)

    async def sendAsync(self, update: "Update") -> None:
        await self._out_queue.put(update)

    def get(self) -> "Update":
        # TODO
        return self._transport.run(self._out_queue.get())

    async def getAsync(self) -> "Update":
        return await self._out_queue.get()

    def receive(self, update: "Update") -> None:
        # TODO
        # to be overloaded
        self.onUpdate(update.model)

    async def receiveAsync(self, update: "Update") -> None:
        return self.receive(update=update)


# class ListModel(PydanticBaseModel):
#     __root__: List[BaseModel]
#     class Config:
#         json_dumps = orjson_dumps
#         json_loads = orjson_loads
# class DictModel(PydanticBaseModel):
#     __root__: Dict[Any, BaseModel]
#     class Config:
#         json_dumps = orjson_dumps
#         json_loads = orjson_loads
