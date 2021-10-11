from abc import ABCMeta
from typing import final


class BaseClientType(type):
    """
    Base type for subsequent types
    in cachelib.
    """

    _bases:    tuple = ()
    _namespace: dict = {}

    def __new__(cls, name=None):
        inst = type.__new__(cls,
            name or (cls.__name__),
            cls._bases,
            cls._namespace)
        return inst

    def __init__(self, name: str = None):
        pass


@final
class NotSetType(BaseClientType):
    """
    Used to identify a field that
    has never been set.
    """
    pass


@final
class NullType(BaseClientType):
    """
    Used to identify an object that
    is none but not of 'NoneType'.
    """
    pass


@final
class UnknownType(BaseClientType):
    """
    Used to identify an object of
    unknown origin.
    """
    pass


class CacheAgentType(ABCMeta, type):
    """Handles cache calls."""
    pass


NotSet  = NotSetType()
Null    = NullType()
Unknown = UnknownType()
