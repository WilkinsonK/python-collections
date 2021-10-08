from requests import Session, Response


class _BaseClientType(type):
    """
    Base type for subsequent types
    in clientlib.
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


class _NotSetType(_BaseClientType):
    """
    Used to identify a field that
    has never been set.
    """
    pass


class _TimeoutType(_BaseClientType):
    """
    Representational type of float
    to determine timeout limits in seconds.
    """

    _bases = (float,)


NotSet            = _NotSetType()
ConnectionTimeout = _TimeoutType("ConnectionTimeout")
ReadTimeout       = _TimeoutType("ReadTimeout")
