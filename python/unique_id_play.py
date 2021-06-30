# Attempt to create own unique id generator

from hashlib import sha1
from os import urandom
from string import ascii_lowercase, ascii_letters, digits
from time import time
from typing import Sequence, Callable, Generator

__all__ = ('create_simple_generator', 'create_auid_generator')


def _mask(alen: int) -> int:
    """Return precalculated mask"""

    assert 1 < alen < 256, "alphabet length must be between 1 and 255 inclusive!"

    if alen == 2:
        return 0b00000001
    if alen <= 4:
        return 0b00000011
    if alen <= 8:
        return 0b00000111
    if alen <= 16:
        return 0b00001111
    if alen <= 32:
        return 0b00011111
    if alen <= 64:
        return 0b00111111
    if alen <= 128:
        return 0b01111111

    return 0b11111111


def _timestamp_bytes() -> bytes:
    return int(time() * 1000000).to_bytes(8, "big")


def _hashed_gen(alphabet: Sequence[str], start: bytes) -> Generator[str, None, None]:
    """Generate random characters by given criteria"""

    alen = len(alphabet)

    assert 1 < alen < 256, "alphabet length must be between 1 and 255 inclusive!"

    mask = _mask(alen)
    buffer = sha1(start).digest()

    while True:
        buffer = sha1(start + buffer).digest()
        for b in bytearray(buffer):
            b = b & mask
            if b < alen:
                yield alphabet[b]


def _random_gen(alphabet: Sequence[str], buffer_size: int = 1024) -> Generator[str, None, None]:
    """Generate random characters by given criteria"""

    alen = len(alphabet)

    assert buffer_size > 0, "buffer_size must be greater than 1!"
    assert 1 < alen < 256, "alphabet length must be between 1 and 255 inclusive!"

    mask = _mask(alen)

    while True:
        for b in bytearray(urandom(buffer_size)):
            b = b & mask
            if b < alen:
                yield alphabet[b]


def create_simple_generator(*, alphabet: Sequence[str] = ascii_letters + digits, default_size: int = 64,
                            buffer_size: int = 1024) -> Callable[..., str]:
    """Generate random number of characters"""

    assert default_size > 0, "size must be greater than 1!"

    gen = _random_gen(alphabet, buffer_size)

    def generator(size: int = default_size) -> str:
        assert size > 0, "size must be greater than 1!"

        return str().join([next(gen) for _ in range(size)])

    return generator


def create_auid_generator(namespace: str = None, *, alphabet: Sequence[str] = ascii_lowercase + digits,
                          buffer_size: int = 1024) -> Callable[[], str]:
    """Create random uid looks like UUID."""

    gen = _random_gen(alphabet, buffer_size)

    namespace = namespace or str().join([next(gen) for _ in range(64)])
    ngen = _hashed_gen(alphabet, namespace.encode())
    namespace = str().join([next(ngen) for _ in range(8)])
    namespace_enc = namespace.encode()

    sgen = _hashed_gen(alphabet, _timestamp_bytes() + namespace_enc)
    scope = str().join([next(sgen) for _ in range(4)])

    def generator() -> str:
        uid = str().join([next(gen) for _ in range(12)])

        tgen = _hashed_gen(alphabet, namespace_enc + _timestamp_bytes())
        t1 = str().join([next(tgen) for _ in range(4)])
        t2 = str().join([next(tgen) for _ in range(4)])

        return f"{namespace}-{scope}-{t1}-{t2}-{uid}"

    return generator
