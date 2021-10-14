from abc import ABCMeta


class ClientType(ABCMeta, type):
    """Client representational access object."""

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    @property
    def status(self) -> str:
        pass
