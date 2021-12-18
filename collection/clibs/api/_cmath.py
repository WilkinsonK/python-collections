import cffi

from clibs.bin._math._math import lib as __lib, ffi as __ffi


__ffi: cffi.FFI = __ffi


def isprime(n: int):
    return bool(__lib.CisPrime(n))


def get_next_prime(n: int):
    return int(__lib.CgetNextPrime(n))


def primes(*bounds):
    lower, upper = [1, *bounds] if len(bounds) < 2 else bounds
    lower = int(__lib.CgetNextPrime(lower))
    while lower < upper:
        yield lower
        lower = int(__lib.CgetNextPrime(lower))


def _next_factor(n: int):
    for p in primes(n):
        if n % p == 0:
            return n // p, p


def prime_factors(n: int):
    while not (isprime(n) or (n <= 1)):
        n, prime = _next_factor(n)
        yield prime
    yield n
