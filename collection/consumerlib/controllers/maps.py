from enum import Enum, auto


class ListenState(Enum):
    CLOSED    = auto()
    REFRESH   = auto()
    READY     = auto()
    LISTENING = auto()
