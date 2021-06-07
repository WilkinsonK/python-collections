import functools
import inspect
import pickle

from typing import Any

import redis


__all__ = ("CacheAgent",)

Unknown = type("Unknown", (int, ), {})
Null    = type("Null", (int, ), {})


def compose_key(func, *args, **kwargs):
    """
    From a function and the arguments passed
    into it, create an identification id that
    is unique, but not so unique that it's
    likelyhood of being called is too low.
    """

    key = dict(called=func.__qualname__, params=clean_argset(func, *args, **kwargs))
    return str(key)


def clean_argset(func, *args, **kwargs):
    """
    Clean a set of parameters so that it
    can be used more flexibly/to the
    needs of the CacheAgent.
    """

    argset = inspect.getcallargs(func, *args, **kwargs)
    for inst in ("cls", "self"):
        argset.pop(inst, Null)
    return argset


class CacheAgent:
    """
    Redis connection instance for creating cache calls
    to a specified instance.
    """

    connected:      bool
    connection          = redis.Redis
    serializer          = pickle
    redis_host:     str = Unknown
    redis_name:     str = Unknown
    redis_port:     int = Unknown
    max_ttl:        int = 300

    def precall_lookup(self, func):
        """
        Prior to execution of the wrapped function,
        perform a lookup on the connected Redis
        instance. If the result is not `unknown`
        return that result instead.
        """

        @functools.wraps(func)
        def inner(*args, **kwargs):
            key = compose_key(func, *args, **kwargs)
            if (result := self[key]) is Unknown:
                result = func(*args, **kwargs)
                self[key] = result
            return result

        return inner

    def __init__(self, name: str = Null, redis_conf: dict = {}, max_ttl: int = Null):
        """
        Initialize a new connection to the desired
        Redis host for making caching calls.
        """

        self.redis_name = name if name != Null else f"cache-agent@{id(self)}"
        self.max_ttl    = max_ttl if max_ttl != Null else self.max_ttl

        for k, v in redis_conf.items():
            if v in ("password", "pass"):
                continue
            setattr(self, f"redis_{k}", v)

        try:
            self.connection = self.connection(
                **redis_conf, client_name=self.redis_name
            )
            self.connected = True
        except:
            self.connected = False

    def get(self, key: str, default: Any = Unknown):
        """
        Direct implementation of the CacheAgent
        `__getitem__` method.
        """
        return self.__getitem__(key) if not Unknown else default

    def __getitem__(self, key):
        ret_val = self.connection.get(key, Unknown)
        return self.serializer.loads(ret_val) if not Unknown else Unknown

    def set(self, key: str, value: Any):
        """
        Direct implementation of the CacheAgent
        `__setitem__` method.
        """
        return self.__setitem__(key, value)

    def __setitem__(self, key, value):
        value = self.serializer.dumps(value)
        self.connection.set(key, value, ex=self.max_ttl)
        return key, value



if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv("../assets/.env")

    config = {
        "host": os.getenv("REDIS_HOST"),
        "port": os.getenv("REDIS_PORT"),
        "password": os.getenv("REDIS_PASS")
    }
    agent = CacheAgent("TestAgent", config)
    print(agent.connected)