"""
Use for simplifying API callouts.
"""

import abc
import enum
import os

from typing import Any, Callable

import requests


def _is_annotated(obj: object, name: str):
    return name in obj.__annotations__


def _get_public_attrs(obj: object):
    return [(i, getattr(obj, i))
        for i in dir(obj) if "_" not in i[:2]
    ]


def _ensure_annotated(obj: object, name: str):
    if not _is_annotated(obj, name):
        raise ClientFieldError(f"{name!r} was never annotated!")


class NotDefinedType(type):
    """Attribute or name has not been defined."""

    def __len__(self):
        return 0 # allows for if statements
                 # to recognize type as a
                 # pseudo null type

    def __repr__(self):
        return self.__name__


NotSet = NotDefinedType("NotSet", (), {})


class Applier(Callable[[object, str, Any], None]):
    """
    Determines how a value is applied to
    a target object.
    """

    def __call__(self, obj: object, name: str, value: Any) -> None:
        """Sets a value on a target object."""


class ApplierMeta(enum.EnumMeta, abc.ABCMeta):
    """
    Meta type to resolve metaclass conflict
    between `Applier` and `enum.EnumMeta`
    types.
    """


@enum.unique
class ApplyBehavior(Applier, enum.Enum, metaclass=ApplierMeta):
    """Define how an attribute is set on an object."""
    REPLACE = lambda obj, key, value: setattr(obj, key, value)
    UPDATE  = lambda obj, key, value: getattr(obj, key).update(value)
    APPEND  = lambda obj, key, value: getattr(obj, key).append(value)
    PREPEND = lambda obj, key, value: getattr(obj, key).insert(0, value)


@enum.unique
class RESTMethod(str, enum.Enum):
    """Method accepted by REST APIs."""
    CONNECT = "connect"
    DELETE  = "delete"
    GET     = "get"
    HEAD    = "head"
    OPTIONS = "options"
    PATCH   = "patch"
    POST    = "post"
    PUT     = "put"
    TRACE   = "trace"

    def __str__(self):
        return self.value


Method = RESTMethod


class AttributeField:
    annotation:      Any = NotSet
    apply_behavior:  ApplyBehavior
    default:         Any
    default_factory: Callable[..., Any]

    def __init__(self, default=NotSet, default_factory=NotSet, apply_behavior=NotSet, **kwargs):
        self.default         = default
        self.default_factory = default_factory
        self.apply_behavior  = apply_behavior or ApplyBehavior.REPLACE

    def apply(self, obj: object, name: str, value: Any):
        """
        Sets the given value to an attribute
        of the target object.
        """
        if _is_attribute(value):
            value = _attribute_as_value(value)

        try:
            self.apply_behavior(obj, name, value)
        except AttributeError:
            ApplyBehavior.REPLACE(obj, name, value)

    def validate(self, obj: object, name: str):
        """
        Enure value of object has been defined
        properly.
        """
        if not hasattr(obj, name):
            pass # TODO: raise all hell
        value = getattr(obj, name)

        if _is_attribute(value):
            field = value
            if not _has_default_option(field):
                raise ClientValidationError(
                    f"expected {name!r} of {obj.__name__!r} "
                    f"to have a defined value, not {NotSet!r}")
            value = _attribute_as_value(field)

        self.apply(obj, name, value)


def _attribute_as_value(field: AttributeField):
    if field.default_factory:
        return field.default_factory()
    return field.default


def _has_default_option(field: AttributeField):
    return any([
        field.default is not NotSet,
        field.default_factory is not NotSet])


def _is_attribute(obj: object):
    return isinstance(obj, AttributeField)


def _validate_fields(obj: object, fields: dict[str, AttributeField]):
    for name, field in fields.items():
        field.validate(obj, name)


def required():
    """
    Identify a required attribute field.
    """
    return AttributeField()


def optional(default: Any = None, **kwargs):
    """
    Identify an optional attribute field.
    """
    return AttributeField(default, **kwargs)


def optional_dict(apply_behavior=ApplyBehavior.UPDATE):
    """
    Identify an optional dictionary field.
    """
    return optional(
        default_factory=dict,
        apply_behavior=apply_behavior)


class APIClientABCMeta(abc.ABCMeta):
    __required_fields__: dict[str, AttributeField]
    __optional_fields__: dict[str, AttributeField]

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._identify_attributes()

    def _identify_attributes(cls):
        public_attrs = _get_public_attrs(cls)

        _required_, _optional_ = {}, {}
        for name, field in public_attrs:
            if not _is_attribute(field):
                continue
            _ensure_annotated(cls, name)

            field.annotation = cls.__annotations__[name]
            if not _has_default_option(field):
                _required_.update({name: field})
                continue

            _optional_.update({name: field})

        cls.__required_fields__ = _required_
        cls.__optional_fields__ = _optional_


class BaseAPIClient(abc.ABC, metaclass=APIClientABCMeta):

    # Client specific attributes
    max_timeout:     float | tuple[float, float] = required()
    root_uri:        str                         = required()
    healthcheck_uri: str                         = optional()

    # Session build specific attributes
    auth:                          str = optional()
    cert:    str | bytes | os.PathLike = optional()
    headers:            dict[str, Any] = optional_dict()
    hooks:              dict[str, str] = optional_dict()
    proxies:            dict[str, str] = optional_dict()
    stream:                       bool = optional(default=False)
    verify:                       bool = optional(default=True)

    __session__:        requests.Session
    __session_fields__:        tuple[str] = (
        "headers", "proxies", "hooks",
        "auth", "stream", "verify", "cert"
    )

    def __new__(cls, *args, **kwargs):
        cls._pre(args, kwargs)
        return cls._new(args, kwargs)

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.__session__.close()

    @classmethod
    def _pre(cls, args, kwargs):
        parent = cls._get_parent_class()

        _validate_fields(cls, parent.__required_fields__)
        _validate_fields(cls, parent.__optional_fields__)

    @classmethod
    def _new(cls, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(*args, **kwargs)
        return inst

    @classmethod
    def _get_parent_class(cls):
        if cls is not BaseAPIClient:
            return BaseAPIClient
        return cls

    def _init(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        self._init_session()
        self.healthcheck()

    def _init_session(self, **kwargs):
        parent = self._get_parent_class()
        field_names = self.__session_fields__

        _session_ = requests.Session()
        for name in field_names:
            value = getattr(self, name, None)
            field = parent.__optional_fields__[name]
            field.apply(_session_, name, kwargs.get(name, value))

        self.__session__ = _session_

    def handle_http_error(self, error: requests.HTTPError, resp: requests.Response = None) -> None:
        """Handle http protocol errors."""
        args = (error,)
        if resp is not None:
            args = (*args, resp.status_code, resp.elapsed.total_seconds())
        raise ClientResponseError(*args)

    def healthcheck(self) -> int:
        """Send a health check ping to api reference."""
        uri = (self.healthcheck_uri or self.root_uri)
        resp = self._send(RESTMethod.GET, "", root_uri=uri)
        return resp.status_code

    def refresh(self, **kwargs) -> None:
        """Reset the internal client session."""
        self.__session__.close()
        self._init_session(**kwargs)

    def send(self, method: RESTMethod, endpoint: str = None, **kwargs) -> requests.Response:
        """Send a request using the API Client settings."""
        try:
            resp = self._send(method, endpoint, **kwargs)
            resp.raise_for_status()
        except requests.RequestException as error:
            self.handle_http_error(error, error.response)
        return resp

    def _send(self, method: RESTMethod, endpoint: str, **kwargs):
        uri, timeout = _parse_send_kwargs(self, kwargs)
        uri = "/".join([uri, endpoint or ""])
        return self.__session__.request(
            str(method),
            url=uri, timeout=timeout, **kwargs)


def _parse_send_kwargs(client: BaseAPIClient, kwargs: dict):
    parse = lambda n: kwargs.pop(n, getattr(client, n))
    return parse("root_uri"), parse("max_timeout")


class ClientLibException(BaseException):
    """Raise for errors concerning `clientlib.py`"""


class ClientFieldError(ClientLibException):
    """Raise for errors related to Client fields."""


class ClientValidationError(ClientLibException):
    """Raise for errors during Client validation."""


class ClientResponseError(ClientLibException):
    """Raise if response from sent request is bad."""

    def __init__(self, message, status=500, elapsed=0.0):
        self.elapsed = elapsed
        self.message = message
        self.status  = status

    def __str__(self):
        return f"<[{self.status}]: {self.message} [elapsed: {self.elapsed}s]"


if __name__ == "__main__":

    class GoogleAPI(BaseAPIClient):
        root_uri = "https://www.google.com"
        max_timeout = (10.0, 40.0)


    with GoogleAPI() as client:
        resp = client.send(Method.GET)
        print(resp.headers)
