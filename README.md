# UltimakerPy
Python program to easily operate Ultimaker 3D printers with commands. Successor library to "umapi".

## Setup
1. Connect the printer to the local network and fix the IP address.
2. On a PC connected to the same network, access `http://{IP address}` to open the SwaggerUI and perform the authentication process and obtain a username and password.
3. In the working directory, create a yaml file named `config.yaml` like:

    ```YAML
    MyPrinterName:
        ip_address: 192.168.xxx.xxx
        username: xxxxxxxxxxx
        password: xxxxxxxxxxx

        logging_interval: 1.0
        request_timeout: 3.0
        timer_timeout: 300

        api_version: v1
    ```

4. Verify the connection with the following command:

    ```Python console
    >>> from ultimakerpy import UMS3
    >>> UMS3(name='MyPrinterName').is_accessible()
    # True
    ```

## Example: Logging sensor data

```Python
from ultimakerpy import UMS3

printer = UMS3(name='MyPrinterName')
targets = {
    'status': printer.status,
    'head_pos_x': printer.head.position_x,
    'bed_pos': printer.bed.position,
    'nozzle_temp': printer.main_nozzle.temperature,
}

with printer.data_logger('output1.csv', targets) as dl:
    time.sleep(10)  # log for 10 seconds
```

See "component.py" for more methods to get sensor values and to change printer parameters.

## Example: Using timer to time commands

```python
import time
from ultimakerpy import UMS3, JobState

def print_started(state):
    if state == JobState.PRINTING:
        time.sleep(6.0)
        return True
    return False

def layer_reached(pos, n):
    if round(pos / 0.2) >= n:  # set layer pitch: 0.2 mm
        return True
    return False

printer = UMS3(name='MyPrinterName')
targets = {
    'job_state': printer.job_state,
    'bed_pos': printer.bed.position,
}

printer.print_from_dialog()  # select file to print
with printer.data_logger('output2.csv', targets) as dl:
    timer = dl.get_timer()

    # sleep until active leveling finishes
    timer.wait_for_datalog('job_state', print_started)

    for n in range(1, 101):
        # sleep until the printing of specified layer to start
        timer.wait_for_datalog('bed_pos', lambda v: layer_reached(v, n))
        print('printing layer:', n)
```


**Author:** Kota AONO  
**License:** Apache License 2.0
