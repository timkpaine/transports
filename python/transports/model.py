from asyncio import Queue
from collections import deque
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field, PrivateAttr, root_validator  # noqa: F401
from typing import TYPE_CHECKING, Any, Optional
from uuid import uuid4

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

    @root_validator(pre=True)
    @classmethod
    def apply_validation(cls, values):
        values["id"] = values.get("id", str(uuid4()))
        values["name"] = values.get("name", values["id"])
        values["created"] = values.get("created", datetime.utcnow())
        values["modified"] = values.get("modified", values["created"])
        return values

    # pydantic configuration
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        extra = "forbid"

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
            copied.modified = datetime.utcnow()

            if freeze:
                # make readonly
                # NOTE: can only do if not cloning
                copied.freeze()

        return copied

    @classmethod
    def _walk_types(cls):
        for field in cls.__fields__.values():
            # TODO is this good enough?
            yield field.annotation

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
