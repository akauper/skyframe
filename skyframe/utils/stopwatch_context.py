import asyncio
import time
from typing import Optional, Self


class StopwatchContext:
    def __init__(self):
        self._is_async = False
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    def __enter__(self) -> Self:
        self._start_time = time.monotonic()
        return self

    async def __aenter__(self) -> Self:
        self._start_time = asyncio.get_event_loop().time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.monotonic()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._end_time = asyncio.get_event_loop().time()

    @property
    def elapsed(self) -> float:
        if self._start_time is None:
            return 0

        if self._end_time is None:
            if self._is_async:
                return asyncio.get_event_loop().time() - self._start_time
            return time.monotonic() - self._start_time

        return self._end_time - self._start_time

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed * 1000

    @property
    def elapsed_ms_int(self) -> int:
        return int(self.elapsed_ms)

    @property
    def start_time(self) -> float:
        return self._start_time

    @property
    def end_time(self) -> float:
        return self._end_time
