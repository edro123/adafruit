# Write your code here :-)
# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
This code was intiially based on
    adafruit example: https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/temperature-logger-example
    ...
"""

import time
from adafruit_funhouse import FunHouse
import board
#import busio
import adafruit_sgp30
import microcontroller

# Constants:

DARK_LIMIT = 500 # nighlight mode on if light level below this

HUMIDITY_MULTIPLIER = (
    1.48  # % Multiplier to match the RH to a reference
)
HUMIDITY_LOW = 45 
HUMIDITY_HIGH = 55

TEMPERATURE_MULTIPLIER = (
    0.864  # Multiplier to match the temperature to reference
    # Access the cpu temp and model a dynamic offset?
)
TEMPERATURE_LOW = 62
TEMPERATURE_HIGH = 80

PRESSURE_OFFSET = (
    1  # mm Hg to adjust the pressure to match a reference
)

CO2_MULTIPLIER = (
    0.35  # multiplier to match CO2 value to Netatmo
)
CO2_ERROR = 400
CO2_LOW = 1000
CO2_HIGH = 2000

VOC_OFFSET = (
    0  # PPM to adjust the VOC value to match a reference
)
VOC_LOW = 10
VOC_HIGH = 2500

IO_queue = ""
def add_to_IO_queue(message, print_it_too):
    global IO_queue
    # if IO_queue is not empty: add a new line
    IO_queue = message if IO_queue == "" else IO_queue + "\n" + message
    if print_it_too: print("IO_queue is now: " + message)

funhouse = FunHouse(default_bg=None)

# Initialize the SGP 30 VOC/CO2 board
#See this link for how to handle the i2c bus on the funhouse board: https://circuitpython.readthedocs.io/projects/funhouse/en/latest/
try:
    i2c = board.I2C()
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()

    if funhouse.peripherals.button_sel:
        SGP30_CALIBRATING = True
        add_to_IO_queue("SGP30 present and select switch pressed on startup: start calibration.", False)
    else:
        SGP30_CALIBRATING = False
        #load baseline calibration data (eCO2, TVOC)
        # factory numbers: sgp30.set_iaq_baseline(0x8973, 0x8AAE)
        # 1/10/22 indoor / outdoor: sgp30.set_iaq_baseline(0x8DFC, 0x91EE)
        # 1/11/22 outdoor:
        sgp30.set_iaq_baseline(0x9872, 0x98D7)
        add_to_IO_queue("SGP30 Present and initialized.", False)
    SGP30_PRESENT = True
except:
    add_to_IO_queue("SGP30 initializing error: do not use.", False)
    SGP30_PRESENT = False
    SGP30_CALIBRATING = False

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
    elif parameter == "voc" and SGP30_PRESENT:
        #dots[4] - VOC: color varies with level, blue - green - red
        if measurement > VOC_HIGH: funhouse.peripherals.dotstars[1] = (LED_bright, 0, 0)
        elif measurement > VOC_LOW: funhouse.peripherals.dotstars[1] = (0, LED_bright, 0)
        else: funhouse.peripherals.dotstars[1] = (0, 0, LED_bright)
    elif parameter == "temperature":
        #dots[3] - temperature: blue   -   green   -   yellow
        if measurement < TEMPERATURE_LOW: funhouse.peripherals.dotstars[3] = (0, 0, LED_bright)
        elif measurement > TEMPERATURE_HIGH: funhouse.peripherals.dotstars[3] = (LED_bright, 0, 0)
        else: funhouse.peripherals.dotstars[3] = (0, LED_bright, 0)
    elif parameter == "humidity":
        #dots[1] - humidity: orange   -   green   -   red
        if measurement < HUMIDITY_LOW: funhouse.peripherals.dotstars[4] = (LED_bright, LED_dim, 0)
        elif measurement > HUMIDITY_HIGH: funhouse.peripherals.dotstars[4] = (LED_bright, 0, 0)
        else: funhouse.peripherals.dotstars[4] = (0, LED_bright, 0)
    else:
        print("set_dotstar parameter mismatch")

def sensor_update(motion_detected, IO_update, save_sgp30_cals):
    global IO_queue
    print("---------------------")

    if SGP30_PRESENT:
        co2 = max(CO2_MULTIPLIER * sgp30.eCO2, 418)
        voc = sgp30.TVOC + VOC_OFFSET
        print ("0 - CO2 " + str(co2))
        set_dotstar("co2", co2)
        print("1 - VOC " + str(voc))
        set_dotstar("voc", voc)
    else:
        funhouse.peripherals.dotstars[0] = (0, 0, 0)
        funhouse.peripherals.dotstars[1] = (0, 0, 0)

    print("2 - PIR " + str(motion_detected))

    cal_temperature_F = (TEMPERATURE_MULTIPLIER * funhouse.peripherals.temperature * 9 / 5 + 32)
    print("3 - Temperature %0.1F" % (cal_temperature_F))
    set_dotstar("temperature", cal_temperature_F)

    cal_humidity = HUMIDITY_MULTIPLIER * funhouse.peripherals.relative_humidity
    print("4 - Humidity %0.1F" % (cal_humidity))
    set_dotstar("humidity", cal_humidity)

    cal_pressure = funhouse.peripherals.pressure + PRESSURE_OFFSET
    print("Pressure %0.1F" % (cal_pressure))

    print("Light %0.1F" % (funhouse.peripherals.light))

    cpu_temp_F = microcontroller.cpu.temperature * 9 / 5 + 32
    print("CPU temperature " + str(cpu_temp_F))

    # Turn on WiFi
    if IO_update:
        funhouse.peripherals.led = True
        try:
            funhouse.network.enabled = True
            # Connect to WiFi
            funhouse.network.connect()
            # Push to IO using REST
        except:
            add_to_IO_queue("WiFi error - check secrets file!", True)
            # Turn off WiFi, but leave red led on to indicate IO error
            #funhouse.peripherals.led = False
            funhouse.network.enabled = False
            return
        try:
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
                    print(co2_base_string)
                    tvoc_base_string = "tvoc_base: " + str(tvoc_base)
                    funhouse.push_to_io("text", tvoc_base_string)
                    print(tvoc_base_string)
                    """
                    Normally the file system is read only. See this link - https://learn.adafruit.com/cpu-temperature-logging-with-circuit-python/writing-to-the-filesystem
                    with open("sgp30_cal_data.txt", "a") as f:
                        f.write(co2_base_string)
                        f.write(tvoc_base_string)
                    """
            else:
                funhouse.push_to_io("co2", 0)
                funhouse.push_to_io("voc", 0)
            funhouse.push_to_io("pir", motion_detected)
            funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
            funhouse.push_to_io("cputemp", cpu_temp_F)
            # push IO_queue to text IO feed then clear it
            if IO_queue != "":
                try:
                    print("IO text feed: \n" + IO_queue)
                    funhouse.push_to_io("text", IO_queue)
                except:
                    print("Error pushing to IO text feed")
                    print("Error text was " + IO_queue)
                IO_queue = ""
            else:
                print("IO_queue is empty")
        except:
            add_to_IO_queue("IO connect error - check secrets file!", True)
            # Turn off WiFi, but leave red led on to indicate IO error
            #funhouse.peripherals.led = False
            funhouse.network.enabled = False
            return
        # Turn off WiFi
        funhouse.peripherals.led = False
        funhouse.network.enabled = False
        print("Push to IO complete")

# Timing defaults to low power values
SGP30_CAL_DATA_SAVE_INTERVAL = 3600 # in seconds, only in calibrate mode
FAST_IO_UPDATE_INTERVAL = 30 # Dashboard / web update interval in seconds
FAST_SLEEP_INTERVAL = 0.2 # light sleep time for each loop

IO_update_interval = 10 * FAST_IO_UPDATE_INTERVAL
sleep_interval = 10 * FAST_SLEEP_INTERVAL
funhouse.display.brightness = 0.25
print("Slow update mode on startup")

IO_update_time = time.time() - IO_update_interval
SGP30_cal_data_save_time = time.time() - SGP30_CAL_DATA_SAVE_INTERVAL

PIR_motion_detected = 0
add_to_IO_queue("Funhouse start up complete", False)
while True:
    if PIR_motion_detected == 0 and funhouse.peripherals.pir_sensor:
        PIR_motion_detected = 1
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
        sensor_update(PIR_motion_detected, False, False)
    if time.time() - IO_update_time > IO_update_interval:
        if SGP30_CALIBRATING and (time.time() - SGP30_cal_data_save_time > SGP30_CAL_DATA_SAVE_INTERVAL):
            sensor_update(PIR_motion_detected, True, True)
            SGP30_cal_data_save_time = time.time()
        else:
            sensor_update(PIR_motion_detected, True, False)
        IO_update_time = time.time()
        PIR_motion_detected = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)

    funhouse.enter_light_sleep(sleep_interval)

    if funhouse.peripherals.button_up:
        # set to fast mode
        IO_update_interval = FAST_IO_UPDATE_INTERVAL
        sleep_interval = FAST_SLEEP_INTERVAL
        funhouse.display.brightness = 0.25
        print("Switch to fast update")
        sensor_update(PIR_motion_detected, False, False)
        IO_update_time = time.time()
    elif funhouse.peripherals.button_down:
        # set to slow mode
        IO_update_interval = 10 * FAST_IO_UPDATE_INTERVAL
        sleep_interval = 10 * FAST_SLEEP_INTERVAL
        funhouse.display.brightness = 0
        print("Switch to slow update")
        sensor_update(PIR_motion_detected, True, False)
        IO_update_time = time.time()
