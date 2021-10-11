from cachelib.mixins import CacheAgentHostsMixIn, CacheAgentInitMixIn,  \
                            CacheAgentTransactionMixIn
from cachelib.typedefs import CacheAgentType


class BaseCacheAgent(
    CacheAgentHostsMixIn,
    CacheAgentInitMixIn,
    CacheAgentTransactionMixIn,
    metaclass=CacheAgentType):
    pass

BaseCacheAgent()
