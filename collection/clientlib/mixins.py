from os import PathLike
from typing import Any, Mapping, Tuple, Union

from clientlib.enums import ApplyBehavior, AttrDefault
from clientlib.errors import RequiredAttributeError
from clientlib.types import ConnectionTimeout, ReadTimeout, \
                            NotSet, Session


class BaseClientMixIn(object):

    # Client specific attributes
    healthcheck_url:                                             str = NotSet
    root_url:                                                    str = NotSet
    max_timeout: Union[float, Tuple[ConnectionTimeout, ReadTimeout]] = NotSet

    # Internal session specific attributes
    headers:        Mapping[str, Any]
    proxies:        Mapping[str, str]
    hooks:          Mapping[str, str]
    auth:                         str
    stream:                      bool
    verify:                      bool
    cert: Union[str, bytes, PathLike]

    _session: Session
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
        cls._validate()
        inst = cls._make_new(args, kwargs)
        return inst

    @classmethod
    def _make_new(cls, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(*args, **kwargs)
        return inst

    @classmethod
    def _validate(cls):
        """
        Not implemented here.
        Perform pre-initialization validation.
        """
        pass

    def _init(self, *args, **kwargs):
        """
        Not implemented here.
        Perform initialization on an instance.
        """
        pass


class ClientValidationMixIn(BaseClientMixIn):

    @classmethod
    def _validate(cls):
        cls._validate_required_attrs()

    @classmethod
    def _validate_required_attrs(cls):
        for attr in cls._required_attrs:
            cls._validate_required_attr(attr)

    @classmethod
    def _validate_required_attr(cls, attr):
        if getattr(cls, attr, NotSet) is NotSet:
            raise RequiredAttributeError(
                f"expected {attr!r} of {cls.__name__!r} to have "
                f"a defined value, not {NotSet.__name__!r}")


class ClientInitMixIn(BaseClientMixIn):

    def _init(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        self._init_session()

    def _init_session(self, **kwargs):
        ss = Session()
        for attr in self._session_attr_defaults:
            value = getattr(self, attr.name, None)
            attr.apply(ss, kwargs.get(attr.name, value))
        self._session = ss
