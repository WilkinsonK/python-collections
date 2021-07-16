import enum
import functools
import socket
import warnings

from dataclasses import dataclass
from socket import AddressFamily, SocketKind


def getclass(inst: object):
    return inst.__class__


def not_implemented(func):

    @functools.wraps(func)
    def inner(*args, **kwargs):
        raise NotImplementedError(f"{func.__qualname__} was not overriden")

    return inner


class SocketDataClass:
    __dataclass_fields__ = dict()

    def asiterable(self):
        iterable = dict()
        for key in self.__dataclass_fields__.keys():
            iterable.update({key: getattr(self, key)})
        return iterable


@dataclass
class SocketAttributes(SocketDataClass):
    family: AddressFamily = socket.AF_INET
    type:      SocketKind = socket.SOCK_STREAM
    proto:            int = -1
    fileno:           int = None


@dataclass
class SocketConnection(SocketDataClass):
    connection: socket.socket
    retaddress: str


class SocketStatus(enum.IntEnum):
    OPEN:   int = enum.auto()
    CLOSED: int = enum.auto()


class SocketOpenWarning(Warning):
    """Warn if a socker is never closed."""


class SocketType(type):
    """Socket Interface for defining server/client sockets."""


class BaseSocket(metaclass=SocketType):
    _socket        = socket.socket
    _socket_status = SocketStatus.CLOSED

    def __init__(self, host: str, port: int, **attrs):
        """Init a SocketType object."""
        self._host  = host
        self._port  = port
        self._attrs = SocketAttributes(**attrs).asiterable()

    def __repr__(self):
        return (
            f"<{getclass(self).__name__}: "
            f"port={self._port!r}, "
            f"host={self._host!r}, "
            f"status={self._socket_status.name}>"
        )

    def __del__(self):
        if self._socket_status == SocketStatus.OPEN:
            warnings.warn(
                f"SocketType {getclass(self).__name__!r} was never closed",
                SocketOpenWarning
            )

    @property
    def socket(self):
        return self._socket

    @property
    def status(self):
        return self._socket_status


class BaseServerSocket(BaseSocket):

    def open(self):
        self.__open__()

    def close(self):
        self.__close__()

    def listen(self, backlog: int = 0):
        self._socket.listen(backlog)
        return SocketConnection(*self._socket.accept())

    def __open__(self):
        self._socket = self._socket(**self._attrs)
        self._socket.bind((self._host, self._port))
        self._socket_status = SocketStatus.OPEN

    def __close__(self):
        self._socket.close()
        self._socket        = getclass(self)._socket
        self._socket_status = getclass(self)._socket_status

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, etype, eval, tback):
        self.close()


class BaseClientSocket(BaseSocket):

    def connect(self):
        self.__connect__()

    def detach(self):
        self.__detach__()

    @not_implemented
    def send(self, data, *args, **kwargs):
        return NotImplemented

    def __connect__(self):
        self._socket = self._socket(**self._attrs)
        self._socket.connect((self._host, self._port))
        self._socket_status = SocketStatus.OPEN

    def __detach__(self):
        self._socket.detach()
        self._socket        = getclass(self)._socket
        self._socket_status = getclass(self)._socket_status

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, etype, eval, tback):
        self.detach()


class ServerSocket(BaseServerSocket):
    """
    SocketType object intended for opening
    listening ports.
    """


class ClientSocket(BaseClientSocket):
    """
    SocketType object intended for sending
    data to listening ports.
    """
