from enum import Enum
import os


def _abssource(relpath: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relpath))


def _relsource(relpath: str) -> str:
    return os.path.abspath(os.path.join(os.getcwd(), relpath))


ENDPOINT = _abssource('endpoint.json')
CONFIG = _relsource('config.yaml')
PRINTABLE_FORMATS = [
    ('UFP file','*.ufp'),
    ('GCODE file', '*.gcode')
]


class CTYPE:
    APP_JSON = 'application/json'
    MP_FD = 'multipart/form-data'


class JobState:
    PAUSE = 'pause'
    ABORT = 'abort'
    PRINT = 'print'
    NONE = 'none'
    PRE_PRINT = 'pre_print'
    PRINTING = 'printing'


class PrinterStatus:
    BOOTING = 'booting'
    WAITING_FOR_PERIPHERALS = 'waiting_for_peripherals'
    IDLE = 'idle'
    PRINTING = 'printing'
    ERROR = 'error'
    MAINTENANCE = 'maintenance'
