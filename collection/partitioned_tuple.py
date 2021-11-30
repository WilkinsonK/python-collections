import math
from typing import Iterable

from clibs import _cmath


class PartitionedTuple(tuple):
    _partition_bias:     float
    _partition_count:    int
    _partition_capacity: int

    def __new__(cls, items, bias=0.5, *args, **kwargs):
        items = cls._partition_items(list(items), bias)
        inst  = cls._initialize_tuple(items, *args, **kwargs)
        return inst

    def __init__(self, items: Iterable, bias: float = 0.5):
        self._sample_value       = self[0] if len(self) > 0 else []
        self._partition_count    = len(self)
        self._partition_capacity = len(self._sample_value)

    def __repr__(self):
        count, capacity  = self.count, self.capacity
        return "".join([
            f"{self.__class__.__name__}(",
            f"{count=}, {capacity=}, ",
            f"[{self._render_repr()}]", f")"
        ])

    @classmethod
    def _initialize_tuple(cls, items: list, *args, **kwargs):
        if cls is tuple:
            cls = PartitionedTuple

        inst = tuple.__new__(cls, items)
        inst.__init__(items, *args, **kwargs)
        return inst

    @classmethod
    def _get_dimensions(cls, items: list, bias: float):
        size = _get_size_buffer(items)
        return _get_dimensions(size, bias)

    @classmethod
    def _partition_items(cls, items: list, bias: float):
        count, cap = cls._get_dimensions(items, bias)
        return _partition_items(items, count, cap)

    def _render_repr(self):
        sample, end = list(self._sample_value), None
        if self.capacity >= 5:
            sample, end = sample[:5], "..."
        return self._render_repr_sample(sample, end)

    @staticmethod
    def _render_repr_sample(sample: list, end: str = None):
        sample = [f"{i!r}" for i in sample]
        if end:
            sample += [end]
        return ", ".join(sample)

    @property
    def count(self):
        return self._partition_count

    @property
    def capacity(self):
        return self._partition_capacity


def _get_size_buffer(iterable: Iterable):
    size = len(iterable)
    while _cmath.isprime(size):
        size += 1
    return size


def _get_dimensions(size: int, bias: float):
    factors = [f for f in _cmath.prime_factors(size)]
    bias    = math.floor(len(factors) * bias)
    return [math.prod(i) for i in (factors[:bias], factors[bias:])]


def _partition_items(items: list, count: int, capacity: int):
    new = []
    while len(new) < count:
        i, items = items[:capacity], items[capacity:]
        new.append(i)
    return new


def _test():
    for i in range(10000):
        print(i, [j for j in _cmath.prime_factors(i)])
        test = PartitionedTuple([j for j in range(i)])


if __name__ == "__main__":
    _test()

