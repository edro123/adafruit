# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
This code was intiially based on"
    adafruit example: https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/temperature-logger-example
    ...
"""

from adafruit_funhouse import FunHouse
import time
import board

funhouse = FunHouse(default_bg=None)

DELAY = 180
TEMPERATURE_OFFSET = (
    -4  # Degrees F to adjust the temperature to compensate for board produced heat
    # Access the cpu temp and model a dynamic offset?
)

PRESSURE_OFFSET = (
    1  # mm Hg to adjustment to calibrate the pressure sensor
)

HUMIDITY_OFFSET = (
    14  # mm Hg to adjustment to calibrate the humidity sensor
)

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.network.enabled = False

def log_data(save_pir):
    funhouse.peripherals.led = True
    cal_temperature_F = (funhouse.peripherals.temperature * 9 / 5 + 32 + TEMPERATURE_OFFSET)
    cal_humidity = funhouse.peripherals.relative_humidity + HUMIDITY_OFFSET
    cal_pressure = funhouse.peripherals.pressure + PRESSURE_OFFSET
    print("---------------------")
    print("Temperature %0.1F" % (cal_temperature_F))
    print("Humidity %0.1F" % (cal_humidity))
    print("Pressure %0.1F" % (cal_pressure))
    print("Light %0.1F" % (funhouse.peripherals.light))
    print("PIR " + str(save_pir))
    # Turn on WiFi
    funhouse.network.enabled = True
    # Connect to WiFi
    funhouse.network.connect()
    # Push to IO using REST
    funhouse.push_to_io("temperature", cal_temperature_F)
    funhouse.push_to_io("humidity", cal_humidity)
    funhouse.push_to_io("pressure", cal_pressure)
    funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
    funhouse.push_to_io("pir", save_pir)
    # Turn off WiFi
    funhouse.network.enabled = False
    funhouse.peripherals.led = False

save_time = time.time() - DELAY
save_pir = 0
while True:
    if save_pir == 0 and funhouse.peripherals.pir_sensor:
        save_pir = 1
        print("PIR Motion detected!")
        funhouse.peripherals.dotstars[2] = (16, 16, 16)
    slider = funhouse.peripherals.slider
    if slider is not None: funhouse.display.brightness = slider
    if time.time() - save_time > DELAY:
        log_data(save_pir)
        save_time = time.time()
        save_pir = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)
    else:
        funhouse.enter_light_sleep(0.5)
