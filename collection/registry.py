"""
registry.py
by: Keenan W. Wilkinson

This module was designed with the `click` package in mind:
https://click.palletsprojects.com/

Use this module to register `click.Command` and `click.Group`
objects from a target module on higher level `click.Group`
objects in your project.
"""

import importlib
import importlib.util

from types import ModuleType
from typing import TypeVar
from typing_extensions import Self

from click import Command, Group


ClickCmd = TypeVar("ClickCmd", Command, Group)


class ModuleCommand:
    __slots__ = ("__cmd", "__module", "__name")

    __cmd:    ClickCmd
    __module: str
    __name:   str

    def __init__(self, cmd: ClickCmd, *,
        module: str = None, name: str =None, **kwds):

        self.__cmd    = cmd
        self.__module = module or cmd.callback.__module__
        self.__name   = name or cmd.name

    @property
    def command(self):
        return self.__cmd

    @property
    def module(self):
        return self.__module

    @property
    def name(self):
        return self.__name


Namespace    = dict[str, ModuleCommand]
RegistryDict = dict[str, Namespace]


class ModuleNamespace(ModuleType):
    __commands__: Namespace

    @staticmethod
    def pre_command_load() -> None:
        """
        Executes prior to commands being loaded.
        """

    @staticmethod
    def post_command_load() -> None:
        """
        Executes after commands have been loaded.
        """


class RegistryMeta(type):
    _registry_: RegistryDict

    def __init__(cls, *args, **kwargs):
        cls._registry_ = {}

    def __str__(cls):
        return f"{cls.__name__}({cls._registry_})"

    def _get_namespace(cls, module_cmd: ModuleCommand) -> Namespace:
        return cls._registry_.get(module_cmd.module, {})

    def _update_namespace(cls, module_cmd: ModuleCommand, namespace: dict):
        cls._registry_[module_cmd.module] = namespace

    @property
    def namespaces(cls):
        return cls._registry_


class Registry(metaclass=RegistryMeta):

    def __new__(cls) -> type[Self]:
        return cls

    @classmethod
    def register(cls, module_cmd: ModuleCommand):
        """Register a module command in this registry."""

        namespace = cls._get_namespace(module_cmd)
        namespace |= {module_cmd.name: module_cmd}

        cls._update_namespace(module_cmd, namespace)

    @classmethod
    def get(cls, module: ModuleNamespace | ModuleType | str):
        """Get a registered `Namespace` from this registry."""

        if isinstance(module, (ModuleNamespace, ModuleType)):
            module = module.__name__
        return cls.namespaces.get(module, {})


def module_command(cmd: ClickCmd = None, *,
        module: str = None, name: str = None, registry: Registry = None):
    """
    Register a `Command` or `Group` to it's
    parent module or target namespace.

    params:
    `module`: name of the module path.

    `name`: name designated to the command object.

    `registry`: designated Registry singleton commands
    are registered to.
    """

    registry = registry or Registry

    def inner(cmd: ClickCmd):
        registry.register(
            ModuleCommand(cmd, module=module, name=name))
        return cmd

    if not cmd:
        return inner
    return inner(cmd)


def load_namespace(module: str, *,
        package: str = None, registry: Registry = None) -> ModuleNamespace:
    """
    Imports a module as a `ModuleNamespace`
    allowing that we can expect specific hooks
    to be available, even if they were not defined
    in the module itself.
    """

    module   = ".".join([i for i in (package, module) if i])
    registry = registry or Registry

    mod = importlib.import_module(module)

    body = {}
    for base in (ModuleNamespace, mod):
        body.update(base.__dict__)

    new_mod = type("NewNamespace", (ModuleNamespace, ModuleType), body)
    new_mod.__name__ = mod.__name__
    new_mod.__commands__ = registry.get(mod)

    return new_mod


def register_namespace(module: str, *,
        package: str = None, registry: Registry = None, **kwds):
    """
    Create a wrapper which registers commands
    from the target namespace on to the decorated
    `Group` or `Command`.
    """

    namespace = load_namespace(module,
        package=package, registry=registry)

    def wrapper(cmd: ClickCmd):
        namespace.pre_command_load()

        for _, command in namespace.__commands__.items():
            cmd.add_command(command.command)

        namespace.post_command_load()
        return cmd

    return wrapper
