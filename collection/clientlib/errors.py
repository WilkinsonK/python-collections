from requests import HTTPError, RequestException


class ApiClientError(Exception):
    """Raise on errors related to the ApiClient."""

class BadResponseError(ApiClientError):
    """Raise if response from sent request is bad."""

    def __init__(self, message, status=500, elapsed=0.0):
        self.elapsed  = elapsed
        self.message  = message
        self.status   = status
        super(BadResponseError, self).__init__()

    def __str__(self):
        return f"<[{self.status}]: {self.message} [elapsed: {self.elapsed}s]"

class RequiredAttributeError(ApiClientError):
    """Raise if a required attribute is either missing or invalid."""
