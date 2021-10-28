from abc import ABC
from datetime import timedelta
from typing import Any, Union

from cachelib.mixins import CacheAgentHostsMixIn, CacheAgentInitMixIn,  \
                            CacheAgentTransactionMixIn
from cachelib.signatures import Signature
from cachelib.typedefs import CacheAgentType, Unknown


class BaseCacheAgent(
    CacheAgentHostsMixIn, CacheAgentInitMixIn,
    CacheAgentTransactionMixIn, metaclass=CacheAgentType):
    """
    Basic caching broker.
    Use this class to define CacheAgent objects
    per your choice of mapping.
    """

    def precall_lookup(self, func):

        def inner(*args, **kwargs):
            result = self.pull(func, *args, **kwargs)
            if result is not Unknown:
                return result
            sig = self.push(func, *args, **kwargs)
            return sig

        return inner


class RedisCacheAgent(BaseCacheAgent):
    max_ttl: Union[int, timedelta] = None

    def _push(self, signature: Signature):
        key    = str(signature)
        result = self.serializer.dumps(signature())
        self.connection.set(key, result, ex=self.max_ttl)

    def _pull(self, signature: Signature, default: Any):
        key = str(signature)
        result = self.connection.get(key)

        if result:
            return self.serializer.loads(result)
        return default
