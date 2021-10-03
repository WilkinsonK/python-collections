import math
from typing import Iterable


class PartitionedTuple(tuple):
    _partition_bias:     float
    _partition_count:    int
    _partition_capacity: int

    def __new__(cls, items, bias=0.5, *args, **kwargs):
        items = cls._partition_items(list(items), bias)
        inst  = cls._initialize_tuple(items, *args, **kwargs)
        return inst

    def __init__(self, items: Iterable, bias: float = 0.5):
        self._partition_count    = len(self)
        self._partition_capacity = len(self[0])

    def __repr__(self):
        count, capacity  = self.count, self.capacity
        return "".join([
            f"{self.__class__.__name__}(",
            f"{count=}, {capacity=}, ",
            f"[{_render_repr(self)}]", f")"
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
        _, cap = cls._get_dimensions(items, bias)
        return _partition_items(items, cap)

    def _init(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

    @property
    def count(self):
        return self._partition_count

    @property
    def capacity(self):
        return self._partition_capacity


def _factors(start: int):
    while not (_is_prime(start) or (start <= 1)):
        for prime in _primes(start):
            if start % prime == 0:
                yield prime
                start = start // prime
    yield start


def _factor_smallest(num: int):
    factors = [i for i in _factors(num)]
    return factors


def _get_size_buffer(iterable: Iterable):
    size = len(iterable)
    while _is_prime(size):
        size += 1
    return size


def _get_dimensions(size: int, bias: float):
    factors = _factor_smallest(size)
    bias    = math.floor(len(factors) * bias)
    return [math.prod(i) for i in (factors[:bias], factors[bias:])]


def _partition_items(items: list, capacity: int):
    new = []
    while len(items) > 0:
        i, items = items[:capacity], items[capacity:]
        new.append(i)
    return new


def _primes(limit: int):
    next_val = 0
    while next_val < limit:
        while not _is_prime(next_val):
            next_val += 1
        if next_val >= limit: break
        yield next_val
        next_val += 1


def _render_repr(ptuple: PartitionedTuple):
    sample = list(ptuple[0])
    if ptuple.capacity >= 5:
        return _render_repr_sample(sample[:5], "...")
    return _render_repr_sample(sample)


def _render_repr_sample(sample: list, end: str = None):
    sample = [f"{i!r}" for i in sample]
    if end:
        sample += [end]
    return ", ".join(sample)


def _is_prime(num: int):
    if (num <= 1): return False
    if (num <= 3): return True
    if (num % 2 == 0 or num % 3 == 0): return False

    step = 5
    while ((step ** 2) <= num):
        if (num % step == 0 or num % (step + 2) == 0):
            return False
        step += 6

    return True
