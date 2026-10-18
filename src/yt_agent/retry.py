from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def with_retry(operation: Callable[[], T], attempts: int = 3, base_delay: float = 0.5, jitter: float = 0.2) -> T:
    last_error: Exception | None = None
    for index in range(max(1, attempts)):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if index == attempts - 1:
                break
            time.sleep(base_delay * (2 ** index) + random.random() * jitter)
    assert last_error is not None
    raise last_error
