import contextlib
import pathlib
from typing import IO, Iterable, Protocol

import yaml

from setuptools import setup, find_packages


PROJECT_ROOT = pathlib.Path(__file__).parents[2]

BUILD_FILES = (
    PROJECT_ROOT / "build.yaml",
)
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"


class DataLoader(Protocol):

    @staticmethod
    def __call__(stream: IO, data: Iterable) -> Iterable:
        """Load data from a list of `IO` objects."""


def read_file_data(data: Iterable, files: list[IO], data_loader: DataLoader):
    for file in files:
        data = data_loader(file, data)
    return data


def read_build_file():

    def loader(stream: IO, data: dict):
        data.update(yaml.load(stream, yaml.FullLoader))
        return data

    with contextlib.ExitStack() as es:
        files = [
            es.enter_context(open(loc)) for loc in BUILD_FILES]
        data = read_file_data({}, files, loader)

    return data


def read_requirements_file():

    def loader(stream: IO, data: list):
        data.extend(stream.readlines())
        return data

    with contextlib.ExitStack() as es:
        files = [es.enter_context(open(REQUIREMENTS_FILE))]
        data = read_file_data([], files, loader)

    return "\n".join(set(data))


SETUP_MANIFEST = {}
SETUP_BUILD    = {}


def install():
    global SETUP_MANIFEST
    global SETUP_BUILD

    manifest = read_build_file()
    SETUP_MANIFEST |= manifest["project"]

    SETUP_BUILD |= manifest["project_build"]
    SETUP_BUILD["install_requires"] = read_requirements_file()
    SETUP_BUILD["packages"] = find_packages()

    SETUP_MANIFEST |= SETUP_BUILD

    setup(**SETUP_MANIFEST)


if __name__ == "__main__":
    install()
