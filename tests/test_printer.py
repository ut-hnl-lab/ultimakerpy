import time
from ultimakerpy.timer import Timer
from ultimakerpy.printer import UMS3
from ultimakerpy.const import JobState

NUM_PRINTLAYER = 20
PITCH = 0.2


def print_started(state):
    if state == JobState.PRINTING:
        time.sleep(6.0)
        return True
    elif state == JobState.NONE:
        raise Exception('active-leveling failed')
    return False


def layer_reached(pos, n):
    if round(pos / PITCH) >= n:
        return True
    return False


def test_print():
    print('test_print')
    printer = UMS3(name='hnl')
    print('accessibility', printer.is_accessible())

    targets = {'job_state': printer.job_state, 'bed_pos': printer.bed.position}

    printer.print('./tests/tp.ufp')
    printer.peripherals.camera_streaming()
    with printer.data_logger('test_print.csv', targets) as dl:

        timer = dl.get_timer()
        print('waiting')
        timer.wait_for_datalog('job_state', print_started)
        print('start')

        for n in range(1, NUM_PRINTLAYER+1):
            timer.wait_for_datalog('bedpos', lambda x: layer_reached(x, n))
            print('layer', n)

        printer.pause()
        print('pausing')
        time.sleep(30)

        printer.resume()
        print('resuming')
        time.sleep(60)

        printer.abort()
        print('aborting')


if __name__ == '__main__':
    test_print()
