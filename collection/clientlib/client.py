from clientlib.base import BaseClient
from clientlib.enums import Method
from clientlib.errors import BadResponseError, HTTPError, RequestException
from clientlib.types import NotSet, Response


class ApiClient(BaseClient):
    """
    Access object for interaction with an external API.
    """

    def handle_http_error(self, error: HTTPError, resp: Response = None) -> None:
        """Handle http protocol errors."""
        args = (error,)
        if resp is not None:
            args = (*args, resp.status_code, resp.elapsed.total_seconds())
        raise BadResponseError(*args)

    def healthcheck(self) -> int:
        """Send a health check ping to api reference."""
        target_url = self.root_url
        if self.healthcheck_url is not NotSet:
            target_url = self.healthcheck_url
        resp = self._send(Method.GET, "", root_url=target_url)
        return resp.status_code

    def refresh(self, **kwargs) -> None:
        """Reset the client session."""
        self.session.close()
        self._init_session(**kwargs)

    def send(self, method: Method, endpoint: str = None, data: dict = None, **kwargs) -> Response:
        """Send a request using the ApiClient settings."""
        try:
            resp = self._send(method, endpoint, data=data, **kwargs)
            resp.raise_for_status()
        except RequestException as error:
            self.handle_http_error(error, error.response)
        return resp
