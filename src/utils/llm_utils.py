import math

from configs import (
    LLM_MAX_CALLS,
    LLM_MIN_BATCH_SIZE,
    LLM_MAX_BATCH_SIZE,
)

def calculate_batch_size(
    total_items: int,
    max_calls: int = LLM_MAX_CALLS,
    min_batch_size: int = LLM_MIN_BATCH_SIZE,
    max_batch_size: int = LLM_MAX_BATCH_SIZE,
) -> int:

    if total_items <= 0:
        return min_batch_size

    batch_size = math.ceil(total_items / max_calls)

    batch_size = max(batch_size, min_batch_size)
    batch_size = min(batch_size, max_batch_size)

    return batch_size
