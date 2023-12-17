# Universal method caller: sync or async depending on the context
# Only for Python 12+


import asyncio
import time
from functools import wraps
from inspect import signature
from typing import Optional, Self

_SAME_ERR = "Sync and async methods must have the same signature"
_SM_ERR = "Sync method never assigned"
_AM_ERR = "Async method never assigned"
_SMA_ERR = "Sync method already assigned"
_AMA_ERR = "Async method already assigned"


class UniCall[T]:
    def __init__(self, method: Optional[T] = None):
        self._sm = self._am = None
        self.assign(method)

    def assign(self, method: Optional[T]) -> Self:
        if method is None:
            return

        if asyncio.iscoroutinefunction(method):
            assert self._am is None, _SMA_ERR
            assert (signature(self._sm) == signature(method)) if self._sm is not None else True, _SAME_ERR

            self._am = method
        else:
            assert self._sm is None, _AMA_ERR
            assert (signature(self._am) == signature(method)) if self._am is not None else True, _SAME_ERR
            self._sm = method

        return self

    def __get__(self, obj, objtype=None) -> T:
        assert self._am is not None, _AM_ERR
        assert self._sm is not None, _SM_ERR
        
        try:
            asyncio.get_running_loop()
            method = self._am
        except RuntimeError:
            method = self._sm

        if obj is None:
            return method

        @wraps(method)
        def _call(*args, **kwargs):
            return method(obj, *args, **kwargs)

        return _call


def unicall[T](method: T) -> UniCall[T]:
    return UniCall[T](method)


class Test:
    @unicall
    def do(self, param: int) -> str:
        print(f"Running sync {param} do...")
        time.sleep(0.2)
        return "sync result"

    @do.assign
    async def do(self, param: int) -> str:
        print(f"Running async {param} do...")
        await asyncio.sleep(0.3)
        return "async result"

    def xxx(self, i):
        pass

print(Test().do(1))

async def run():
    print(await Test().do(2))

asyncio.run(run())

print(Test().do(3))
