from dataclasses import dataclass
from enum import Enum
from typing import Any

from clientlib.typedefs import Session


class ApplyBehavior(Enum):
    """Define how an attribute is set on an object."""
    REPLACE = lambda obj, key, value: setattr(obj, key, value)
    UPDATE  = lambda obj, key, value: getattr(obj, key).update(value)
    APPEND  = lambda obj, key, value: getattr(obj, key).append(value)
    PREPEND = lambda obj, key, value: getattr(obj, key).insert(0, value)


class Method(str, Enum):
    CONNECT = "connect"
    DELETE  = "delete"
    GET     = "get"
    HEAD    = "head"
    OPTIONS = "options"
    PATCH   = "patch"
    POST    = "post"
    PUT     = "put"
    TRACE   = "trace"

    def __str__(self):
        return self.value


@dataclass
class AttrDefault:
    name:  str
    value: Any
    behavior: ApplyBehavior = ApplyBehavior.REPLACE

    def apply(self, session: Session, value: Any):
        """Apply the assigned attribute to the session."""
        self.behavior(session, self.name, value or self.value)
