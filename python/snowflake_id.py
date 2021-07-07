# Simple implementation of the Snowflake ID algorithm
# https://en.wikipedia.org/wiki/Snowflake_ID


from time import time
from typing import Iterator, Optional

MAX_INSTANCE = 0b1111111111
MAX_SEQ = 0b111111111111


def snowflake(instance: int, seq: int = 0) -> Iterator[Optional[int]]:
    assert 0 <= instance <= MAX_INSTANCE, f"instance value must be positive and not exceed {MAX_INSTANCE}!"
    assert 0 <= seq <= MAX_SEQ, f"seq value must be positive and not exceed {MAX_SEQ}!"

    instance = instance << 12
    last_time = 0

    while True:
        current_time = int(time() * 1000)

        if last_time == current_time:
            if seq == MAX_SEQ:
                yield None
                continue
            seq += 1
        elif last_time > current_time:
            yield None
            continue
        else:
            seq = 0

        yield (last_time := current_time) << 22 | instance | seq


def get_milliseconds(value: int) -> int:
    return value >> 22


def get_seq(value: int) -> int:
    return value & MAX_SEQ


def get_instance(value: int) -> int:
    return value >> 12 & MAX_INSTANCE
