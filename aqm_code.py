# pylint: disable=invalid-name
"""
This code was intiially based on an adafruit example:
https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/temperature-logger-example
"""
VERSION = "aqm_code.py version 0.1, 1-27-22"

import time
# Make sure secrets.py exists and get this device's ID
try:
    from secrets import secrets
    FUNHOUSE_ID = secrets["funhouse_id"]
except ImportError:
    print("Missing or invalid secrets.py - please correct!")
    raise

from adafruit_funhouse import FunHouse
import board
import adafruit_sgp30
import microcontroller

#  Timing constants
SGP30_CAL_DATA_SAVE_INTERVAL = 3600  # in seconds, only in calibrate mode
FAST_IO_UPDATE_INTERVAL = 60  # Fast IO web update interval in seconds
FAST_SLEEP_INTERVAL = 0.2  # fast loop sleep time
NORMAL_IO_UPDATE_INTERVAL = 600  # normal IO web update interval in seconds
NORMAL_SLEEP_INTERVAL = 1  # normal loop sleep time

# Set Constants:

DARK_THRESHOLD = 420  # nighlight mode on if light level below this

# linear calibration constants: y = Mx + B
HUMIDITY_M = 1.0669
HUMIDITY_B = 13.418

TEMPERATURE_M = 1.2129
TEMPERATURE_B = -29.553

PRESSURE_M = 0.8471
PRESSURE_B = 157.59

CO2_M = 0.2746
CO2_B = 303.48

VOC_M = 1
VOC_B = 0

# LED color control constants
HUMIDITY_BLUE = 42
# HUMIDITY GREEN 42 - 53
HUMIDITY_RED = 53

TEMPERATURE_BLUE = 62
# TEMPERATURE GREEN 62 - 80
TEMPERATURE_RED = 80

CO2_BLUE = 800
# CO2 GREEN 800 - 2500
CO2_RED = 2500

VOC_BLUE = 200
# VOC GREEN 200 - 2500
VOC_RED = 2500


def set_dotstar(parameter, measurement):
    # Use the limit constants to set LED colors
    # red > HIGH, blue < LOW, green > LOW and < HIGH, yellow = error
    led_bright = int(255 * funhouse.display.brightness)
    if parameter == "co2" and SGP30_PRESENT:
        if measurement < 418:
            funhouse.peripherals.dotstars[0] = (led_bright, led_bright, 0)
        elif measurement > CO2_RED:
            funhouse.peripherals.dotstars[0] = (led_bright, 0, 0)
        elif measurement < CO2_BLUE:
            funhouse.peripherals.dotstars[0] = (0, 0, led_bright)
        else:
            # GREEN
            funhouse.peripherals.dotstars[0] = (0, led_bright, 0)
    elif parameter == "voc" and SGP30_PRESENT:
        if measurement == 0:
            funhouse.peripherals.dotstars[1] = (led_bright, led_bright, 0)
        elif measurement > VOC_RED:
            funhouse.peripherals.dotstars[1] = (led_bright, 0, 0)
        elif measurement < VOC_BLUE:
            funhouse.peripherals.dotstars[1] = (0, 0, led_bright)
        else:
            # GREEN
            funhouse.peripherals.dotstars[1] = (0, led_bright, 0)
    elif parameter == "temperature":
        if measurement == 0:
            funhouse.peripherals.dotstars[3] = (led_bright, led_bright, 0)
        elif measurement > TEMPERATURE_RED:
            funhouse.peripherals.dotstars[3] = (led_bright, 0, 9)
        elif measurement < TEMPERATURE_BLUE:
            funhouse.peripherals.dotstars[3] = (0, 0, led_bright)
        else:
            # GREEN
            funhouse.peripherals.dotstars[3] = (0, led_bright, 0)
    elif parameter == "humidity":
        if measurement == 0:
            funhouse.peripherals.dotstars[4] = (led_bright, led_bright, 0)
        elif measurement > HUMIDITY_RED:
            funhouse.peripherals.dotstars[4] = (led_bright, 0, 0)
        elif measurement < HUMIDITY_BLUE:
            funhouse.peripherals.dotstars[4] = (0, 0, led_bright)
        else:
            # GREEN
            funhouse.peripherals.dotstars[4] = (0, led_bright, 0)
    else:
        text_queue.add("set_dotstar parameter mismatch")


def sensor_update(motion_detected, io_update, save_sgp30_cals):
    print("---------------------")

    if SGP30_PRESENT:
        co2 = sgp30.eCO2
        voc = sgp30.TVOC
        if not CALIBRATE:
            co2 = CO2_M * co2 + CO2_B
            voc = VOC_M * voc + VOC_B
        print("0 - CO2 " + str(co2))
        set_dotstar("co2", co2)
        print("1 - VOC " + str(voc))
        set_dotstar("voc", voc)
    else:
        funhouse.peripherals.dotstars[0] = (0, 0, 0)
        funhouse.peripherals.dotstars[1] = (0, 0, 0)

    print("2 - PIR " + str(motion_detected))

    temperature_f = (funhouse.peripherals.temperature * 9 / 5 + 32)
    rel_humidity = funhouse.peripherals.relative_humidity
    pressure_mb = funhouse.peripherals.pressure
    if not CALIBRATE:
        temperature_f = TEMPERATURE_M * temperature_f + TEMPERATURE_B
        rel_humidity = HUMIDITY_M * rel_humidity + HUMIDITY_B
        pressure_mb = PRESSURE_M * pressure_mb + PRESSURE_B

    print("3 - Temperature %0.1F" % (temperature_f))
    set_dotstar("temperature", temperature_f)

    print("4 - Humidity %0.1F" % (rel_humidity))
    set_dotstar("humidity", rel_humidity)

    print("x - Pressure %0.1F" % (pressure_mb))

    print("x - Light %0.1F" % (funhouse.peripherals.light))

    cpu_temp_f = microcontroller.cpu.temperature * 9 / 5 + 32
    print("x - CPU temperature " + str(cpu_temp_f))

    # Turn on WiFi
    if io_update:
        try:
            funhouse.network.enabled = True
            # Connect to WiFi
            funhouse.network.connect()
            try:
                # Push to IO using REST
                funhouse.push_to_io("temperature", temperature_f)
                funhouse.push_to_io("humidity", rel_humidity)
                funhouse.push_to_io("pressure", pressure_mb)
                if SGP30_PRESENT:
                    funhouse.push_to_io("co2", co2)
                    funhouse.push_to_io("voc", voc)
                    if save_sgp30_cals:
                        text_queue.add("co2eq_base: " + str(sgp30.baseline_eCO2))
                        text_queue.add("tvoc_base: " + str(sgp30.baseline_TVOC))
                else:
                    funhouse.push_to_io("co2", 0)
                    funhouse.push_to_io("voc", 0)
                funhouse.push_to_io("pir", motion_detected)
                funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
                funhouse.push_to_io("cputemp", cpu_temp_f)
                # push text_queue to text IO feed then clear it if successfull
                if text_queue.queue() != "":
                    funhouse.push_to_io("text", str(FUNHOUSE_ID) + text_queue.queue())
                    # If successfull, clear the queue . If not, don't and try to send next time
                    text_queue.clear()
                print("Push to IO complete")
            except Exception as e:
                funhouse.peripherals.play_tone(1500, 0.25)
                text_queue.add(str(e) + "\nAdafruit IO error - check secrets file!")
        except Exception as e:
            funhouse.peripherals.play_tone(1500, 0.25)
            text_queue.add(str(e) + "\nWiFi error - check secrets file!")
        funhouse.network.enabled = False


class adafruit_io_text_queue:
    def __init__(self):
        self.count = 0
        self.text_queue = ""


    def add(self, message):
        print(message)
        if len(self.text_queue) > 2047:
            # the text_queue is cleared when pushed to the io text feed
            # if it's grown this large, there must be a (repeating) problem
            # don't add, but keep the current text and hope it will eventually upload
            print("io text queue size limit reached - frozen!")
        else:
            self.count += 1
            # number each message so we can see if any are missing
            self.text_queue = self.text_queue + str(self.count) + ": " + str(message) + "\n"

    def queue(self):
        return self.text_queue

    def clear(self):
        self.text_queue = ""


text_queue = adafruit_io_text_queue()

funhouse = FunHouse(default_bg=None)
# If the select button is pressed on start up, enter calibration mode and use raw sensor values
if funhouse.peripherals.button_sel:
    CALIBRATE = True
    text_queue.add("Select pressed on startup - calibration mode.")
else:
    CALIBRATE = False

# Initialize the SGP 30 VOC/CO2 board
# See this link for how to handle the i2c bus on the funhouse board:
# https://circuitpython.readthedocs.io/projects/funhouse/en/latest/
try:
    i2c = board.I2C()
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    text_queue.add("SGP30 serial #:" + str([hex(i) for i in sgp30.serial]))
    sgp30.iaq_init()

    if CALIBRATE:
        text_queue.add("SGP30 - calibration mode.")
    else:
        # load baseline calibration data (eCO2, TVOC)
        # factory numbers: sgp30.set_iaq_baseline(0x8973, 0x8AAE)
        # 1/10/22 indoor / outdoor: sgp30.set_iaq_baseline(0x8DFC, 0x91EE)
        # 1/11/22 outdoor:
        sgp30.set_iaq_baseline(0x9872, 0x98D7)
        text_queue.add("SGP30 initialized.")
    SGP30_PRESENT = True
except ValueError as e:
    funhouse.peripherals.play_tone(1000, 0.25)
    text_queue.add(str(e) + "\nSGP30 initialize error: Mark offline.")
    SGP30_PRESENT = False

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.network.enabled = False

# Start up with normal constants
io_update_interval = NORMAL_IO_UPDATE_INTERVAL
sleep_interval = NORMAL_SLEEP_INTERVAL
funhouse.display.brightness = 0.25
dark_limit = DARK_THRESHOLD

io_update_time = time.time() - io_update_interval
sgp30_cal_data_save_time = time.time() - SGP30_CAL_DATA_SAVE_INTERVAL

pir_motion_detected = 0
text_queue.add("Start up complete")
text_queue.add("Running software: " + VERSION)
text_queue.add("On Funhouse ID: " + FUNHOUSE_ID)

while True:
    # Monitor motion detection every loop
    if pir_motion_detected == 0 and funhouse.peripherals.pir_sensor:
        pir_motion_detected = 1
        print("PIR Motion detected!")
        if (funhouse.display.brightness == 0 and funhouse.peripherals.light < dark_limit):
            # Night light mode
            funhouse.peripherals.set_dotstars(0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF)
        else:
            funhouse.peripherals.dotstars[2] = (16, 16, 16)

    if time.time() - io_update_time > io_update_interval:
        if CALIBRATE and (time.time() - sgp30_cal_data_save_time > SGP30_CAL_DATA_SAVE_INTERVAL):
            sensor_update(pir_motion_detected, True, True)
            sgp30_cal_data_save_time = time.time()
        else:
            sensor_update(pir_motion_detected, True, False)
        io_update_time = time.time()
        pir_motion_detected = 0
        funhouse.peripherals.dotstars[2] = (0, 0, 0)
    elif SGP30_PRESENT:
        # if we're not doing an IO update, Read co2 sensor every loop (for better results?)
        temp_co2 = sgp30.eCO2
        temp_voc = sgp30.TVOC

    # set TFT display and LED brightness with slider value
    slider = funhouse.peripherals.slider
    if slider is not None and slider != funhouse.display.brightness:
        funhouse.display.brightness = slider
        print("Slider changed to " + str(funhouse.display.brightness))
        sensor_update(pir_motion_detected, False, False)
    # set update rates with up and down buttons
    if funhouse.peripherals.button_up:
        # set to fast mode
        io_update_interval = FAST_IO_UPDATE_INTERVAL
        sleep_interval = FAST_SLEEP_INTERVAL
        funhouse.display.brightness = 0.25
        text_queue.add("Switch to fast updates")
        sensor_update(pir_motion_detected, True, False)
        io_update_time = time.time()
    elif funhouse.peripherals.button_down:
        # set to normal mode
        io_update_interval = NORMAL_IO_UPDATE_INTERVAL
        sleep_interval = NORMAL_SLEEP_INTERVAL
        funhouse.display.brightness = 0
        text_queue.add("Switch to normal updates")
        sensor_update(pir_motion_detected, True, False)
        io_update_time = time.time()
    # Turn night light mode on / off with select button
    elif funhouse.peripherals.button_sel:
        # Toggle nightlight mode (dark_limit)
        if dark_limit == DARK_THRESHOLD:
            dark_limit = 0
            print("night light mode off")
        else:
            dark_limit = DARK_THRESHOLD
            print("night light mode on")

    funhouse.peripherals.led = False
    funhouse.enter_light_sleep(sleep_interval)
    funhouse.peripherals.led = True
