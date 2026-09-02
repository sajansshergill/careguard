"""Small context manager for measuring wall-clock latency."""
from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def timed():
    """Usage:  with timed() as t: ...   then t() -> elapsed ms."""
    start = time.perf_counter()
    elapsed = {"ms": 0.0}
    try:
        yield lambda: elapsed["ms"]
    finally:
        elapsed["ms"] = (time.perf_counter() - start) * 1000
