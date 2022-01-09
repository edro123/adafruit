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
import microcontroller

# Constants:
DELAY = 180 # Dashboard / web update interval in seconds

DARK_LIMIT = 500

SGP30_PRESENT = False

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

# Initialize the SGP 30 VOC/CO2 board
if SGP30_PRESENT:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

    # Create library object on our I2C port
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

    print("SGP30 serial #", [hex(i) for i in sgp30.serial])

    sgp30.iaq_init()
    sgp30.set_iaq_baseline(0x8973, 0x8AAE)
    print("eCO2 = " + str(sgp30.eCO2))
    print("TVOC = " + str(sgp30.TVOC))

funhouse = FunHouse(default_bg=None)

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.network.enabled = False

def set_dotstar(parameter, measurement):
    LED_bright = int(255 * funhouse.display.brightness)
    LED_dim = int(64 * funhouse.display.brightness)
    if parameter == "co2" and SGP30_PRESENT:
        #dots[0] - co2: color varies with level: yellow - blue - green  - red
        if measurement > CO2_HIGH: funhouse.peripherals.dotstars[0] = (LED_bright, 0, 0)
        elif measurement > CO2_LOW: funhouse.peripherals.dotstars[0] = (0, LED_bright, 0)
        elif measurement > CO2_ERROR: funhouse.peripherals.dotstars[0] = (0, 0, LED_bright)
        else: funhouse.peripherals.dotstars[0] = (LED_bright, LED_bright, 0) # Calibration problem?
    elif parameter == "humidity":
        #dots[1] - humidity: orange   -   green   -   red
        if measurement < HUMIDITY_LOW: funhouse.peripherals.dotstars[1] = (LED_bright, LED_dim, 0)
        elif measurement > HUMIDITY_HIGH: funhouse.peripherals.dotstars[1] = (LED_bright, 0, 0)
        else: funhouse.peripherals.dotstars[1] = (0, LED_bright, 0)
    elif parameter == "temperature":
        #dots[3] - temperature: blue   -   green   -   yellow
        if measurement < TEMPERATURE_LOW: funhouse.peripherals.dotstars[3] = (0, 0, LED_bright)
        elif measurement > TEMPERATURE_HIGH: funhouse.peripherals.dotstars[3] = (LED_bright, 0, 0)
        else: funhouse.peripherals.dotstars[3] = (0, LED_bright, 0)
    elif parameter == "voc" and SGP30_PRESENT:
        #dots[4] - VOC: color varies with level, green - yellow - red
        if measurement > VOC_HIGH: funhouse.peripherals.dotstars[4] = (LED_bright, 0, 0)
        elif measurement > VOC_LOW: funhouse.peripherals.dotstars[4] = (LED_bright, LED_bright, 0)
        else: funhouse.peripherals.dotstars[4] = (0, LED_bright, 0)
    else:
        print("set_dotstar parameter mismatch")

def sensor_update(motion_detected, IO_update):
    funhouse.peripherals.led = True
    print("---------------------")
    cal_temperature_F = (funhouse.peripherals.temperature * 9 / 5 + 32 + TEMPERATURE_OFFSET)
    print("Temperature %0.1F" % (cal_temperature_F))
    set_dotstar("temperature", cal_temperature_F)

    cal_humidity = funhouse.peripherals.relative_humidity + HUMIDITY_OFFSET
    print("Humidity %0.1F" % (cal_humidity))
    set_dotstar("humidity", cal_humidity)

    cal_pressure = funhouse.peripherals.pressure + PRESSURE_OFFSET
    print("Pressure %0.1F" % (cal_pressure))

    if SGP30_PRESENT:
        co2 = sgp30.eCO2
        voc = sgp30.TVOC
        print ("CO2 " + str(co2))
        set_dotstar("co2", co2)
        print("VOC " + str(voc))
        set_dotstar("voc", voc)
    else:
        funhouse.peripherals.dotstars[0] = (0, 0, 0)
        funhouse.peripherals.dotstars[4] = (0, 0, 0)

    print("PIR " + str(motion_detected))

    print("Light %0.1F" % (funhouse.peripherals.light))

    cpu_temp_F = microcontroller.cpu.temperature * 9 / 5 + 32
    print("CPU temperature " + str(cpu_temp_F))

    # Turn on WiFi
    if IO_update:
        funhouse.network.enabled = True
        # Connect to WiFi
        funhouse.network.connect()
        # Push to IO using REST
        funhouse.push_to_io("temperature", cal_temperature_F)
        funhouse.push_to_io("humidity", cal_humidity)
        funhouse.push_to_io("pressure", cal_pressure)
        if SGP30_PRESENT:
            funhouse.push_to_io("co2", co2)
            funhouse.push_to_io("voc", voc)
        else:
            funhouse.push_to_io("co2", 0)
            funhouse.push_to_io("voc", 0)
        funhouse.push_to_io("pir", motion_detected)
        funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
        funhouse.push_to_io("cputemp", cpu_temp_F)
        # Turn off WiFi
        funhouse.network.enabled = False
    funhouse.peripherals.led = False

save_time = time.time() - DELAY
motion_detected = 0
while True:
    if motion_detected == 0 and funhouse.peripherals.pir_sensor:
        motion_detected = 1
        print("PIR Motion detected!")
        if funhouse.display.brightness == 0 and funhouse.peripherals.light < DARK_LIMIT:
            #Night light mode
            funhouse.peripherals.set_dotstars(0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF)
        else:
            funhouse.peripherals.dotstars[2] = (16, 16, 16)
    #set TFT display and LED brightness with slider value
    slider = funhouse.peripherals.slider
    if slider is not None: 
        funhouse.display.brightness = slider
        print("Slider changed to " + str(funhouse.display.brightness))
        sensor_update(motion_detected, False)
    if time.time() - save_time > DELAY:
        sensor_update(motion_detected, True)
        save_time = time.time()
        motion_detected = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)
    else:
        funhouse.enter_light_sleep(0.5)
