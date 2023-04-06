from orjson import loads
from typing import Optional, Type

from .exceptions import UpdateMalformed
from .model import BaseModel
from .transport import Transport
from .update import Update


class JSONTransport(Transport):
    type: Type = str

    ##################
    # Server methods #
    ##################
    async def onConnect(self, client_id: Optional[str] = None) -> str:
        # defer to parent
        return await super().onConnect(client_id=client_id)

    async def host(self, model: BaseModel, client_id: str, shared: bool = True, readonly: bool = False) -> None:
        # defer to parent
        return await super().host(model=model, client_id=client_id, shared=shared, readonly=readonly)

    async def onDisconnect(self, model: BaseModel, client_id: str) -> None:  # type: ignore[override]
        # defer to parent
        return await super().onDisconnect(model=model, client_id=client_id)

    def initial(self, client_id: str) -> str:  # type: ignore[override]
        # defer to parent
        return super().initial(client_id=client_id).json()

    ##################
    # Client methods #
    ##################
    async def onInitial(self, update: str) -> BaseModel:  # type: ignore[override]
        update_inst: Update = await self._update_to_model(update)
        return await super().onInitial(update=update_inst)

    async def _update_to_model(self, update: str) -> Update:
        # first, parse out the json into a dict
        data = loads(update)

        # now lookup the model map
        if "model_type" not in data:
            raise UpdateMalformed("Update data has no `model_type`")

        if "model_target" not in data:
            raise UpdateMalformed("Update data has no `model_target`")

        if data["model_type"] not in self.model_map:
            raise UpdateMalformed(f"Class type ({data['model_type']}) not known, did you forget to call `hosts`?")

        # grab the class type
        class_type: Type[BaseModel] = self.model_map[data.pop("model_type")]

        # instantiate the inital model
        model_inst: BaseModel = class_type.parse_obj(data["model"])
        data["model"] = model_inst

        # defer to parent now that we have the model
        return Update(**data)

    #################
    # Bidirectional #
    #################
    async def send(self, client_id: str) -> str:  # type: ignore[override]
        return (await super().send(client_id=client_id)).json()

    async def receive(self, client_id: str, update: str) -> None:  # type: ignore[override]
        update_inst: Update = await self._update_to_model(update)
        await super().receive(client_id=client_id, update=update_inst)
