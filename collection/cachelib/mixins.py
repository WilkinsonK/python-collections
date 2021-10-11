import pickle

from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping

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
    def _new(cls, name, config, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(name, config, *args, **kwargs)

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
        """
        Not implemented here.
        Override this method to handle connecting
        to a host.
        """
        pass

    def close(self):
        self._close()

    def _close(self):
        self._connection.close()
        self._connection    = self.connectable
        self._connect_state = ConnectState.CLOSED


class CacheAgentTransactionMixIn(CacheAgentABCMixIn, BaseCacheAgentMixIn):

    def push(self, func: Callable, *args, **kwargs):
        sig = Signature(func, *args, **kwargs)
        self._push(sig)

    def _push(self, signature: Signature):
        """
        Not implemented here.
        Push an entry into the cache host.
        """
        pass

    def pull(self, func: Callable, *args, **kwargs):
        sig = Signature(func, *args, **kwargs)
        return self._pull(sig, Unknown)

    def _pull(self, signature: Signature, default=Unknown):
        """
        Not implemeneted here.
        Pull an entry, if exists, from the
        cache host.
        """
        pass
