from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field as dc_field
from logging import Logger
from typing import Any, Callable, Coroutine, List, Mapping, Tuple, Union

from consumerlib.helpers.typedefs import ClientType


class BaseMapMeta(ABC, type):

    @abstractmethod
    def keys(cls) -> List[str]:
        return NotImplemented

    def items(cls) -> List[Tuple[str, Any]]:
        items = []
        for key in cls.keys():
            item = (key, cls[key])
            items.append(item)
        return items

    def __iter__(cls):
        return iter(cls.keys())

    def __getitem__(cls, name):
        if name not in cls.keys():
            raise AttributeError(f"{cls.__name__} has no attribute {name!r}")
        return getattr(cls, name)

    def __contains__(cls, name):
        return name in cls.keys()


class NoDundersMapMeta(BaseMapMeta, ABCMeta):

    def keys(cls):
        return [k for k in dir(cls) if "_" not in k[:2]]


class EventMapMeta(NoDundersMapMeta):

    def __getitem__(cls, name) -> Union[Coroutine, Callable]:
        return super().__getitem__(name)


class FetchMapMeta(NoDundersMapMeta):

    def __getitem__(cls, name) -> Callable:
        return super().__getitem__(name)


@dataclass
class Parameter:
    name:              str
    type_factory: Callable = dc_field(repr=False, default=lambda p: p)
    validator:    Callable = dc_field(repr=False, default=lambda p: None)

    _value: Any = dc_field(repr=False, init=False, default=None)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.type_factory(value)

    def validate(self, value):
        """Validates the value passed in to the function."""
        tmp = self.type_factory(value)
        self.validator(tmp)

    def validate_and_set(self, value):
        """Validates and sets the passed value."""
        self.validate(value)
        self.value = value


class ParamMapMeta(NoDundersMapMeta):

    def items(cls) -> List[Tuple[str, Parameter]]:
        return super().items()

    def __getitem__(cls, name) -> Parameter:
        return super().__getitem__(name)


class BaseClientMap(ABC):
    _client_member_classes = {}

    def keys(self):
        return [k for k in self._client_member_classes.keys()]

    def __init__(self, settings: Mapping[str, Any], logger: Logger = None):
        self._set_client_member_classes()
        self._set_client_members(settings, logger)

    def _set_client_members(self, settings, logger):
        for name, member_class in self._client_member_classes.items():
            client = member_class(settings, logger)
            setattr(self, name, client)

    def _set_client_member_classes(self):
        for name in dir(self):
            if "__" in name[:2]:
                continue

            value = getattr(self, name)
            if type(value) is not ClientType:
                continue
            self._client_member_classes[name] = value

    def __getitem__(self, name) -> ClientType:
        if name not in self.keys():
            class_name = (self.__class__).__name__
            raise AttributeError(f"{class_name} has no attribute {name!r}")
        return getattr(self, name)

    def __contains__(self, name):
        return name in self.keys()


class BaseFetchMap(Callable[..., Any], metaclass=FetchMapMeta):

    def __init__(self, func: Callable[..., Any]):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class ClientMap(BaseClientMap):
    """Client name to host relationship mapping."""
    pass


class EventMap(metaclass=EventMapMeta):
    """Event to procedure relationship mapping."""
    pass


class FetchMap(BaseFetchMap):
    """Cursor fetch methods mapping."""
    NONE = lambda curs: None
    ONE  = lambda curs: curs.fetchone()
    ALL  = lambda curs: curs.fetchall()


class ParamMap(metaclass=ParamMapMeta):
    """Config to parameter relationship mapping."""
    pass
