import asyncio
import re
import time

from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Mapping

from consumerlib.controllers.maps import ListenState
from consumerlib.helpers.maps import EventMap, ClientMap
from consumerlib.helpers.queues import MessageQueue


class BaseControllerMixIn:
    clients_class  = ClientMap
    event_channels = EventMap
    queue_class    = MessageQueue

    _clients: clients_class
    _logger:  Logger
    _queue:   queue_class

    _listen_state = ListenState.CLOSED

    @property
    def logger(self):
        return self._logger

    @property
    def clients(self):
        return self._clients

    @property
    def listen_state(self):
        return self._listen_state

    @property
    def queue(self):
        return self._queue

    def set_listen_state(self, state: str):
        self._listen_state = ListenState[state]

    def listen_state_is(self, state: str):
        return self._listen_state is ListenState[state]


class ControllerInitMixIn(BaseControllerMixIn):

    def __new__(cls, *args, **kwargs):
        return cls._new(args, kwargs)

    @classmethod
    def _new(cls, args, kwargs, init=True):
        inst = object.__new__(cls)
        if init:
            inst._init(*args, **kwargs)
        return inst

    def _init(self, settings: Mapping[str, Any], logger: Logger, *args, **kwargs):
        self._logger  = logger
        self._clients = self._init_clients(settings)
        self._queue   = self._init_queue(settings)
        self.__init__(*args, **kwargs)

    def _init_clients(self, settings):
        inst = object.__new__(self.clients_class)
        inst.__init__(settings, self._logger)
        return inst

    def _init_queue(self, settings):
        inst = object.__new__(self.queue_class)
        inst.__init__(settings.get("QUEUE_MAX_SIZE", 2000))
        return inst


class ControllerABCMixIn(BaseControllerMixIn, ABC):

    def prerun(self, *args, **kwargs):
        """Execute any prerequisite code here."""
        pass

    def postrun(self, *args, **kwargs):
        """Execute any post run/cleanup code here."""
        pass

    @abstractmethod
    def connect(self) -> None:
        """Connect to target hosts."""
        return NotImplemented

    @abstractmethod
    def close(self) -> None:
        """Close connections to target hosts."""
        return NotImplemented

    @abstractmethod
    def refresh(self) -> None:
        """Refresh connections to target hosts."""
        return NotImplemented

    @abstractmethod
    def listen(self) -> None:
        """Listen for events."""
        return NotImplemented


class ControllerHostsMixIn(ControllerABCMixIn, BaseControllerMixIn):

    def _connect(self, *args, **kwargs):
        self._logger.info("connecting to hosts...")
        try:
            self.connect(*args, **kwargs)
        except Exception as failure:
            self._logger.error("failed connecting to hosts:", exc_info=True)
            raise failure

    def _close(self):
        self._logger.info("closing connections from hosts...")
        try:
            self.close()
        except Exception as failure:
            self._logger.error("failed disconnecting from hosts:", exc_info=True)
            raise failure

    def _refresh(self):
        try:
            # may need to implement an event queue
            # then wait for any remaining events to
            # close out before running refresh.
            self.refresh()
        except Exception as failure:
            self._logger.error("failed refreshing host connections.")
            raise failure


class ControllerListenMixIn(ControllerABCMixIn, BaseControllerMixIn):

    def _listen(self):
        if self.listen_state_is("CLOSED"):
            # Should we raise an error here?
            return

        self._logger.info("listening for events...")
        self.listen()

    def _prerun(self, *args, **kwargs):
        self._logger.info("starting consumer...")
        self.prerun()
        self._logger.info("ready to listen for events.")

    def _postrun(self, *args, **kwargs):
        self._logger.info("stopping consumer...")
        self.postrun()
        self._logger.info("consumer no longer in ready state.")


class ControllerQueueWatchMixIn(ControllerABCMixIn, BaseControllerMixIn):

    def handle_event(self, event, message):
        """
        Not implemented here.
        handle an incoming event.
        """
        pass

    def watch_queue(self):
        if self.listen_state_is("REFRESH"):
            time.sleep(1)
            return

        self._active_watch_queue()
        self._passive_watch_queue()

    def _passive_watch_queue(self, wait: float = 1):
        time.sleep(wait)
        self.set_listen_state("LISTENING")

    def _active_watch_queue(self):
        while self.listen_state_is("LISTENING"):
            event, message = self._get_next_message()
            if message is None:
                return

            self.logger.info(f"received message: {message!r}")
            self.handle_event(event, message)

    def _get_next_message(self):
        message = self.queue.pull()
        if message is not None:
            return self._parse_message(message)
        return (None, None)

    def _parse_message(self, message):
        event = re.split(r"^/\w+/", message["channel"])[-1]
        return self.event_channels[event], message


class BaseAsyncControllerMixIn(ControllerABCMixIn, BaseControllerMixIn):
    pass


class AsyncControllerHostsMixIn(BaseAsyncControllerMixIn):

    async def _connect(self, *args, **kwargs):
        self._logger.info("connecting to hosts...")
        try:
            await self.connect(*args, **kwargs)
        except Exception as failure:
            self._logger.error("failed connecting to hosts:", exc_info=True)
            raise failure

    async def _close(self):
        self._logger.info("closing connections from hosts...")
        try:
            await self.close()
        except Exception as failure:
            self._logger.error("failed disconnecting from hosts:", exc_info=True)
            raise failure

    async def _refresh(self):
        try:
            # may need to implement an event queue
            # then wait for any remaining events to
            # close out before running refresh.
            await self.refresh()
        except Exception as failure:
            self._logger.error("failed refreshing host connections.")
            raise failure


class AsyncControllerListenMixIn(BaseAsyncControllerMixIn):

    async def _listen(self):
        if self.listen_state_is("CLOSED"):
            # Should we raise an error here?
            return

        self.logger.info("listening for events...")
        await self.listen()

    async def _prerun(self, *args, **kwargs):
        self._logger.info("starting consumer...")
        await self.prerun()
        self._logger.info("ready to listen for events.")

    async def _postrun(self, *args, **kwargs):
        self._logger.info("stopping consumer...")
        await self.postrun()
        self._logger.info("consumer no longer in ready state.")


class AsyncControllerQueueWatchMixIn(BaseAsyncControllerMixIn):

    async def handle_event(self, event, message):
        """
        Not implemented here.
        handle an incoming event.
        """
        pass

    async def watch_queue(self):
        if self.listen_state_is("REFRESH"):
            await asyncio.sleep(1)
            return

        await self._active_watch_queue()
        await self._passive_watch_queue()

    async def _passive_watch_queue(self, wait: float = 1):
        await asyncio.sleep(wait)
        self.set_listen_state("LISTENING")

    async def _active_watch_queue(self):
        while self.listen_state_is("LISTENING"):
            event, message = await self._get_next_message()

            if message is None:
                return

            await self.handle_event(event, message)

    async def _get_next_message(self):
        message = self.queue.pull()
        if message is not None:
            return await self._parse_message(message)
        return (None, None)

    async def _parse_message(self, message):
        event = re.split(r"^/\w+/", message["channel"])[-1]
        return self.event_channels[event], message
