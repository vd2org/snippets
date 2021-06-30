# Simple implementation of the Snowflake ID algorithm
# https://en.wikipedia.org/wiki/Snowflake_ID


from time import time
from typing import Iterator

MAX_INSTANCE = 0b1111111111
MAX_SEQ = 0b111111111111


def snowflake(instance: int, seq: int = 0) -> Iterator[int]:
    assert instance <= MAX_INSTANCE, f"Instance value must not exceed {MAX_INSTANCE}!"

    instance = instance << 12

    while True:
        seq += 1

        if seq > MAX_SEQ:
            seq = 0

        yield int(time() * 1000) << 22 | instance | seq


def get_milliseconds(value: int) -> int:
    return value >> 22


def get_seq(value: int) -> int:
    return value & MAX_SEQ


def get_instance(value: int) -> int:
    return value >> 12 & MAX_INSTANCE
