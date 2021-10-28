from dataclasses import dataclass, field
from inspect import FullArgSpec, getcallargs, getfullargspec
from types import ModuleType
from typing import Any, Callable, Dict

from cachelib.typedefs import Null


@dataclass(order=True)
class BaseSignature:
    callable:    Callable    = field(repr=False)
    callname:            str = field(init=False)
    module:       ModuleType = field(init=False)
    argspec:     FullArgSpec = field(init=False, repr=False)
    callargs: Dict[str, Any] = field(init=False, default_factory=dict)

    def __init__(self, callable: Callable, *args, **kwargs):
        self.callable = callable
        self.module   = callable.__module__
        self.argspec  = getfullargspec(callable)
        self._set_callargs(*args, **kwargs)
        self._set_callname()

    def __call__(self):
        args   = self.callargs.get("args", ())
        kwargs = self.callargs.get("kwargs", {})
        return self.callable(*args, **kwargs)

    def _set_callargs(self, *args, **kwargs):
        """
        Not implemented here.
        Set the signature callargs.
        """
        pass

    def _set_callname(self):
        """
        Not implemented here.
        Set the signature callname.
        """
        pass


class Signature(BaseSignature):

    def _set_callargs(self, *args, **kwargs):
        callargs = self._get_callargs(*args, **kwargs)
        self.callargs = self._parse_callargs(callargs)

    def _get_callargs(self, *args, **kwargs):
        if [args, kwargs] == [(), {}]:
            return {}
        return getcallargs(self.callable, *args, **kwargs)

    def _parse_callargs(self, callargs: Dict[str, Any]):
        for inst in ("cls", "self"):
            parent = callargs.get(inst, Null)
            if parent is Null:
                continue
            callargs.update({inst: parent.__class__})
        return callargs

    def _set_callname(self):
        callname = self._get_signature_name()
        self.callname = callname

    def _get_signature_name(self):
        parent = self._get_parent_name()
        if parent:
            return ".".join([parent, self.callable.__name__])
        return self.callable.__name__

    def _get_parent_name(self):
        for inst in ("cls", "self"):
            parent = self.callargs.get(inst, Null)
            if parent is not Null:
                return parent.__name__
