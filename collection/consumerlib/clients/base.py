from consumerlib.clients.maps import ConnectState
from consumerlib.clients.mixins import                             \
                ClientDatabaseMixIn, ClientInitMixin, ClientContextMixIn
from consumerlib.helpers.typedefs import ClientType


class BaseClient(ClientInitMixin, metaclass=ClientType):

    def _connect(self):
        self._connect_state = ConnectState.PENDING
        try:
            self._connection = self.connectable(**self._connect_params)
            self._connect_state = ConnectState.OPEN
        except:
            self._connect_state = ConnectState.CLOSED
            raise

    def _close(self):
        try:
            self._connection.close()
        except:
            raise
        finally:
            self._connect_state = ConnectState.CLOSED


class BaseDatabaseClient(BaseClient, ClientDatabaseMixIn, ClientContextMixIn):
    """Use this class to create a DAO client."""
    pass
