# Simplified version of Snowflake with microseconds(54 bits) as timestamp part.
# The instance is reduced to 6 bits and seq to 4 bits.
#
# Actually for python there is no chance to getting more than two equal timestamps
# in microseconds in one iteration, so seq increments with each iteration.
#
# Also, 54 bit of the timestamp is enough to generate IDs till 2255-06-05 23:47:34.
#
# https://en.wikipedia.org/wiki/Snowflake_ID


from time import time
from typing import Iterator, Optional

MAX_INSTANCE = 0b111111
MAX_SEQ = 0b1111


def microflake(instance: int, *, seq: int = 0, epoch: int = 0) -> Iterator[Optional[int]]:
    assert 0 <= instance <= MAX_INSTANCE, f"instance value must be positive and not exceed {MAX_INSTANCE}!"
    assert 0 <= seq <= MAX_SEQ, f"seq value must be positive and not exceed {MAX_SEQ}!"
    assert epoch <= int(time() * 1000000), f"epoch must be lower than current time in us {int(time() * 1000000)}"

    instance = instance << 4
    last_time = 0

    while True:
        current_time = int(time() * 1000000) - epoch

        if current_time < last_time:
            yield None
            continue

        if seq == MAX_SEQ:
            if last_time == current_time:
                continue
            seq = 0

        yield (last_time := current_time) << 10 | instance | seq

        seq += 1


def get_microseconds(value: int) -> int:
    return value >> 10


def get_seq(value: int) -> int:
    return value & MAX_SEQ


def get_instance(value: int) -> int:
    return value >> 4 & MAX_INSTANCE
