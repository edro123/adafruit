# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
This code was intiially based on"
    an adafruit example: https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/temperature-logger-example
    ...
"""

from adafruit_funhouse import FunHouse

funhouse = FunHouse(default_bg=None)

DELAY = 180
TEMPERATURE_OFFSET = (
    -3  # Degrees C to adjust the temperature to compensate for board produced heat
)

PRESSURE_OFFSET = (
    0  # mm Hg to adjustment to calibrate the pressure sensor
)

HUMIDITY_OFFSET = (
    10  # mm Hg to adjustment to calibrate the humidity sensor
)

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.display.brightness = 0
funhouse.network.enabled = False

def log_data():
    print("---------------------")
    print("Temperature %0.1F" % (funhouse.peripherals.temperature + TEMPERATURE_OFFSET)*9 / 5 - 32)
    print("Humidity %0.1F" % (funhouse.peripherals.relative_humidity + HUMIDITY_OFFSET))
    print("Pressure %0.1F" % (funhouse.peripherals.pressure) + PRESSURE_OFFSET)
    print("Light %0.1F" % (funhouse.peripherals.light))
    # Turn on WiFi
    funhouse.network.enabled = True
    # Connect to WiFi
    funhouse.network.connect()
    # Push to IO using REST
    funhouse.push_to_io("temperature", funhouse.peripherals.temperature - TEMPERATURE_OFFSET)
    funhouse.push_to_io("humidity", funhouse.peripherals.relative_humidity)
    funhouse.push_to_io("pressure", funhouse.peripherals.pressure)
    funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
    # Turn off WiFi
    funhouse.network.enabled = False


while True:
    log_data()
    print("Sleeping for {} seconds...".format(DELAY))
    funhouse.enter_light_sleep(DELAY)
