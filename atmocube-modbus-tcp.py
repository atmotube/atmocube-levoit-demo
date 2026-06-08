import asyncio

from pyvesync import VeSync
from pymodbus.client import ModbusTcpClient

from local_settings import (
    LEVOIT_EMAIL,
    LEVOIT_PASSWORD,
    ATMOCUBE_IP,
    ATMOCUBE_IP_PORT,
)

# pyvesync 3.x uses a country code, not a timezone, as the 3rd positional arg.
# Keep timezone explicit as a keyword argument.
VESYNC_COUNTRY_CODE = "US"
VESYNC_TIME_ZONE = "America/New_York"

PM25_OFF_THRESHOLD = 10
PM25_ON_THRESHOLD = 20


def get_current_fan_level(purifier):
    """Return the current purifier fan level for pyvesync 3.x devices."""
    state = getattr(purifier, "state", None)
    if state is not None:
        return getattr(state, "fan_level", None) or getattr(state, "fan_set_level", None)

    return getattr(purifier, "fan_level", None)


async def change_fan_level(purifier, fan_level):
    current_fan_level = get_current_fan_level(purifier)

    if current_fan_level != fan_level:
        print("changing fan speed to " + str(fan_level))
        changed = await purifier.set_fan_speed(speed=fan_level)
        if not changed:
            print(
                "failed to change fan speed; valid levels may be "
                + str(getattr(purifier, "fan_levels", "unknown"))
            )


def read_atmocube_pm25(client):
    result = client.read_input_registers(0x0040, count=20)
    available = client.read_discrete_inputs(0x0040, count=20)

    if result.isError():
        raise RuntimeError("Failed to read Atmocube input registers: " + str(result))
    if available.isError():
        raise RuntimeError("Failed to read Atmocube availability bits: " + str(available))

    print("---------------------")
    if available.bits[0] == 1:
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

    if available.bits[12] == 1:
        print("no2 = {:.1f} ppm".format(result.registers[12] / 1000))
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

    return pm25


async def control_purifier_from_pm25(purifier, pm25):
    # Refresh purifier state before making decisions.
    await purifier.update()

    if pm25 < PM25_OFF_THRESHOLD:
        if purifier.is_on:
            print("turning off air purifier")
            await purifier.turn_off()
        return

    if pm25 <= PM25_ON_THRESHOLD:
        return

    if not purifier.is_on:
        print("turning on air purifier")
        await purifier.turn_on()
        await purifier.update()

    if pm25 < 50:
        await change_fan_level(purifier, 1)
    elif pm25 < 140:
        await change_fan_level(purifier, 2)
    else:
        await change_fan_level(purifier, 3)


async def main():
    async with VeSync(
        username=LEVOIT_EMAIL,
        password=LEVOIT_PASSWORD,
        country_code=VESYNC_COUNTRY_CODE,
        time_zone=VESYNC_TIME_ZONE,
    ) as manager:
        await manager.login()
        if not manager.enabled:
            print("VeSync login failed")
            return

        await manager.get_devices()
        await manager.update()

        purifiers = manager.devices.air_purifiers
        if not purifiers:
            print("purifier is not found")
            return

        levoit_200s = purifiers[0]
        await levoit_200s.update()

        print("Found device: " + levoit_200s.device_name)
        print("is_on = " + str(levoit_200s.is_on))
        print("state = " + str(getattr(levoit_200s, "state", None)))
        print("features = " + str(getattr(levoit_200s, "features", None)))
        print("modes = " + str(getattr(levoit_200s, "modes", None)))
        print("fan_levels = " + str(getattr(levoit_200s, "fan_levels", None)))

        client = ModbusTcpClient(ATMOCUBE_IP, port=ATMOCUBE_IP_PORT)
        try:
            if not client.connect():
                print("failed to connect to Atmocube Modbus TCP")
                return

            while True:
                pm25 = read_atmocube_pm25(client)
                await control_purifier_from_pm25(levoit_200s, pm25)
                await asyncio.sleep(1)
        finally:
            client.close()


if __name__ == "__main__":
    asyncio.run(main())
