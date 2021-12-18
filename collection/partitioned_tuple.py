import itertools
import math

from dataclasses import dataclass
from typing import Iterable

from clibs import _cmath


@dataclass(init=True)
class Dimensions:
    count:    int
    capacity: int

    @classmethod
    def from_iter(cls, arr: Iterable, bias: float = 0.4):
        return cls(len(arr), bias)

    def __init__(self, size: int, bias: float):
        size            = _buffer_size(size)
        count, capacity = _dimensions(size, bias)
        self._set_values(count, capacity)

    def _set_values(self, count, capacity):
        self.count      = count
        self.capacity   = capacity


class BasePartitionedTuple(tuple):
    _count:     int
    _capacity:  int

    _bias_base: float = 0.4
    _bias_min:  float = 0.001 # lower bound of partition calc offset.
    _count_max:   int = 30    # upper bound of no. partitions

    @classmethod
    def _get_dimensions(cls, arr: Iterable, kwargs: dict):
        bias_override = kwargs.get("bias", None)
        bias          = bias_override or cls._bias_base
        while True:
            dims = Dimensions.from_iter(arr, bias)
            if bias_override:
                break
            if dims.count < cls._count_max:
                break
            if bias < cls._bias_min:
                break
            bias = bias * 0.2
        return dims

    @classmethod
    def _new(cls, arr: Iterable, dims: Dimensions, args: tuple, kwargs: dict):
        inst = tuple.__new__(cls, _partition(*arr, dims=dims))
        inst._init(dims, (arr, *args), kwargs)
        return inst

    def __new__(cls, arr, *args, **kwargs):
        dims = cls._get_dimensions(arr, kwargs)
        return cls._new(arr, dims, args, kwargs)

    def _init(self, dims: Dimensions, args: tuple, kwargs: dict):
        self._count    = dims.count
        self._capacity = dims.capacity
        self.__init__(*args, **kwargs)

    def __init__(self, arr: Iterable, bias: float = None, *args, **kwargs):
        pass


def _buffer_size(size):
    while _cmath.isprime(size):
        size += 1
    return size


def _dimensions(size: int, bias: float):
    f   = _factors(size, bias)
    mid = len(f) // 2
    return [math.prod(i) for i in (f[:mid], f[mid:])]


def _partition(*items, dims: Dimensions):
    new, items = [], list(items)
    while len(new) < dims.count:
        i, items = items[:dims.capacity], items[dims.capacity:]
        new.append(i)
    return new


def _arrncr(arr: list):
    """
    Given an array, guess the number of
    possible permutations.
    """
    count = len(arr)
    split = len(arr)
    return _ncr(count, split)


def _ncr(count: int, split: int):
    return math.comb(count, split) * math.factorial(split)


def _permutate(arr: list, bias: float):
    split, guess = len(arr), _arrncr(arr)
    bias  = math.floor(((guess * bias) + 1))
    perms = itertools.permutations(arr, split)
    return next(itertools.islice(perms, bias, bias+1))


def _factors(n: int, bias: float):
    f = [f for f in _cmath.prime_factors(n)]
    if len(f) % 2:
        f.insert(0, 1)
    return _permutate(f, bias)


class PartitionedTuple(BasePartitionedTuple):

    def name(self):
        return self.__class__.__name__

    def render_repr(self):
        _repr = f"{self.name()}(%s)"
        return _repr % "".join(self.repr_parts())

    def repr_parts(self):
        stats           = self.render_stats()
        sample          = self.render_sample()
        return [stats, sample]

    def render_stats(self):
        capacity = self._capacity
        count    = self._count
        return f"{count=}, {capacity=}, "

    def render_sample(self):
        sample, end = self[0], None
        if self._capacity >= 5:
            sample, end = sample[:5], "..."

        sample = [f"{i!r}" for i in sample]
        if end:
            sample += [end]
        return "[%s]" % ", ".join(sample)

    def __repr__(self):
        return self.render_repr()


def _test():
    for i in range(1, 10_000):
        arr = [0 for _ in range(i)]
        pt  = PartitionedTuple(arr)
        print(i, pt)


if __name__ == "__main__":
    _test()

