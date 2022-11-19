import csv
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict

from .client import FutureResult, UMClient
from .timer import Timer


class DataLogger:

    def __init__(
            self, client: 'UMClient', output_csv: str,
            logging_interval: float = 1.0, timer_timeout: float = 600.) -> None:
        self.funcs = {'timestamp': lambda: datetime.now().timestamp()}
        self._client = client
        self.output_csv = output_csv
        self.logging_interval = logging_interval
        self.__valdict = None
        self.__thread = None
        self.__loop_alive = False

        self._timer = Timer(self, timeout=timer_timeout)

    def register(self, funcs: Callable[[], Any]) -> None:
        self.funcs.update(funcs)

    def get(self, *names: str) -> Any:
        valdict = self.get_all()
        if len(names) > 1:
            return tuple(valdict[name] for name in names)
        return valdict[names[0]]

    def get_all(self) -> Dict[str, Any]:
        self._timer.wait_for(lambda: self.__valdict is not None)
        return self.__valdict.copy()

    @contextmanager
    def loop(self) -> None:
        try:
            f = open(self.output_csv, 'a', newline='')
            self.__writer = csv.writer(f)
            self.__writer.writerow(self.funcs.keys())

            self.__thread = threading.Thread(target=self.update)
            self.__loop_alive = True
            self.__thread.start()
            yield
        finally:
            self.__loop_alive = False
            self.__thread.join()
            f.flush()
            f.close()

    def update(self) -> None:
        def main():
            with self._client.batch_mode():
                rets = [f() for f in self.funcs.values()]
            valdict = {}
            for ret, name in zip(rets, self.funcs.keys()):
                if isinstance(ret, FutureResult):
                    val = ret.get()
                else:
                    val = ret
                valdict[name] = val
            self.__valdict = valdict
            self.__writer.writerow(valdict.values())

        while self.__loop_alive:
            t1 = time.perf_counter()
            main()
            t2 = time.perf_counter()
            time.sleep(max(0, self.logging_interval-(t2-t1)))

    def get_timer(self) -> 'Timer':
        return self._timer
