import asyncio
import re
import time

from consumerlib.controllers.maps import ListenState
from consumerlib.controllers.mixins import                          \
                    ControllerInitMixIn, ControllerHostsMixIn,      \
                    ControllerListenMixIn
from consumerlib.helpers.aioevents import execute_async_task


class BaseController(ControllerInitMixIn, ControllerHostsMixIn, ControllerListenMixIn):
    """
    Basic controls/functionality needed to define a controller
    class.
    """

    def _prerun(self):
        self.connect()
        self._listen_state = ListenState.READY

    def _postrun(self):
        self.close()
        self._listen_state = ListenState.CLOSED

    def _refresh(self):
        self._listen_state = ListenState.REFRESH
        self._close()
        self._connect()
        self._listen_state = ListenState.READY

    def _listen(self):
        self._watch_queue()

    def _watch_queue(self):
        while self.listen_state is not ListenState.CLOSED:
            if self.listen_state is ListenState.REFRESH:
                time.sleep(1)
                continue

            self._active_watch_queue()
            self._passive_watch_queue()

    def _passive_watch_queue(self):
        time.sleep(1)
        self._listen_state = ListenState.LISTENING

    def _active_watch_queue(self):
        while self.listen_state is ListenState.LISTENING:
            event, message = self._get_next_message()
            if message is None:
                self._passive_watch_queue()
                continue

            self.logger.info(f"received message: {message!r}")
            self._schedule_event(event, message)

    def _get_next_message(self):
        message = self.queue.pull()
        if message is not None:
            return self._parse_message(message)
        return (None, None)

    def _parse_message(self, message):
        event = re.split(r"^/\w+/", message["channel"])[-1]
        return self.event_channels[event], message

    def _schedule_event(self, event, message):
        try:
            execute_async_task(self._execute_event(event, message))
            self.logger.info(f"completed task: {event}")
        except Exception as failure:
            self.logger.error("error executing task:", exc_info=True)
            raise

    async def _execute_event(self, event, message):
        loop   = asyncio.get_running_loop()
        handle = execute_async_task(event(message), loop=loop)
        try:
            result = await handle
            self.clients.novasys.log_salesforce_message(message)
            return result
        finally:
            handle.cancel()
