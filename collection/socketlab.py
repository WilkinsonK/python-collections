import enum
import socket
import warnings

from dataclasses import dataclass
from socket import AddressFamily, SocketKind


def getclass(inst: object):
    return inst.__class__


@dataclass
class SocketAttributes:
    family: AddressFamily = socket.AF_INET
    type:      SocketKind = socket.SOCK_STREAM
    proto:            int = -1
    fileno:           int = None


class SocketStatus(enum.IntEnum):
    OPEN:   int = enum.auto()
    CLOSED: int = enum.auto()


class SocketOpenWarning(Warning):
    """Warn if a socker is never closed"""


class SocketType(type):
    """Socket Interface for defining server/client sockets"""


class BaseSocket(metaclass=SocketType):
    _socket        = socket.socket
    _socket_status = SocketStatus.CLOSED

    def __init__(self, host, port, **attrs):
        self._host  = host
        self._port  = port
        self._attrs = SocketAttributes(**attrs)

    def __repr__(self):
        return (
            f"<{getclass(self).__name__}:"
            f" {self._socket_status.name}>"
        )

    def __del__(self):
        if self._socket_status == SocketStatus.OPEN:
            warnings.warn(
                f"Socket {getclass(self).__name__} was never closed",
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

    def listen(self, backlog: int = 0) -> tuple[socket.socket, str]:
        self._socket.listen(backlog)
        return self._socket.accept()

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

    def send(self, data, *args, **kwargs):
        raise NotImplementedError(
            f"{getclass(self).__name__}.send"
            " was not overriden"
        )

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
