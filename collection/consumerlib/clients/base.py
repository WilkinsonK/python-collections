from consumerlib.clients.mixins import                             \
                ClientDatabaseMixIn, ClientHostMixIn, ClientInitMixin, ClientContextMixIn
from consumerlib.helpers.typedefs import ClientType


class BaseClient(ClientInitMixin, ClientHostMixIn, metaclass=ClientType):

    def connect(self):
        try:
            self._connect()
        except Exception as failure:
            class_name = (self.__class__).__name__
            self._logger.error(f"failed connecting to host {class_name}:", exc_info=True)
            raise failure

    def close(self):
        try:
            self._close()
        except Exception as failure:
            class_name = (self.__class__).__name__
            self._logger.error(f"failed disconnection from {class_name}:", exc_info=True)
            raise failure


class BaseDatabaseClient(BaseClient, ClientDatabaseMixIn, ClientContextMixIn):
    """Use this class to create a DAO client."""
    pass
