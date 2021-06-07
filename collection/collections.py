import math

from collections import UserList
from typing import Union, List, Tuple


class PartitionList(UserList):

    def partition_list(self, array, bias):
        init_size = self._get_init_size(array)
        partition_array = list()
        partitions, capacity = factors_from_bias(init_size, bias)

        step = 0
        while len(partition_array) < partitions:
            partition_array.append(tuple(array[step:step+capacity]))
            step += capacity

        self.container = partition_array
        self.partitions = partitions
        self.capacity = capacity
        self.total_count = len(array)

        return self

    def _get_init_size(self, array):
        size = len(array)
        while is_prime(size):
            size += 1
        return size

    def __init__(self, array: Union[list, tuple], bias: int = 0.5):
        self.partition_list(array, bias)

    def __repr__(self):
        name = self.__class__.__name__
        parts = f"partitions: {self.partitions}"
        size = f"max-capacity: {self.capacity}"
        total = f"total-elements: {self.total_count}"
        return f"{name}([{parts}, {size}, {total}], {self.container})"

    def __iter__(self):
        return iter(self.container)


def factors_from_bias(num: int, bias: float = 0.5):
    factors = factor_smallest(num)
    bias = math.floor(len(factors) * bias)

    return math.prod(factors[:bias]), math.prod(factors[bias:])


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
    step = 0
    while step < limit:
        while not is_prime(step):
            step += 1
        if step >= limit: break
        yield step
        step += 1


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