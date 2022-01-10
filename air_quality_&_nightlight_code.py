# Write your code here :-)
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
IO_UPDATE_INTERVAL = 180 # Dashboard / web update interval in seconds
SGP30_CAL_DATA_SAVE_INTERVAL = 3600 # in seconds, only in calibrate mode

DARK_LIMIT = 500 # nighlight mode on if light level below this

HUMIDITY_OFFSET = (
    11  # mm Hg to adjust the humidity sensor to match a reference
)
HUMIDITY_LOW = 45
HUMIDITY_HIGH = 58

TEMPERATURE_OFFSET = (
    -5.5  # Degrees F to adjust the temperature to compensate for board produced heat
    # Access the cpu temp and model a dynamic offset?
)
TEMPERATURE_LOW = 65
TEMPERATURE_HIGH = 78

PRESSURE_OFFSET = (
    1  # mm Hg to adjust the pressure to match a reference
)

CO2_OFFSET = (
    0  # PPM to adjust the CO2 value to match a reference
)
CO2_ERROR = 390
CO2_LOW = 1000
CO2_HIGH = 2500

VOC_OFFSET = (
    0  # PPM to adjust the VOC value to match a reference
)
VOC_LOW = 10
VOC_HIGH = 100

funhouse = FunHouse(default_bg=None)


SGP30_PRESENT = True

# Initialize the SGP 30 VOC/CO2 board
#See this link for how to handle the i2c bus on the funhouse board: https://circuitpython.readthedocs.io/projects/funhouse/en/latest/
if SGP30_PRESENT:
    # initialize the sgpl30
    i2c = board.I2C()
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()

    if funhouse.peripherals.button_down:
        print("Down switch pressed on startup, and SGP30_PRESENT: start calibration")
        SGP30_CALIBRATED = False
    else:
        SGP30_CALIBRATED = True
        #load baseline calibration data
        sgp30.set_iaq_baseline(0x8973, 0x8AAE)

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

def sensor_update(motion_detected, IO_update, save_sgp30_cals):
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
        co2 = sgp30.eCO2 + CO2_OFFSET
        voc = sgp30.TVOC + VOC_OFFSET
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
            if save_sgp30_cals:
                co2_base = sgp30.baseline_eCO2
                tvoc_base = sgp30.baseline_TVOC
                co2_base_string = "co2eq_base: " + str(co2_base)
                funhouse.push_to_io("text", co2_base_string)
                tvoc_base_string = "tvoc_base: " + str(tvoc_base)
                funhouse.push_to_io("text", tvoc_base_string)
                with open("sgp30_cal_data.txt", a) as f:
                    f.write(co2_base_string)
                    f.write(tvoc_base_string)
        else:
            funhouse.push_to_io("co2", 0)
            funhouse.push_to_io("voc", 0)
        funhouse.push_to_io("pir", motion_detected)
        funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
        funhouse.push_to_io("cputemp", cpu_temp_F)
        # Turn off WiFi
        funhouse.network.enabled = False
    funhouse.peripherals.led = False

IO_update_time = time.time() - IO_UPDATE_INTERVAL
SGP30_cal_data_save_time = time.time() - SGP30_CAL_DATA_SAVE_INTERVAL

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
        sensor_update(motion_detected, False, up_button_pressed)
    if time.time() - IO_update_time > IO_UPDATE_INTERVAL:
        if not SGP30_CALIBRATED and (time.time() - SGP30_cal_data_save_time > SGP30_CAL_DATA_SAVE_INTERVAL):
            sensor_update(motion_detected, True, True)
            SGP30_cal_data_save_time = time.time()
        else:
            sensor_update(motion_detected, True, False)
        IO_update_time = time.time()
        motion_detected = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)
    else:
        funhouse.enter_light_sleep(0.5)
