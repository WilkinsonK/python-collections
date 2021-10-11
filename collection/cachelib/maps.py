from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, List, Tuple


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
        return [k for k in dir(cls) if "__" not in k[:2]]


@dataclass
class Parameter:
    name: str
    type: type = object
    validator: Callable = lambda p: None

    def validate(self, value):
        self.validator(value)


class ParamMapMeta(NoDundersMapMeta):

    def items(cls) -> List[Tuple[str, Parameter]]:
        return super().items()

    def __getitem__(cls, name) -> Parameter:
        return super().__getitem__(name)


class ParamMap(metaclass=ParamMapMeta):
    """Config to parameter relationship mapping."""
    pass


class ConnectState(Enum):
    OPEN   = auto()
    CLOSED = auto()
