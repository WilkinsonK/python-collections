"""
ApiClient Library as standardization of API client objects.
"""
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from typing import Any, Mapping, Tuple, Union

import requests


NoValue           = type("NoValue", (int,), {})
ConnectionTimeout = type("ConnectionTimeout", (float,), {})
ReadTimeout       = type("ReadTimeout", (float,), {})


class ApplyBehavior(Enum):
    REPLACE = lambda session, key, value: setattr(session, key, value)
    UPDATE  = lambda session, key, value: getattr(session, key).update(value)
    APPEND  = lambda session, key, value: getattr(session, key).append(value)
    PREPEND = lambda session, key, value: getattr(session, key).insert(0, value)


@dataclass
class AttrDefault:
    name:  str
    value: Any
    behavior: ApplyBehavior = ApplyBehavior.REPLACE

    def apply(self, session: requests.Session, value: Any):
        """Apply the assigned attribute to the session."""
        self.behavior(session, self.name, value or self.value)


class BaseApiClient(ABC, object):
    """
    Access object for interaction with an external API.
    """

    # Client specific attributes
    root_url:                                                    str = NoValue
    max_timeout: Union[float, Tuple[ConnectionTimeout, ReadTimeout]] = NoValue

    # Internal session specific attributes
    headers:        Mapping[str, Any]
    proxies:        Mapping[str, str]
    hooks:          Mapping[str, str]
    auth:                         str
    stream:                      bool
    verify:                      bool
    cert: Union[str, bytes, PathLike]

    _session: requests.Session
    _session_attr_defaults: Tuple[AttrDefault] = (
        AttrDefault("headers", {}, ApplyBehavior.UPDATE),
        AttrDefault("proxies", {}, ApplyBehavior.UPDATE),
        AttrDefault("hooks", {}, ApplyBehavior.UPDATE),
        AttrDefault("auth", None),
        AttrDefault("stream", False),
        AttrDefault("verify", True),
        AttrDefault("cert", None)
    )

    _required_attrs: Tuple[str] = ("root_url", "max_timeout")

    def __new__(cls, *args, **kwargs):
        cls._validate_required_attrs()
        inst = cls._make_new(args, kwargs)
        return inst

    @classmethod
    def _make_new(cls, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(*args, **kwargs)
        return inst

    @classmethod
    def _validate_required_attrs(cls):
        for attr in cls._required_attrs:
            cls._validate_required_attr(attr)

    @classmethod
    def _validate_required_attr(cls, attr):
        if getattr(cls, attr, NoValue) is NoValue:
            raise RequiredAttributeError(
                f"expected {attr!r} of {cls.__name__!r} to have "
                f"a defined value, not {NoValue.__name__!r}")

    def _init(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        self._init_session()
        self.healthcheck()

    def _init_session(self, **kwargs):
        ss = requests.Session()
        for attr in self._session_attr_defaults:
            value = getattr(self, attr.name, None)
            attr.apply(ss, kwargs.get(attr.name, value))
        self._session = ss

    def _send(self, method, endpoint, **kwargs):
        address = "/".join([self.root_url, endpoint or ""])
        timeout = kwargs.pop("timeout", self.max_timeout)
        return self.session.request(
            method, url=address, timeout=timeout, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    @property
    def session(self) -> requests.Session:
        return self._session

    def handle_http_error(self, error: requests.HTTPError, resp: requests.Response = None) -> None:
        """Handle http protocol errors."""
        args = (error,)
        if resp is not None:
            args = (*args, resp.status_code, resp.elapsed.total_seconds())
        raise BadResponseError(*args)

    def healthcheck(self) -> int:
        """Send a health check ping to api reference."""
        resp = self.send("get")
        return resp

    def refresh(self, **kwargs) -> None:
        """Reset the client session."""
        self.session.close()
        self._init_session(**kwargs)

    def send(self, method: str, endpoint: str = None, data: dict = None, **kwargs) -> requests.Response:
        """Send a request using the ApiClient settings."""
        try:
            resp = self._send(method, endpoint, data=data, **kwargs)
            resp.raise_for_status()
        except requests.RequestException as error:
            self.handle_http_error(error, error.response)
        return resp


class ApiClientError(Exception):
    """Raise on errors related to the ApiClient."""

class BadResponseError(ApiClientError):
    """Raise if response from sent request is bad."""

    def __init__(self, message, status=500, elapsed=0.0):
        self.elapsed  = elapsed
        self.message  = message
        self.status   = status
        super(BadResponseError, self).__init__()

    def __str__(self):
        return f"<[{self.status}]: {self.message} [elapsed: {self.elapsed}s]"

class RequiredAttributeError(ApiClientError):
    """Raise if a required attribute is either missing or invalid."""
