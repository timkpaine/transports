import pydantic
from datetime import datetime
from udatetime import utcnow
from pydantic import BaseModel as PydanticBaseModel, Field, PrivateAttr  # noqa: F401
from typing import Optional
from uuid import uuid4
from .model import BaseModel
from .utils import orjson_dumps, orjson_loads


class Update(PydanticBaseModel):
    # Basic fields
    id: str = ""
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

    # Advanced fields
    model: BaseModel

    # internals
    model_type: str = ""  # class type of `model`
    model_target: str = ""  # model target to which `model` should be sent to

    @pydantic.validator("id", pre=True, always=True)
    def default_id(cls, v, *, values, **kwargs):
        return v or str(uuid4())

    @pydantic.validator("created", pre=True, always=True)
    def default_created(cls, v):
        return v or utcnow()

    @pydantic.validator("modified", pre=True, always=True)
    def default_modified(cls, v, *, values, **kwargs):
        return v or values["created"]

    @pydantic.validator("model_target", pre=True, always=True)
    def default_model_target(cls, v, *, values, **kwargs):
        return v or values["model"].id

    # pydantic configuration
    class Config:
        # any types
        arbitrary_types_allowed = True

        # allow mutation (see frozen as well)
        allow_mutation = False

        # pass around models by value
        copy_on_model_validation = "deep"

        # no undeclared fields
        extra = "forbid"

        # frozen
        frozen = True

        # access by attr
        orm_mode = True

        # json_encoders = {}
        json_dumps = orjson_dumps
        json_loads = orjson_loads

    def __hash__(self):
        return hash(self.id)

    # overload dict to include model name
    def dict(self, *args, **kwargs):
        ret = super().dict(*args, **kwargs)
        ret["model_type"] = self.model.__class__.__name__
        return ret

    # `json()` doesnt use `dict`, so have to get creative
    def json(self, *args, **kwargs):
        return self.__config__.json_dumps(self.dict(), default=self.__json_encoder__)
