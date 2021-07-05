# Simple implementation of the asynchronous ttl cache decorator for Python 3.9+.

from functools import wraps
from time import time
from typing import Dict, Any, Callable, NamedTuple, Awaitable


class CacheInfo(NamedTuple):
    ttl: int
    size: int
    threshold: int
    hits: int
    misses: int
    current: int
    cleaning: int
    cleaned: int


class CacheRecord(NamedTuple):
    expire: int
    data: Any


def cached(ttl: int = 10 * 60, size: int = 1024, threshold: int = 2048):
    assert ttl > 0, "Must be positive integer"
    assert size > 0, "Must be positive integer"
    assert threshold > size, "Must be greater than threshold"

    cache: Dict[str, CacheRecord] = {}
    hits: int = 0
    misses: int = 0
    cleaning: int = 0
    cleaned: int = 0

    def info() -> CacheInfo:
        return CacheInfo(ttl, size, threshold, hits, misses, len(cache), cleaning, cleaned)

    def clean(now: int):
        nonlocal cleaning, cleaned

        temp = []

        for item in reversed(cache.items()):
            if item[1].expire < now:
                continue
            temp.append(item)
            if len(temp) >= size:
                break

        cleaning += 1
        cleaned += len(cache) - len(temp)

        cache.clear()
        cache.update(reversed(temp))

    def inner(f: Callable[[...], Awaitable]):
        @wraps(f)
        async def decorator(*args, **kwargs) -> Any:
            nonlocal hits, misses

            key = repr(args) + repr(kwargs)
            now = int(time())
            
            if rec := cache.get(key):
                if rec.expire > now:
                    hits += 1
                    return rec.data
                del cache[key]

            if len(cache) > threshold:
                clean(now)

            cache[key] = (rec := CacheRecord(expire=now + ttl, data=await f(*args, **kwargs)))
            misses += 1
            return rec.data

        decorator.cache_info = info

        return decorator

    return inner
