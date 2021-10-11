import sqlite3

from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Mapping, Tuple, Union

import psycopg2

from consumerlib.clients.maps import ConnectState
from consumerlib.helpers.maps import FetchMap, ParamMap


class BaseClientMixIn:
    connect_params = ParamMap
    connectable    = sqlite3.connect

    _connection: sqlite3.Connection
    _logger:     Logger
    _settings:   Mapping[str, Any]

    _connect_state  = ConnectState.CLOSED
    _connect_params = {}

    @property
    def connection(self):
        return self._connection

    @property
    def connect_state(self):
        return self._connect_state

    @property
    def logger(self):
        return self._logger

    @property
    def settings(self):
        return self._settings


class ClientInitMixin(BaseClientMixIn):

    def __new__(cls, *args, **kwargs):
        return cls._new(args, kwargs)

    @classmethod
    def _new(cls, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(*args, **kwargs)
        return inst

    def _init(self, settings, logger, *args, **kwargs):
        self._init_attributes(settings, logger)
        self.__init__(*args, **kwargs)

    def _init_attributes(self, settings, logger):
        self._logger   = logger
        self._settings = settings
        self._connect_params = self._init_connect_params()

    def _init_connect_params(self):
        _connect_params = {}
        for key, setting in self.connect_params.items():
            value = self._settings[setting.name]
            setting.validate_and_set(value)
            _connect_params[key] = setting.value
        return _connect_params


class ClientABCMixIn(BaseClientMixIn, ABC):

    @abstractmethod
    def connect(self) -> None:
        """Connect to target host."""
        return NotImplemented

    @abstractmethod
    def close(self) -> None:
        """Disconnect from target host."""
        return NotImplemented


class ClientHostMixIn(ClientABCMixIn, BaseClientMixIn):

    def _connect(self) -> None:
        self._connect_state = ConnectState.PENDING
        try:
            conn = self.__class__.connectable
            self._connection = conn(**self._connect_params)
            self._connect_state = ConnectState.OPEN
        except:
            self._connect_state = ConnectState.CLOSED
            raise

    def _close(self) -> None:
        try:
            self._connection.close()
        except:
            raise
        finally:
            self._connect_state = ConnectState.CLOSED


class ClientContextMixIn(ClientHostMixIn, BaseClientMixIn):

    def __enter__(self):
        if self._connect_state is ConnectState.CLOSED:
            self._connect()
        return self

    def __exit__(self, type, value, traceback):
        self._close()


class ClientDatabaseMixIn(ClientHostMixIn, BaseClientMixIn):
    connectable = psycopg2.connect

    def cursor(self, **kwargs):
        if self._connect_state is ConnectState.CLOSED:
            self._connect()
        return self._cursor(**kwargs)

    def _cursor(self, **kwargs):
        return self._connection.cursor(**kwargs)

    def commit(self):
        if self._connect_state is ConnectState.CLOSED:
            return
        self._commit()

    def _commit(self):
        self._connection.commit()

    def execute(self, query: str, params: Union[Mapping[str, Any], Tuple], fetch=FetchMap.NONE):
        if self._connect_state is ConnectState.CLOSED:
            return # need to define a not connected error
        fetch = self._parse_fetch_method(fetch)
        return self._execute(query, params, fetch)

    def _execute(self, query, params, fetch):
        with self._cursor() as cursor:
            cursor.execute(query, params)
            result = fetch(cursor)
        return result

    def _parse_fetch_method(self, method: Union[str, FetchMap]):
        if isinstance(method, str):
            return FetchMap[method.upper()]
        return method
