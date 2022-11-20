import random
import time

from ultimakerpy.client import UMClient
from ultimakerpy.datalog import DataLogger
from ultimakerpy.printer import UMS3


URL = 'https://pokeapi.co/api/v2/pokemon/{}'


def test_datalogger():
    print('test_datalogger')
    client = UMClient()
    logger = DataLogger(client, 'test_datalogger.csv', logging_interval=0)
    logger.register({
        'poke1': lambda: client.get(URL.format(random.randint(1, 100)))['name'],
        'poke2': lambda: client.get(URL.format(random.randint(1, 100)))['name'],
        'poke3': lambda: client.get(URL.format(random.randint(1, 100)))['name']
    })
    with logger.loop():
        for i in range(3):
            print(i, logger.get('poke1', 'poke2', 'poke3'))
            time.sleep(1.0)


def test_s3_datalogger():
    print('test_s3_datalogger')
    printer = UMS3(name='hnl')
    targets = {
        'status': printer.status,
        'job_state': printer.job_state,
        'amb_temp': printer.peripherals.ambient_temperature,
        'head_pos_x': printer.head.position_x,
        'head_pos_y': printer.head.position_y,
        'head_spd_x': printer.head.max_speed_x,
        'head_spd_y': printer.head.max_speed_y,
        'head_acc': printer.head.accel,
        'head_jrk_x': printer.head.jerk_x,
        'head_jrk_y': printer.head.jerk_y,
        'bed_pos': printer.bed.position,
        'bed_temp_cur': printer.bed.temperature,
        'bed_temp_tgt': printer.bed.target_temperature,
        'mnoz_temp_cur': printer.main_nozzle.temperature,
        'mnoz_temp_tgt': printer.main_nozzle.target_temperature,
        'snoz_temp_cur': printer.sub_nozzle.temperature,
        'snoz_temp_tgt': printer.sub_nozzle.target_temperature,
        'mfed_spd': printer.main_feeder.max_speed,
        'mfed_acc': printer.main_feeder.acceleration,
        'mfed_jrk': printer.main_feeder.jerk,
        'sfed_spd': printer.sub_feeder.max_speed,
        'sfed_acc': printer.sub_feeder.acceleration,
        'sfed_jrk': printer.sub_feeder.jerk,
        'led_brn': printer.led.brightness,
        'fan_spd': printer.fan.speed,
    }
    with printer.data_logger('test_s3_datalogger.csv', targets) as dl:
        for i in range(3):
            print(i)
            time.sleep(1.0)


if __name__ == '__main__':
    test_datalogger()
    test_s3_datalogger()
