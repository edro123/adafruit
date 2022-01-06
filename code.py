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
import busio
import adafruit_sgp30

# Initialize the SGP 30 VOC/CO2 board
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)

funhouse = FunHouse(default_bg=None)

DELAY = 180 # Dashboard / web update interval in seconds

CO2_ERROR = 390
CO2_LOW = 1000
CO2_HIGH = 2500

HUMIDITY_OFFSET = (
    14  # mm Hg to adjustment to calibrate the humidity sensor
)
HUMIDITY_LOW = 45
HUMIDITY_HIGH = 58

TEMPERATURE_OFFSET = (
    -7.5  # Degrees F to adjust the temperature to compensate for board produced heat
    # Access the cpu temp and model a dynamic offset?
)
TEMPERATURE_LOW = 65
TEMPERATURE_HIGH = 78

PRESSURE_OFFSET = (
    1  # mm Hg to adjustment to calibrate the pressure sensor
)

VOC_LOW = 10
VOC_HIGH = 100

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.network.enabled = False

def set_dotstar(parameter, measurement):
    if funhouse.display.brightness == 0:
        return
    elif parameter == "co2":
        #dots[0] - co2: color varies with level: yellow - blue - green  - red
        if measurement > CO2_HIGH: funhouse.peripherals.dotstars[0] = (64, 0, 0)
        elif measurement > CO2_LOW: funhouse.peripherals.dotstars[0] = (0,64,0)
        elif measurement > CO2_ERROR: funhouse.peripherals.dotstars[0] = (0, 0, 64)
        else: funhouse.peripherals.dotstars[1] = (64, 64, 0) # Calibration problem?
    elif parameter == "humidity":
        #dots[1] - humidity: orange   -   green   -   red
        if measurement < HUMIDITY_LOW: funhouse.peripherals.dotstars[1] = (64,20,0)
        elif measurement > HUMIDITY_HIGH: funhouse.peripherals.dotstars[1] = (64, 0, 0)
        else: funhouse.peripherals.dotstars[1] = (0, 64, 0)
    elif parameter == "temperature":
        #dots[3] - temperature: blue   -   green   -   yellow
        if measurement < TEMPERATURE_LOW: funhouse.peripherals.dotstars[3] = (0, 0, 64)
        elif measurement > TEMPERATURE_HIGH: funhouse.peripherals.dotstars[3] = (64, 0, 0)
        else: funhouse.peripherals.dotstars[3] = (0, 64, 0)
    elif parameter == "voc":
        #dots[4] - VOC: color varies with level, green - yellow - red
        if measurement > VOC_HIGH: funhouse.peripherals.dotstars[4] = (64, 0, 0)
        elif measurement > VOC_LOW: funhouse.peripherals.dotstars[4] = (64,64,0)
        else: funhouse.peripherals.dotstars[4] = (0, 64, 0)
    else:
        print("set_dotstar parameter mismatch")

def sensor_update(save_pir):
    funhouse.peripherals.led = True
    cal_temperature_F = (funhouse.peripherals.temperature * 9 / 5 + 32 + TEMPERATURE_OFFSET)
    cal_humidity = funhouse.peripherals.relative_humidity + HUMIDITY_OFFSET
    cal_pressure = funhouse.peripherals.pressure + PRESSURE_OFFSET
    co2 = sgp30.eCO2
    voc = sgp30.TVOC
    print("---------------------")
    print ("CO2 " + str(co2))
    set_dotstar("co2", co2)
    print("Humidity %0.1F" % (cal_humidity))
    set_dotstar("humidity", cal_humidity)
    print("PIR " + str(save_pir))
    print("Temperature %0.1F" % (cal_temperature_F))
    set_dotstar("temperature", cal_temperature_F)
    print("VOC " + str(voc))
    set_dotstar("voc", voc)
    print("Pressure %0.1F" % (cal_pressure))
    print("Light %0.1F" % (funhouse.peripherals.light))
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
    #set TFT display brightness with slider value
    slider = funhouse.peripherals.slider
    if slider is not None: funhouse.display.brightness = slider
    if funhouse.display.brightness == 0:
        #Turn non-PIR dotstars off if TFT is off
        funhouse.peripherals.dotstars[0] = (0, 0, 0)
        funhouse.peripherals.dotstars[1] = (0, 0, 0)
        funhouse.peripherals.dotstars[3] = (0, 0, 0)
        funhouse.peripherals.dotstars[4] = (0, 0, 0)
    if time.time() - save_time > DELAY:
        sensor_update(save_pir)
        save_time = time.time()
        save_pir = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)
    else:
        funhouse.enter_light_sleep(0.5)
