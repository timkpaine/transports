import time
import pytest
from typing import List, Dict
from transports import Transport, BaseModel


class MyModel(BaseModel):
    ...


class MyOtherModel(BaseModel):
    ...


class MyParentModel(BaseModel):
    x: List[MyModel]
    y: Dict[str, MyOtherModel]


class TestTransport:
    def test_instantiation(self):
        x = MyModel()
        assert x.name == x.id

    def test_copy(self):
        x = MyModel()

        # introduce a minimal delay
        time.sleep(0.001)

        y = x.copy()
        z = x.copy(clone=True)

        # copy assigns new id and new last_updated
        assert x.id != y.id
        assert x.created == y.created
        assert x.modified != y.modified

        # copy with cloning creates identical copy
        assert x.id == z.id
        assert x.created == z.created
        assert x.modified == z.modified

    def test_copy_freeze(self):
        x = MyModel()

        # introduce a minimal delay
        time.sleep(0.001)

        y = x.copy(freeze=True)

        # copy assigns new id and new last_updated
        assert x.id != y.id
        assert x.created == y.created
        assert x.modified != y.modified

        with pytest.raises(TypeError):
            y.name = "test"
        x.name = "test"
        assert y.name != "test"
        assert x.name == "test"

    def test_attach_transport(self):
        mm = MyModel()
        mom = MyOtherModel()
        pm = MyParentModel(x=[mm], y={"a": mom})

        transport = Transport()
        pm.onTransport(transport)

        assert pm._transport == transport
        assert mm._transport == transport
        assert mom._transport == transport

    def test_modelmap(self):
        ts = Transport(None)
        ts.hosts(MyParentModel)

        assert "MyParentModel" in ts.model_map
        assert ts.model_map["MyParentModel"] == MyParentModel
        assert "MyModel" in ts.model_map
        assert ts.model_map["MyModel"] == MyModel
        assert "MyOtherModel" in ts.model_map
        assert ts.model_map["MyOtherModel"] == MyOtherModel
