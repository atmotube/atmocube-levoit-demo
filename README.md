# Atmocube integration demo
Demo integration Atmocube Air Quality monitor + Levoit Air Purifier

This demo demonstrates how to use Atmocube local interfaces and get the air quality data to control purifier via cloud API.

The following interfaces are demonstrated:
- Modbus TCP
- Modbus RTU
- BLE

## Modbus TCP + Levoit 200S demo
Make sure Modbus TCP is enabled via [Atmocube configuration tool](https://atmotube.com/atmocube-support/modbus-setup-guide).

Installation (Python 3.10):

    pip install pyvesync
    pip install pymodbus

Create `local_settings.py` with the following parameters

    ATMOCUBE_IP = '192.168.1.149' #set your real Atmocube IP here
    ATMOCUBE_IP_PORT = 502
    LEVOIT_EMAIL = '[email]' #set levoit account email
    LEVOIT_PASSWORD = '[password]' #set levoit account password
Run script

    python atmocube-modbus-tcp.py
Output should be the following:

    Found device: Air Purifier
    is_on = False
    details = {'filter_life': 0, 'mode': 'manual', 'level': 0, 'display': False, 'child_lock': False, 'night_light': 'off'}
    features = []
    modes = ['sleep', 'off', 'manual']
    ---------------------
    TVOC = 0.07 ppm
    PM1 = 3.4 ug/m3
    PM2.5 = 3.6 ug/m3
    PM4 = 3.6 ug/m3
    PM10 = 3.6 ug/m3
    CO2 = 1233 ppm
    t = 22.67 C
    h = 72.08 %
    abs_h = 14 g/m3
    p = 1019.2 mbar
    noise = 43 dBa
    light = 240 Lux
    co = 0.0 ppm
    o3 = 0.0 ppm
    ch2o = 0.0 ppm

## Modbus RTU
Make sure Modbus RTU is enabled via [Atmocube configuration tool](https://atmotube.com/atmocube-support/modbus-setup-guide).

Connect RS485<>USB cable to Atmocube. Check the serial port number. It should be `COM[x]` for Windows or `/dev/[x]` for Linux/MacOS.

|RS-485|Atmocube|
|--|--|
|GND|GND|
|TXD+|A|
|TXD-|B|

<img src="https://github.com/atmotube/atmocube-levoit-demo/blob/7ee5ef14c6cec39a2943c51078755b050bce9ef9/img/atmocube_modbus_rtu.jpg?raw=true" alt= "Atmocube RS-485 connection" width="300">

Installation (Python 3.10):

    pip install pymodbus

Create `local_settings.py` with the following parameters

    ATMOCUBE_RTU_PORT = '/dev/cu.usbserial-AQ027VNZ' #set your serial port name here
    ATMOCUBE_RTU_DEVICE_ID = 10 #modify id according to Atmocube configuration tool
    ATMOCUBE_RTU_BAUDRATE = 115200
    ATMOCUBE_RTU_DATA_BITS = 8
    ATMOCUBE_RTU_PARITY = 'N'
    ATMOCUBE_RTU_STOP_BITS = 1 

Run script

    python atmocube-modbus-rtu.py
Output should be the following:

    ---------------------
    TVOC = 0.07 ppm
    PM1 = 2.7 ug/m3
    PM2.5 = 3.6 ug/m3
    PM4 = 4.2 ug/m3
    PM10 = 4.5 ug/m3
    CO2 = 1338 ppm
    t = 22.24 C
    h = 72.72 %
    abs_h = 14 g/m3
    p = 1018.0 mbar
    noise = 39 dBa
    light = 53 Lux
    ch2o = 0.0 ppm
## BLE (Bluetooth advertising)
Installation (Python 3.10):

```
pip install bleak
```
On MacOS installation may be tricky. You have to modify `Info.plist` for terminal app. [See Bleak troubleshooting](https://bleak.readthedocs.io/en/latest/troubleshooting.html).

Create `local_settings.py` with the following parameters

    ATMOCUBE_BLE_NAME = 'CUBE_004C' #set your Atmocube device BLE name CUBE_[last 4 MAC address characters]

Run script

    python atmocube-ble.py
Output should be the following:

    ---------------------
    TVOC = 0.10 ppm
    PM1 = 3.3 ug/m3
    PM2.5 = 3.5 ug/m3
    PM10 = 3.5 ug/m3
    t = 22.68 C
    h = 72.09 %
    CO2 = 1328 ppm
    p = 1019.3 mbar
    noise = 43 dBa
    light = 240 Lux
    CH2O = 0.0 ppm
    CO = 0.0 ppm
    O3 = 0.0 ppm
    FW = 1.10.1.29
