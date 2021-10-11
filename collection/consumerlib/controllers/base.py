import asyncio
import re
import time

from consumerlib.controllers.maps import ListenState
from consumerlib.controllers.mixins import ControllerInitMixIn,        \
                     ControllerHostsMixIn, ControllerListenMixIn
from consumerlib.helpers.aioevents import execute_async_task


class BaseController(ControllerInitMixIn, ControllerHostsMixIn, ControllerListenMixIn):
    """
    Basic controls/functionality needed to define a controller
    class.
    """

    def start(self):
        self._prerun()
        self._listen()

    def stop(self):
        self._postrun()

    def prerun(self):
        self._connect()
        self._listen_state = ListenState.READY

    def postrun(self):
        self._close()
        self._listen_state = ListenState.CLOSED

    def refresh(self):
        self._listen_state = ListenState.REFRESH
        self.close()
        self.connect()
        self._listen_state = ListenState.READY
