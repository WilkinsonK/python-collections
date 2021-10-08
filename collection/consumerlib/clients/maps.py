from enum import Enum, auto


class ConnectState(Enum):
    CLOSED  = auto()
    PENDING = auto()
    OPEN    = auto()
