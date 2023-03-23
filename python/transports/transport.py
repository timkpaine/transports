from abc import ABCMeta
from asyncio import get_event_loop, run_coroutine_threadsafe, AbstractEventLoop
from typing import Dict, Optional, Type
from uuid import uuid4
from .model import BaseModel
from .update import Update


class ThreadedMixin:
    loop: AbstractEventLoop

    def run(self, coro):
        """Run a coroutine in a threadsafe and syncronous manner"""
        future = run_coroutine_threadsafe(coro, self.loop)
        # return raw future, don't wait for result
        return future.result()

    async def runAsync(self, coro):
        """Run a coroutine in a threadsafe and syncronous manner"""
        future = run_coroutine_threadsafe(coro, self.loop)
        # return raw future, don't wait for result
        return future


class Transport(ThreadedMixin, metaclass=ABCMeta):
    # Server attributes
    readonly: Dict[str, bool]  # Client -> T/F
    models: Dict[str, BaseModel]  # Client -> Model
    clients: Dict[str, str]  # Model ID -> Client
    type: Type = BaseModel

    # Client attributes
    server_models: Dict[str, BaseModel]  # type: ignore[no-redef]
    # Model ID -> Model
    # NOTE this is reused for both client and server
    model_map: Dict[str, Type[BaseModel]]  # Class name -> BaseModel type

    # General attributes
    loop: AbstractEventLoop

    def __init__(self, event_loop=None):
        # Server attributes
        self.readonly = {}
        self.models = {}
        self.clients = {}

        # Client attributes
        self.server_models = {}
        self.model_map = {}

        # General attributes
        self.loop = event_loop or get_event_loop()

    ##################
    # Server methods #
    ##################
    async def onConnect(self, client_id: Optional[str] = None) -> str:
        """Connect to a client.
        Should be called by the server when the client connects to the server.

        Args:
            client_id (Optional[str], optional): A unique string to represent the client, should be generated if not provided. Defaults to None.
        Returns:
            str: client id, either the provided value or the newly generated client id
        """
        if not client_id:
            client_id = str(uuid4())

        # and return the (possibly generated) client id
        return client_id

    async def host(self, model: BaseModel, client_id: str, shared: bool = True, readonly: bool = False) -> None:
        """Host a model for a given client.

        Args:
            model (BaseModel): An instance of BaseModel. Defaults to None.
            client_id (Optional[str], optional): A unique string to represent the client, should be generated if not provided. Defaults to None.
            shared (bool, optional): Whether or not the model should be shared amonst multiple clients.
                                     If False, the model will be copied. Defaults to True.
            readonly (bool, optional): Whether or not the client should be able to modify the model. Defaults to False.

        Returns:
            str: client id, either the provided value or the newly generated client id
        """
        if not shared or readonly:
            # copy the model
            model = model.copy()

        if readonly:
            # mark model as readonly
            model.freeze()

        # maintain map of client id -> model id
        self.models[client_id] = model

        # maintain reverse map of model id -> client id
        self.clients[model.id] = client_id

        # maintain map of if client's view is readonly
        self.readonly[client_id] = readonly

        # notify model of connection
        model.notifyConnect(client_id=client_id)

    async def onDisconnect(self, model: BaseModel, client_id: str) -> None:
        """Disconnect and cleanup client-specific assets.

        Should be called by the server when the client disconnects from the server.

        Args:
            client_id (str): _description_
        """
        model = self.models.pop(client_id, None) or model  # type: ignore[arg-type]
        self.readonly.pop(client_id, None)
        self.clients.pop(model.id, None)

        # notify model of disconnect
        model.notifyDisconnect(client_id=client_id)

    def initial(self, client_id: str) -> Update:
        """Create an initial update to be sent to the client

        Args:
            client_id (str): client id for looking up model to send

        Returns:
            Update: the initial model to send to the client
        """
        return Update(model=self.models[client_id])

    ##################
    # Client methods #
    ##################
    def hosts(self, model_type: Type[BaseModel]) -> None:
        """Host a model type, allowing the server to create instances of that type

        Args:
            model_type (Type[BaseModel]): type of model to create, should be unique
        """

        # register model as eligible
        self.model_map[model_type.__name__] = model_type

        # recursively descent types and register any other models we find
        for value_type in model_type._walk_types():
            if isinstance(value_type, type) and issubclass(value_type, BaseModel) and value_type.__name__ not in self.model_map:
                self.hosts(value_type)

    async def connect(self):
        # TODO
        ...

    async def disconnect(self):
        # TODO
        self.server_models = {}

    async def onInitial(self, update: Update) -> BaseModel:
        # TODO multi model and events
        model = update.model

        # register in model map
        self.server_models[model.id] = model

        # FIXME
        self.models[""] = model

        # return the instance
        return model

    #################
    # Bidirectional #
    #################
    async def send(self, client_id: str) -> Update:
        # grab model from client
        model = self.models[client_id]

        # pull latest send update
        return await model.getAsync()

    async def receive(self, client_id: str, update: Update) -> None:
        # grab model from client
        model = self.models[client_id]

        # push update to model
        await model.receiveAsync(update)
