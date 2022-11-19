import time
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .datalog import DataLogger


class Timer:

    def __init__(self, data_logger: 'DataLogger', timeout: float) -> None:
        self._data_logger = data_logger
        self._timeout = timeout

    def wait_for_datalog(self, key: str, target: Callable[[Any], bool]) -> None:
        """`target` must take a sensor value as its first argument."""
        self.wait_for(lambda: target(self._data_logger.get(key)))

    def wait_for(self, target: Callable[[], bool]) -> None:
        t1 = time.perf_counter()
        while not target():
            t2 = time.perf_counter()
            if t2 - t1 > self._timeout:
                raise TimeoutError(f'wait time exceeded {self._timeout} seconds')
