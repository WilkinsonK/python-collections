import pickle

from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping, Union

import redis

from cachelib.maps import ConnectState, ParamMap
from cachelib.signatures import Signature
from cachelib.typedefs import Null, Unknown


class BaseCacheAgentMixIn:
    connect_params = ParamMap
    connectable    = redis.Redis
    serializer     = pickle

    _agent_conf: Mapping[str, Any]
    _connection: connectable

    _connect_params = {}
    _connect_state  = ConnectState.CLOSED

    @property
    def connection(self):
        return self._connection

    @property
    def connect_state(self):
        return self._connect_state

    @property
    def name(self):
        return self._agent_name


class CacheAgentInitMixIn(BaseCacheAgentMixIn):

    def __new__(cls, name=Null, config={}, *args, **kwargs):
        return cls._new(name, config, args, kwargs)

    @classmethod
    def _new(cls, name, config, args=(), kwargs={}, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(name, config, *args, **kwargs)

    def __init__(self):
        self.connect()

    def _init(self, config, *args, **kwargs):
        self._agent_conf = config
        self._init_connect_params()
        self.__init__(*args, **kwargs)

    def _init_connect_params(self):
        for key, setting in self.connect_params.items():
            value = self._agent_conf[setting.name]
            setting.validate(value)
            self._connect_params[key] = value

    def connect(self):
        """
        Not implemented here.
        Connect to cache host.
        """
        pass


class CacheAgentABCMixIn(BaseCacheAgentMixIn, ABC):

    @abstractmethod
    def connect(self) -> None:
        """Connect to cache host."""
        return NotImplemented

    @abstractmethod
    def close(self) -> None:
        """Disconnect from cache host."""
        return NotImplemented

    @abstractmethod
    def pull(self, func: Callable, *args, **kwargs) -> Any:
        """Pull an entry from the cache."""
        return NotImplemented

    @abstractmethod
    def push(self, func: Callable, *args, **kwargs) -> None:
        """Push an entry into the cache."""
        return NotImplemented


class CacheAgentHostsMixIn(CacheAgentABCMixIn, BaseCacheAgentMixIn):

    def connect(self):
        try:
            self._connect()
            self._connect_state = ConnectState.OPEN
        except:
            self._close()
            raise

    def _connect(self):
        conf             = self._connect_params
        self._connection = self.connectable(**conf)

    def close(self):
        self._close()
        self._connect_state = ConnectState.CLOSED

    def _close(self):
        self._connection.close()
        self._connection = self.connectable


class CacheAgentTransactionMixIn(CacheAgentABCMixIn, BaseCacheAgentMixIn):

    def push(self, func: Callable, *args, **kwargs):
        sig = Signature(func, *args, **kwargs)
        self._push(sig)
        return sig

    def _push(self, signature: Signature):
        """
        Not implemented here.
        Push an entry into the cache host.
        """
        pass

    def pull(self, func: Callable, *args, **kwargs):
        sig     = Signature(func, *args, **kwargs)
        default = Unknown
        return self._pull(sig, default)

    def _pull(self, signature: Union[bytes, str], default: Any):
        """
        Not implemeneted here.
        Pull an entry, if exists, from the
        cache host.
        """
        pass
