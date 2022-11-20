from contextlib import contextmanager
import json
from tkinter import Tk
import tkinter.filedialog
from typing import Any, Callable, Dict, Iterator
import warnings

import yaml

from .client import UMClient
from .component import LED, Bed, Fan, Feeder, Head, Nozzle, Peripherals, System
from .const import CONFIG, ENDPOINT, PRINTABLE_FORMATS, JobState, PrinterStatus
from .datalog import DataLogger
from .exceptions import PrintJobWarning, RequestError
from .parse import parse_endpoints


class _Printer:

    def __init__(self, machine_type: str, config_key: str) -> None:
        with open(CONFIG, 'r') as f:
            config: dict = yaml.safe_load(f)[config_key]

        with open(ENDPOINT, 'r') as f:
            items = json.load(f)[machine_type]

        ip_address = config['ip_address']
        username = config.get('username', None)
        password = config.get('password', None)

        request_timeout = config.get('request_timeout', 30)
        self.timer_timeout = config.get('timer_timeout', 600)
        self.logging_interval = config.get('logging_interval', 1.0)

        self._client = UMClient(timeout=request_timeout, username=username,
                                password=password)

        self._url, self._lim = parse_endpoints(
            items=items,
            base_path='http://{ip_address}'.format(ip_address=ip_address))

        self._system = System(self._client, self._url['system'],
                              self._lim['system'])

    @contextmanager
    def data_logger(
            self, filepath: str, target_funcs: Dict[str, Callable[[], Any]]
            ) -> Iterator['DataLogger']:
        try:
            dl = DataLogger(self._client, filepath,
                            logging_interval=self.logging_interval,
                            timer_timeout=self.timer_timeout)
            dl.register(target_funcs)
            with dl.loop():
                yield dl
        finally:
            pass

    def print(self, filepath: str) -> None:
        if self.status() != PrinterStatus.IDLE:
            warnings.warn(
                'The new job is ignored because the printer is still working.',
                PrintJobWarning, stacklevel=2)
        else:
            with open(filepath, 'rb') as f:
                self._system.start_job(fileobj=f)

    def print_from_dialog(self) -> None:
        Tk().withdraw()
        filepath = tkinter.filedialog.askopenfilename(
            filetypes=PRINTABLE_FORMATS)
        if filepath == '':
            return
        self.print(filepath)

    def pause(self) -> None:
        self._system.set_job_state(JobState.PAUSE)

    def resume(self) -> None:
        self._system.set_job_state(JobState.PRINT)

    def abort(self) -> None:
        self._system.set_job_state(JobState.ABORT)

    def status(self) -> str:
        return self._system.printer_status()

    def job_state(self) -> str:
        try:
            return self._system.job_state()
        except RequestError:
            return JobState.NONE

    def is_accessible(self) -> bool:
        try:
            self._system.verify()
            return True
        except RequestError:
            return False


class UMS3(_Printer):

    def __init__(self, name: str) -> None:
        super().__init__(machine_type='s3', config_key=name)

        self.__bed = Bed(self._client, self._url['bed'], self._lim['bed'])
        self.__fan = Fan(self._client, self._url['fan'], self._lim['fan'])
        self.__head = Head(self._client, self._url['head'], self._lim['head'])
        self.__led = LED(self._client, self._url['led'], self._lim['led'])
        self.__main_feeder = Feeder(self._client, self._url['feeder1'],
                                    self._lim['feeder1'])
        self.__main_nozzle = Nozzle(self._client, self._url['nozzle1'],
                                    self._lim['nozzle1'])
        self.__sub_feeder = Feeder(self._client, self._url['feeder2'],
                                   self._lim['feeder2'])
        self.__sub_nozzle = Nozzle(self._client, self._url['nozzle2'],
                                   self._lim['nozzle2'])
        self.__peripherals = Peripherals(self._client, self._url['periph'],
                                         self._lim['periph'])

    @property
    def bed(self) -> 'Bed':
        return self.__bed

    @property
    def fan(self) -> 'Fan':
        return self.__fan

    @property
    def head(self) -> 'Head':
        return self.__head

    @property
    def led(self) -> 'LED':
        return self.__led

    @property
    def main_feeder(self) -> 'Feeder':
        return self.__main_feeder

    @property
    def main_nozzle(self) -> 'Nozzle':
        return self.__main_nozzle

    @property
    def sub_feeder(self) -> 'Feeder':
        return self.__sub_feeder

    @property
    def sub_nozzle(self) -> 'Nozzle':
        return self.__sub_nozzle

    @property
    def peripherals(self) -> 'Peripherals':
        return self.__peripherals
