from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field, PrivateAttr, root_validator  # noqa: F401
from typing import Optional
from uuid import uuid4

from .model import BaseModel


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

    @root_validator(pre=True)
    @classmethod
    def apply_validation(cls, values):
        values["id"] = values.get("id", str(uuid4()))
        values["created"] = values.get("created", datetime.utcnow())
        values["model_target"] = values.get("model_target", values["model"].id)
        return values

    # pydantic configuration
    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"
        frozen = True
        from_attributes = True

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
