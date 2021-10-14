import asyncio

from typing import Any, Callable, Coroutine, Mapping, Union

from consumerlib.controllers.maps import ListenState
from consumerlib.controllers.mixins import                             \
                    ControllerABCMixIn, ControllerInitMixIn,        \
                    ControllerHostsMixIn, ControllerListenMixIn,    \
                    ControllerQueueWatchMixIn,                      \
                    AsyncControllerHostsMixIn,                      \
                    AsyncControllerListenMixIn, AsyncControllerQueueWatchMixIn


class AsyncBaseController(
    AsyncControllerHostsMixIn, AsyncControllerListenMixIn,
    AsyncControllerQueueWatchMixIn):
    pass


class BaseController(
    ControllerHostsMixIn, ControllerListenMixIn,
    ControllerQueueWatchMixIn):
    pass


class Controller(ControllerInitMixIn, BaseController):
    """
    Basic controls/functionality needed to define a controller
    class.
    """

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def start(self):
        self._prerun()
        self._listen()

    def stop(self):
        self._postrun()

    def prerun(self):
        self._connect()
        self.set_listen_state("READY")

    def postrun(self):
        self._close()
        self.set_listen_state("CLOSED")

    def refresh(self):
        self.set_listen_state("REFRESH")
        self.close()
        self.connect()
        self.set_listen_state("READY")

    def listen(self):
        while not self.listen_state_is("CLOSED"):
            self._watch_queue()


class AsyncController(ControllerInitMixIn, AsyncBaseController):
    """
    Basic controls/functionality needed to define a controller
    class.
    """

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def start(self):
        await self._prerun()
        await self._listen()

    async def stop(self):
        await self._postrun()

    async def prerun(self):
        await self._connect()
        self.set_listen_state("READY")

    async def postrun(self):
        await self._close()
        self.set_listen_state("CLOSED")

    async def refresh(self):
        self.set_listen_state("REFRESH")
        while not self.listen_state_is("REFRESH"):
            await asyncio.sleep(1)
        await self.postrun()
        await self.prerun()
        self.set_listen_state("READY")

    async def listen(self) -> None:
        while not self.listen_state_is("CLOSED"):
            await self.watch_queue()
