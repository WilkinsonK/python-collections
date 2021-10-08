import asyncio

from asyncio import AbstractEventLoop
from typing import Coroutine


def _make_callback(coro: Coroutine):
    """Convenience function for creating  async tasks."""
    def inner():
        return asyncio.ensure_future(coro)
    return inner


def _get_event_loop(loop: AbstractEventLoop):
    """Convenience function for getting event loop."""
    if loop is None:
        loop = asyncio.get_event_loop()
    return loop


def execute_async_task(coro: Coroutine, delay: float = 0.0, loop: AbstractEventLoop = None):
    """Schedule a coroutine to run at the specified delay."""
    loop     = _get_event_loop(loop)
    callback = _make_callback(coro)
    return loop.call_later(delay, callback)
