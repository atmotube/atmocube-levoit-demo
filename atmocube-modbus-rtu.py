from pymodbus.client import ModbusSerialClient
from local_settings import ATMOCUBE_RTU_PORT, ATMOCUBE_RTU_BAUDRATE, ATMOCUBE_RTU_DATA_BITS, ATMOCUBE_RTU_PARITY, ATMOCUBE_RTU_STOP_BITS, ATMOCUBE_RTU_DEVICE_ID
import time


client = ModbusSerialClient(port=ATMOCUBE_RTU_PORT,
                            baudrate=ATMOCUBE_RTU_BAUDRATE,
                            bytesize=ATMOCUBE_RTU_DATA_BITS,
                            parity=ATMOCUBE_RTU_PARITY,
                            stopbits=ATMOCUBE_RTU_STOP_BITS,
                            timeout=1)

while True:
    result = client.read_input_registers(0x003F, 20, slave=ATMOCUBE_RTU_DEVICE_ID)
    available = client.read_discrete_inputs(0x003F, 20, slave=ATMOCUBE_RTU_DEVICE_ID)
    print("---------------------")
    if available.bits[0] == 1:
        print("TVOC = {:.2f} ppm".format(result.registers[0] / 1000))
    print("PM1 = {:.1f} ug/m3".format(result.registers[1] / 10))
    print("PM2.5 = {:.1f} ug/m3".format(result.registers[2] / 10))
    print("PM4 = {:.1f} ug/m3".format(result.registers[3] / 10))
    print("PM10 = {:.1f} ug/m3".format(result.registers[4] / 10))
    print("CO2 = {:d} ppm".format(result.registers[5]))
    print("t = {:.2f} C".format(result.registers[6] / 100))
    print("h = {:.2f} %".format(result.registers[7] / 100))
    print("abs_h = {:d} g/m3".format(result.registers[8]))
    print("p = {:.1f} mbar".format(result.registers[9] / 10))
    print("noise = {:d} dBa".format(result.registers[10]))
    print("light = {:d} Lux".format(result.registers[11]))
    if available.bits[13] == 1:
        print("co = {:.1f} ppm".format(result.registers[13] / 1000))
    if available.bits[14] == 1:
        print("o3 = {:.1f} ppm".format(result.registers[14] / 1000))
    if available.bits[15] == 1:
        print("ch2o = {:.1f} ppm".format(result.registers[15] / 1000))
    if available.bits[17] == 1:
        print("people = {:d}".format(result.registers[17]))
    if available.bits[18] == 1:
        print("VOC index = {:d}".format(result.registers[18]))
    if available.bits[19] == 1:
        print("NOx index = {:d}".format(result.registers[19]))
    time.sleep(1)
client.close()