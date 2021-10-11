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
        inst.__init__(settings.get("QUEUE_MAX_SIZE", None))
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
        if self.listen_state is ListenState.CLOSED:
            # Should we raise an error here?
            return

        self.logger.info("listening for events...")
        self.listen()

    def _prerun(self, *args, **kwargs):
        self._logger.info("starting PDF Consumer...")
        self.prerun()
        self._logger.info("ready to listen for events.")

    def _postrun(self, *args, **kwargs):
        self._logger.info("stopping PDF Consumer...")
        self.postrun()
        self._logger.info("consumer no longer in ready state.")
