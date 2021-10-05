import functools

from abc import ABC, abstractmethod

from clientlib.enums import Method
from clientlib.errors import HTTPError
from clientlib.mixins import ClientInitMixIn, ClientValidationMixIn
from clientlib.types import Response, Session


def not_implemented(method):
    """
    Raise a not implemented error if method
    returns 'NotImplemented' type.
    """

    message = f"method {method!r} has not been implemented yet!"

    @functools.wraps(method)
    def inner(*args, **kwargs):
        if method(*args, **kwargs) is NotImplemented:
            raise NotImplementedError(message)

    return inner


class BaseClient(ClientInitMixIn, ClientValidationMixIn, ABC):

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.healthcheck()

    def _send(self, method, endpoint, **kwargs):
        root_url, timeout, kwargs = self._parse_send_kwargs(**kwargs)
        method, address = self._parse_send_args(method, root_url, endpoint)
        return self.session.request(
            method, url=address, timeout=timeout, **kwargs)

    def _parse_send_address(self, root_url, endpoint):
        address = "/".join([root_url, endpoint or ""])
        return address

    def _parse_send_args(self, method, root_url, endpoint):
        address = self._parse_send_address(root_url, endpoint)
        method  = self._parse_send_method(method)
        return method, address

    def _parse_send_kwargs(self, **kwargs):
        timeout  = kwargs.pop("max_timeout", self.max_timeout)
        root_url = kwargs.pop("root_url", self.root_url)
        return root_url, timeout, kwargs

    def _parse_send_method(self, method):
        if method.__class__ in (str, Method):
            return str(method)
        return NotImplemented

    @property
    def session(self) -> Session:
        return self._session

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    @abstractmethod
    @not_implemented
    def handle_http_error(self, error: HTTPError, resp: Response = None) -> None:
        """
        Not implemented here.
        Handle http protocol errors.
        """
        return NotImplemented

    @abstractmethod
    @not_implemented
    def healthcheck(self) -> int:
        """
        Not implemented here.
        Send a health check ping to api reference.
        """
        return NotImplemented

    @abstractmethod
    @not_implemented
    def refresh(self, **kwargs) -> None:
        """
        Not implemented here.
        Reset the client session.
        """
        return NotImplemented

    @abstractmethod
    @not_implemented
    def send(self, method: Method, endpoint: str = None, data: dict = None, **kwargs) -> Response:
        """
        Not implemented here.
        Send a request using the ApiClient settings.
        """
        return NotImplemented
