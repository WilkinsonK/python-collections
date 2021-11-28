import hashlib
import json
import re

from dataclasses import dataclass
from pathlib import Path

import cffi


# base locations
CLIBS_ROOT    = Path(__file__).parent
BIN_LOCATION  = CLIBS_ROOT / "bin"
DATA_LOCATION = CLIBS_ROOT / "data"
LIB_LOCATION  = CLIBS_ROOT / "lib"

# tags
TAG_START_BODY = re.compile(r"\/\/ START_BODY", flags=re.M)


class _Singleton:
    _inst = None

    def __new__(cls, *args, **kwargs):
        if not cls._inst:
            cls._inst = cls._new(args, kwargs)
        return cls._inst

    @classmethod
    def _new(cls, args, kwargs):
        inst = object.__new__(cls)
        inst._init(*args, **kwargs)
        return inst

    def _init(self, *args, **kwargs):
        self.__init__(*args, **kwargs)


class Cache(_Singleton):
    _cache_location = DATA_LOCATION / "cache.json"

    def _init(self, *args, **kwargs):
        self._init_cachefile()
        self.__init__(*args, **kwargs)

    def _init_cachefile(self):
        if self._cache_location.exists():
            return
        with open(self._cache_location, "w") as fp:
            fp.write(r"{}")

    def _read_cachefile(self, handler=lambda d: d) -> dict:
        with open(self._cache_location, "r") as fp:
            return handler(json.load(fp))

    def _write_cachefile(self, data: dict):
        with open(self._cache_location, "w") as fp:
            json.dump(data, fp)

    def _get_filehash(self, filename: str):
        with open(LIB_LOCATION / filename, "rb") as fp:
            _hash = hashlib.sha256(fp.read())
        return _hash.hexdigest()

    def file_cached(self, filename: str):
        def _inner(cache: dict):
            if filename not in cache:
                return False
            return self._get_filehash(filename) == cache[filename]
        return self._read_cachefile(_inner)

    def cache_file(self, filename: str):
        def _inner(cache: dict):
            cache.update({
                filename: self._get_filehash(filename)
            })
            return cache
        self._write_cachefile(self._read_cachefile(_inner))


@dataclass
class CFile:
    basename: str
    body:     str
    module:   str
    head:     str  = None
    cached:   bool = False

    @classmethod
    def read_cfile(cls, filename: str):
        head, body = None, (LIB_LOCATION / filename).read_text()
        if re.findall(TAG_START_BODY, body):
            head, body = re.split(TAG_START_BODY, body)
        return head, body

    @classmethod
    def parse_module(cls, filename: str):
        filename = re.sub(r"\.[chso]", "", filename)
        return f"_{filename}"

    @classmethod
    def from_filename(cls, filename: str):
        head, body = cls.read_cfile(filename)
        module     = cls.parse_module(filename)
        cached     = Cache().file_cached(filename)
        return cls(filename, body, module, head, cached)


class Builder:
    _builder_cls       = cffi.FFI
    _manifest_location = DATA_LOCATION / "manifest.json"

    @classmethod
    def _read_manifest(cls):
        with open(cls._manifest_location, "r") as fp:
            return json.load(fp)

    @classmethod
    def _build_file(cls, filename: str):
        cfile  = CFile.from_filename(filename)
        builder = cls._builder_cls()

        if cfile.cached:
            return
        cls._compile_file(builder, cfile)
        Cache().cache_file(cfile.basename)

    @classmethod
    def _compile_file(cls, builder: _builder_cls, cfile: CFile):
        cls._set_source(builder, cfile)
        builder.cdef(cfile.body)
        builder.compile(BIN_LOCATION / cfile.module)

    @staticmethod
    def _set_source(builder: _builder_cls, cfile: CFile):
        params = {"source": cfile.body, "module_name": cfile.module}
        if cfile.head:
            params["source"] = cfile.head
        builder.set_source(**params)

    @classmethod
    def build_modules(cls):
        for source in cls._read_manifest():
            cls._build_file(source)


if __name__ == "__main__":
    Builder.build_modules()
