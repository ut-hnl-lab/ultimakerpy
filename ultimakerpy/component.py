import atexit
from datetime import datetime
import subprocess
from typing import BinaryIO, Dict, Optional, Tuple

from .client import UMClient
from .const import CAMSTREAM_PY_PATH, Ctype
from .exceptions import ChoiceValidationError, RangeValidationError


def _validate_range(val, min_, max_):
    if not min_ <= val <= max_:
        raise RangeValidationError(
            f'{val} is not in limit range of {min_} to {max_}')


def _validate_choice(val, choices):
    if not val in choices:
        raise ChoiceValidationError(
            f'{val} is not in choices {choices}')


class System:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def start_job(self, fileobj: BinaryIO) -> None:
        self._client.post(self._url['job'],
                          files={'job_name': format(datetime.now()),
                                 'file': fileobj})

    def set_job_state(self, value: str) -> None:
        _validate_choice(value, self._lim['state'])
        self._client.put(self._url['state'], {'target': value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def printer_status(self) -> str:
        return self._client.get(self._url['status'],
                                headers={'Accept': Ctype.APP_JSON})

    def job_state(self) -> str:
        return self._client.get(self._url['state'],
                                headers={'Accept': Ctype.APP_JSON})

    def verify(self) -> Dict[str, str]:
        return self._client.get(self._url['verify'],
                                headers={'Accept': Ctype.APP_JSON})


class Peripherals:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def camera_streaming(
            self, name: str = 'Internal Camera') -> 'subprocess.Popen':
        proc = subprocess.Popen(
            'python "{path}" {target} --name "{name}"'.format(
                path=CAMSTREAM_PY_PATH,
                target=self._url['cam_stream'],
                name=name))
        atexit.register(proc.kill)
        return proc

    def ambient_temperature(self) -> float:
        return self._client.get(self._url['amb_temp'],
                                headers={'Accept': Ctype.APP_JSON})


class Bed:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def heat_to(self, value: float) -> None:
        _validate_range(value, *self._lim['tgt_temp'])
        self._client.put(self._url['tgt_temp'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def preheat_to(self, value: float, timeout: Optional[float] = None) -> None:
        _validate_range(value, *self._lim['pre_temp'])
        self._client.put(self._url['pre_temp'],
                         {'temperature': value, 'timeout': timeout},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def move_to(self, value: float) -> None:
        _validate_range(value, *self._lim['pos_z'])
        self._client.put(self._url['pos'], {'z': value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def limit_speed_to(self, value: float) -> None:
        _validate_range(value, *self._lim['speed_z'])
        self._client.put(self._url['speed'], {'z': value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def set_jerk_to(self, value: float) -> None:
        _validate_range(value, *self._lim['jerk_z'])
        self._client.put(self._url['jerk'], {'z': value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def heat_by(self, value: float) -> None:
        new = self.target_temperature() + value
        self.heat_to(value=new)

    def move_by(self, value: float) -> None:
        new = self.position() + value
        self.move_to(value=new)

    def temperature(self) -> float:
        return self._client.get(self._url['cur_temp'],
                                headers={'Accept': Ctype.APP_JSON})

    def target_temperature(self) -> float:
        return self._client.get(self._url['tgt_temp'],
                                headers={'Accept': Ctype.APP_JSON})

    def preheat_temperature(self) -> float:
        return self._client.get(self._url['pre_temp'],
                                headers={'Accept': Ctype.APP_JSON})

    def position(self) -> float:
        return self._client.get(self._url['pos_z'],
                                headers={'Accept': Ctype.APP_JSON})


class Head:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def move_to(
            self,
            x_value: Optional[float] = None,
            y_value: Optional[float] = None) -> None:
        if x_value is not None:
            _validate_range(x_value, *self._lim['pos_x'])
        if y_value is not None:
            _validate_range(y_value, *self._lim['pos_y'])
        self._client.put(self._url['pos'], {'x': x_value, 'y': y_value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def limit_speed_to(
            self,
            x_value: Optional[float] = None,
            y_value: Optional[float] = None) -> None:
        if x_value is not None:
            _validate_range(x_value, *self._lim['speed_x'])
        if y_value is not None:
            _validate_range(y_value, *self._lim['speed_y'])
        self._client.put(self._url['speed'], {'x': x_value, 'y': y_value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def set_acceleration_to(self, value: float) -> None:
        _validate_range(value, *self._lim['accel'])
        self._client.put(self._url['accel'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def set_jerk_to(
            self,
            x_value: Optional[float] = None,
            y_value: Optional[float] = None) -> None:
        if x_value is not None:
            _validate_range(x_value, *self._lim['jerk_x'])
        if y_value is not None:
            _validate_range(y_value, *self._lim['jerk_y'])
        self._client.put(self._url['jerk'], {'x': x_value, 'y': y_value},
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def move_by(
            self,
            x_value: Optional[float] = None,
            y_value: Optional[float] = None) -> None:
        x_new, y_new = None, None
        if x_value is not None:
            x_new = self.position_x() + x_value
        if y_value is not None:
            y_new = self.position_y() + y_value
        self.move_to(x_value=x_new, y_value=y_new)

    def position(self) -> Tuple[float, float]:
        res = self._client.get(self._url['pos'],
                               headers={'Accept': Ctype.APP_JSON})
        return (res['x'], res['y'])

    def position_x(self) -> float:
        return self._client.get(self._url['pos_x'],
                                headers={'Accept': Ctype.APP_JSON})

    def position_y(self) -> float:
        return self._client.get(self._url['pos_y'],
                                headers={'Accept': Ctype.APP_JSON})

    def max_speed(self) -> Tuple[float, float]:
        res = self._client.get(self._url['speed'],
                               headers={'Accept': Ctype.APP_JSON})
        return (res['x'], res['y'])

    def max_speed_x(self) -> float:
        return self._client.get(self._url['speed_x'],
                                headers={'Accept': Ctype.APP_JSON})

    def max_speed_y(self) -> float:
        return self._client.get(self._url['speed_y'],
                                headers={'Accept': Ctype.APP_JSON})

    def accel(self) -> float:
        return self._client.get(self._url['accel'],
                                headers={'Accept': Ctype.APP_JSON})

    def jerk(self) -> Tuple[float, float]:
        res = self._client.get(self._url['jerk'],
                               headers={'Accept': Ctype.APP_JSON})
        return (res['x'], res['y'])

    def jerk_x(self) -> float:
        return self._client.get(self._url['jerk_x'],
                                headers={'Accept': Ctype.APP_JSON})

    def jerk_y(self) -> float:
        return self._client.get(self._url['jerk_y'],
                                headers={'Accept': Ctype.APP_JSON})


class Feeder:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def limit_speed_to(self, value: float) -> None:
        _validate_range(value, *self._lim['speed'])
        self._client.put(self._url['speed'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def set_acceleration_to(self, value: float) -> None:
        _validate_range(value, *self._lim['accel'])
        self._client.put(self._url['accel'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def set_jerk_to(self, value: float) -> None:
        _validate_range(value, *self._lim['jerk'])
        self._client.put(self._url['jerk'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def max_speed(self) -> float:
        return self._client.get(self._url['speed'],
                                headers={'Accept': Ctype.APP_JSON})

    def acceleration(self) -> float:
        return self._client.get(self._url['accel'],
                                headers={'Accept': Ctype.APP_JSON})

    def jerk(self) -> float:
        return self._client.get(self._url['jerk'],
                                headers={'Accept': Ctype.APP_JSON})


class Nozzle:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def heat_to(self, value: float) -> None:
        _validate_range(value, *self._lim['tgt_temp'])
        self._client.put(self._url['tgt_temp'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def heat_by(self, value: float) -> None:
        new = self.target_temperature() + value
        self.heat_to(value=new)

    def temperature(self) -> float:
        return self._client.get(self._url['cur_temp'],
                                headers={'Accept': Ctype.APP_JSON})

    def target_temperature(self) -> float:
        return self._client.get(self._url['tgt_temp'],
                                headers={'Accept': Ctype.APP_JSON})


class LED:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def set_brightness_to(self, value: float) -> None:
        _validate_range(value, *self._lim['brightness'])
        self._client.put(self._url['brightness'], value,
                         headers={'Content-Type': Ctype.APP_JSON,
                                  'Accept': Ctype.APP_JSON})

    def brightness(self) -> float:
        return self._client.get(self._url['brightness'],
                                headers={'Accept': Ctype.APP_JSON})


class Fan:

    def __init__(self, client: 'UMClient', url: Dict, lim: Dict) -> None:
        self._client = client
        self._url = url
        self._lim = lim

    def speed(self) -> float:
        return self._client.get(self._url['speed'],
                                headers={'Accept': Ctype.APP_JSON})
