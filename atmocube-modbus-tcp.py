from pyvesync import VeSync
from pymodbus.client import ModbusTcpClient
import time
from local_settings import LEVOIT_EMAIL, LEVOIT_PASSWORD, ATMOCUBE_IP, ATMOCUBE_IP_PORT

manager = VeSync(LEVOIT_EMAIL, LEVOIT_PASSWORD, "America/New_York", debug=False)
manager.login()
manager.update()


def change_fan_level(fan, fan_level):
    if fan.fan_level != fan_level:
        print("changing fan speed to " + str(fan_level))
        fan.change_fan_speed(speed=fan_level)


if manager.fans and len(manager.fans) > 0:
    levoit_200s = manager.fans[0]
    print("Found device: " + levoit_200s.device_name)
    print("is_on = " + str(levoit_200s.is_on))
    print("details = " + str(levoit_200s.details))
    print("features = " + str(levoit_200s.features))
    print("modes = " + str(levoit_200s.modes))

    client = ModbusTcpClient(ATMOCUBE_IP, port=ATMOCUBE_IP_PORT)
    while True:
        result = client.read_input_registers(0x0040, 20)
        available = client.read_discrete_inputs(0x0040, 20)
        print("---------------------")
        if (available.bits[0] == 1):
            print("TVOC = {:.2f} ppm".format(result.registers[0] / 1000))
        print("PM1 = {:.1f} ug/m3".format(result.registers[1] / 10))
        pm25 = result.registers[2] / 10
        print("PM2.5 = {:.1f} ug/m3".format(pm25))
        print("PM4 = {:.1f} ug/m3".format(result.registers[3] / 10))
        print("PM10 = {:.1f} ug/m3".format(result.registers[4] / 10))
        print("CO2 = {:d} ppm".format(result.registers[5]))
        print("t = {:.2f} C".format(result.registers[6] / 100))
        print("h = {:.2f} %".format(result.registers[7] / 100))
        print("abs_h = {:d} g/m3".format(result.registers[8]))
        print("p = {:.1f} mbar".format(result.registers[9] / 10))
        print("noise = {:d} dBa".format(result.registers[10]))
        print("light = {:d} Lux".format(result.registers[11]))
        if (available.bits[12] == 1):
            print("no2 = {:.1f} ppm".format(result.registers[12] / 1000))
        if (available.bits[13] == 1):
            print("co = {:.1f} ppm".format(result.registers[13] / 1000))
        if (available.bits[14] == 1):
            print("o3 = {:.1f} ppm".format(result.registers[14] / 1000))
        if (available.bits[15] == 1):
            print("ch2o = {:.1f} ppm".format(result.registers[15] / 1000))
        if (available.bits[17] == 1):
            print("people = {:d}".format(result.registers[17]))
        if (available.bits[18] == 1):
            print("VOC index = {:d}".format(result.registers[18]))
        if (available.bits[19] == 1):
            print("NOx index = {:d}".format(result.registers[19]))
        if pm25 < 10:
            if levoit_200s.is_on:
                print("turning off air purifier")
                levoit_200s.turn_off()
        elif pm25 > 20:
            if not levoit_200s.is_on:
                print("turning on air purifier")
                levoit_200s.turn_on()
            if pm25 < 50:
                change_fan_level(levoit_200s, 1)
            elif pm25 < 140:
                change_fan_level(levoit_200s, 2)
            else:
                change_fan_level(levoit_200s, 3)
        time.sleep(1)
else:
    print("purifier is not found")
