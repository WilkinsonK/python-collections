import math
from typing import Iterable


def _get_size_buffer(iterable: Iterable):
    size = len(iterable)
    while is_prime(size):
        size += 1
    return size


def _get_dimensions(size: int, bias: float):
    factors = factor_smallest(size)
    bias    = math.floor(len(factors) * bias)
    return [math.prod(i) for i in (factors[:bias], factors[bias:])]


def _partition_items(items: list, capacity: int):
    new = []
    while len(items) > 0:
        i, items = items[:capacity], items[capacity:]
        new.append(i)
    return new


class PartitionedTuple(tuple):
    _partition_count:    int
    _partition_capacity: int

    def __new__(cls, items: Iterable, bias: float = 0.5, *args, **kwargs):
        items = cls._partition_items(list(items), bias)
        inst  = cls._make_new(items, *args, **kwargs)
        return inst

    def __init__(self, *items):
        self._partition_count    = len(self)
        self._partition_capacity = len(self[0])

    @classmethod
    def _make_new(cls, items: list, init=True, *args, **kwargs):
        if cls is tuple:
            cls = PartitionedTuple

        inst = tuple.__new__(cls, items)
        if init:
            inst._init(*items, *args, **kwargs)
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


def factor_smallest(num: int):
    factors = list()

    while not (is_prime(num) or (num <= 1)):
        for prime in primes(num):
            if num % prime == 0:
                factors.append(prime)
                num = num // prime

    factors.append(num)
    return factors


def primes(limit: int):
    next_val = 0
    while next_val < limit:
        while not is_prime(next_val):
            next_val += 1
        if next_val >= limit: break
        yield next_val
        next_val += 1


def is_prime(num: int):
    if (num <= 1): return False
    if (num <= 3): return True
    if (num % 2 == 0 or num % 3 == 0): return False

    step = 5
    while ((step ** 2) <= num):
        if (num % step == 0 or num % (step + 2) == 0):
            return False
        step += 6

    return True


part_t = PartitionedTuple([0 for _ in range(49)])
print(part_t.capacity, part_t.count, part_t, end="\n")
