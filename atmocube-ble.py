import time
from bleak import BleakScanner
import asyncio
import threading
from local_settings import ATMOCUBE_BLE_NAME


async def ble():
    stop_event = asyncio.Event()

    def callback(device, advertising_data):
        if device.name == ATMOCUBE_BLE_NAME:
            data = advertising_data.manufacturer_data[0xFFFF]
            if len(data) != 34:
                return
            print("---------------------")
            if data[0] == 1:
                # packet v1
                voc_ppb = int.from_bytes(bytearray([data[1], data[2]]), "little")
                print("TVOC = {:.2f} ppm".format(voc_ppb / 1000))
            elif data[0] == 2:
                # packet v2
                print("VOC index = {:d}".format(int(data[1])))
                print("NOx index = {:d}".format(int(data[2])))
            print("PM1 = {:.1f} ug/m3".format(int.from_bytes(bytearray([data[20], data[21]]), "little") / 10))
            print("PM2.5 = {:.1f} ug/m3".format(int.from_bytes(bytearray([data[3], data[4]]), "little") / 10))
            print("PM10 = {:.1f} ug/m3".format(int.from_bytes(bytearray([data[5], data[6]]), "little") / 10))
            print("t = {:.2f} C".format(int.from_bytes(bytearray([data[7], data[8]]), "little") / 100))
            print("h = {:.2f} %".format(int.from_bytes(bytearray([data[9], data[10]]), "little") / 100))
            print("CO2 = {:d} ppm".format(int.from_bytes(bytearray([data[11], data[12]]), "little")))
            print("p = {:.1f} mbar".format(int.from_bytes(bytearray([data[13], data[14], data[15], data[16]]), "little") / 100))
            print("noise = {:d} dBa".format(int(data[17])))
            print("light = {:d} Lux".format(int.from_bytes(bytearray([data[18], data[19]]), "little")))
            if data[22] != 0xFF and data[23] != 0xFF:
                print("CH2O = {:.1f} ppm".format(int.from_bytes(bytearray([data[22], data[23]]), "little") / 1000))
            if data[25] != 0xFF and data[26] != 0xFF:
                print("CO = {:.1f} ppm".format(int.from_bytes(bytearray([data[25], data[26]]), "little") / 1000))
            if data[27] != 0xFF and data[28] != 0xFF:
                print("O3 = {:.1f} ppm".format(int.from_bytes(bytearray([data[27], data[28]]), "little") / 1000))
            print("FW = {:s}.{:s}.{:s}.{:s}".format(str(data[32]), str(data[31]), str(data[30]), str(data[29])))

    async with BleakScanner(callback) as scanner:
        await stop_event.wait()

asyncio.run(ble())
