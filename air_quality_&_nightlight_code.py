"""
This code was intiially based on an adafruit example:
https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/temperature-logger-example
"""

import time
from adafruit_funhouse import FunHouse
import board
import adafruit_sgp30
import microcontroller

# Set controls:
ADJUST_RAW_VALUES = True

#  Timing constants
SGP30_CAL_DATA_SAVE_INTERVAL = 3600  # in seconds, only in calibrate mode
FAST_IO_UPDATE_INTERVAL = 60  # Fast IO web update interval in seconds
FAST_SLEEP_INTERVAL = 0.2  # fast loop sleep time
NORMAL_IO_UPDATE_INTERVAL = 600  # normal IO web update interval in seconds
NORMAL_SLEEP_INTERVAL = 1  # normal loop sleep time

# Set Constants:

DARK_THRESHOLD = 420  # nighlight mode on if light level below this

HUMIDITY_SCALE = (
    1  # % Multiplier to match the RH to a reference
)
HUMIDITY_OFFSET = (
    15.6  # % Offset to match the RH to a reference
)
HUMIDITY_LOW = 45
HUMIDITY_HIGH = 55

TEMPERATURE_SCALE = (
    1  # Multiplier to match the temperature to reference
)
TEMPERATURE_OFFSET = (
    -11.9  # % Offset to match the temperature to a reference
)
TEMPERATURE_LOW = 62
TEMPERATURE_HIGH = 80

PRESSURE_SCALE = (
    1  # Multiplier to match the temperature to reference
)
PRESSURE_OFFSET = (
    -1.6  # mm Hg to adjust the pressure to match a reference
)

CO2_SCALE = (
    1  # multiplier to match CO2 value to Netatmo
)
CO2_OFFSET = (
    0  # % Offset to match the co2 to a reference
)
CO2_ERROR = 400
CO2_LOW = 1000
CO2_HIGH = 2000

VOC_SCALE = (
    1  # multiplier to match CO2 value to Netatmo
)
VOC_OFFSET = (
    0  # PPM to adjust the VOC value to match a reference
)
VOC_LOW = 10
VOC_HIGH = 2500

io_queue = ""


def add_to_io_queue(message, print_it_too):
    global io_queue
    # if io_queue is not empty: add a new line
    io_queue = message if io_queue == "" else io_queue + "\n" + message
    if print_it_too:
        print(message)


funhouse = FunHouse(default_bg=None)

# Initialize the SGP 30 VOC/CO2 board
# See this link for how to handle the i2c bus on the funhouse board:
# https://circuitpython.readthedocs.io/projects/funhouse/en/latest/
try:
    i2c = board.I2C()
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()

    if funhouse.peripherals.button_sel:
        SGP30_CALIBRATING = True
        add_to_io_queue("SGP30 present - calibration mode.", True)
    else:
        SGP30_CALIBRATING = False
        # load baseline calibration data (eCO2, TVOC)
        # factory numbers: sgp30.set_iaq_baseline(0x8973, 0x8AAE)
        # 1/10/22 indoor / outdoor: sgp30.set_iaq_baseline(0x8DFC, 0x91EE)
        # 1/11/22 outdoor:
        sgp30.set_iaq_baseline(0x9872, 0x98D7)
        add_to_io_queue("SGP30 Present - initialized.", True)
    SGP30_PRESENT = True
except RuntimeError:
    add_to_io_queue("SGP30 initializing error: do not use.", True)
    SGP30_PRESENT = False
    SGP30_CALIBRATING = False

# Turn things off
funhouse.peripherals.dotstars.fill(0)
funhouse.network.enabled = False


def set_dotstar(parameter, measurement):
    led_bright = int(255 * funhouse.display.brightness)
    led_dim = int(64 * funhouse.display.brightness)
    if parameter == "co2" and SGP30_PRESENT:
        # dots[0] - co2: color varies with level: yellow - blue - green  - red
        if measurement > CO2_HIGH:
            funhouse.peripherals.dotstars[0] = (led_bright, 0, 0)
        elif measurement > CO2_LOW:
            funhouse.peripherals.dotstars[0] = (0, led_bright, 0)
        elif measurement > CO2_ERROR:
            funhouse.peripherals.dotstars[0] = (0, 0, led_bright)
        else:
            funhouse.peripherals.dotstars[0] = (led_bright, led_bright, 0)
    elif parameter == "voc" and SGP30_PRESENT:
        # dots[4] - VOC: color varies with level, blue - green - red
        if measurement > VOC_HIGH:
            funhouse.peripherals.dotstars[1] = (led_bright, 0, 0)
        elif measurement > VOC_LOW:
            funhouse.peripherals.dotstars[1] = (0, led_bright, 0)
        else:
            funhouse.peripherals.dotstars[1] = (0, 0, led_bright)
    elif parameter == "temperature":
        # dots[3] - temperature: blue   -   green   -   yellow
        if measurement < TEMPERATURE_LOW:
            funhouse.peripherals.dotstars[3] = (0, 0, led_bright)
        elif measurement > TEMPERATURE_HIGH:
            funhouse.peripherals.dotstars[3] = (led_bright, 0, 0)
        else:
            funhouse.peripherals.dotstars[3] = (0, led_bright, 0)
    elif parameter == "humidity":
        # dots[1] - humidity: orange   -   green   -   red
        if measurement < HUMIDITY_LOW:
            funhouse.peripherals.dotstars[4] = (led_bright, led_dim, 0)
        elif measurement > HUMIDITY_HIGH:
            funhouse.peripherals.dotstars[4] = (led_bright, 0, 0)
        else:
            funhouse.peripherals.dotstars[4] = (0, led_bright, 0)
    else:
        print("set_dotstar parameter mismatch")


def sensor_update(motion_detected, IO_update, save_sgp30_cals):
    global io_queue
    print("---------------------")

    if SGP30_PRESENT:
        co2 = sgp30.eCO2
        voc = sgp30.TVOC
        if ADJUST_RAW_VALUES:
            # co2 = max(co2 * CO2_SCALE + CO2_OFFSET, 418)
            voc = voc * VOC_SCALE + VOC_OFFSET
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
    if ADJUST_RAW_VALUES:
        temperature_f = temperature_f * TEMPERATURE_SCALE + TEMPERATURE_OFFSET
        rel_humidity = rel_humidity * HUMIDITY_SCALE + HUMIDITY_OFFSET
        pressure_mb = pressure_mb + PRESSURE_OFFSET + PRESSURE_OFFSET

    print("3 - Temperature %0.1F" % (temperature_f))
    set_dotstar("temperature", temperature_f)

    print("4 - Humidity %0.1F" % (rel_humidity))
    set_dotstar("humidity", rel_humidity)

    print("x - Pressure %0.1F" % (pressure_mb))

    print("x - Light %0.1F" % (funhouse.peripherals.light))

    cpu_temp_f = microcontroller.cpu.temperature * 9 / 5 + 32
    print("x - CPU temperature " + str(cpu_temp_f))

    # Turn on WiFi
    if IO_update:
        funhouse.peripherals.led = True
        try:
            funhouse.network.enabled = True
            # Connect to WiFi
            funhouse.network.connect()
            # Push to IO using REST
        except RuntimeError:
            add_to_io_queue("WiFi error - check secrets file!", True)
            # Turn off WiFi, but leave red led on to indicate IO error
            # funhouse.peripherals.led = False
            funhouse.network.enabled = False
            return
        try:
            funhouse.push_to_io("temperature", temperature_f)
            funhouse.push_to_io("humidity", rel_humidity)
            funhouse.push_to_io("pressure", pressure_mb)
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
                    Normally the file system is read only. See this link:
                    https://learn.adafruit.com/cpu-temperature-logging-with-circuit-python/writing-to-the-filesystem
                    with open("sgp30_cal_data.txt", "a") as f:
                        f.write(co2_base_string)
                        f.write(tvoc_base_string)
                    """
            else:
                funhouse.push_to_io("co2", 0)
                funhouse.push_to_io("voc", 0)
            funhouse.push_to_io("pir", motion_detected)
            funhouse.push_to_io("lightlevel", funhouse.peripherals.light)
            funhouse.push_to_io("cputemp", cpu_temp_f)
            # push io_queue to text IO feed then clear it
            if io_queue != "":
                print("IO text: \n" + io_queue)
                try:
                    funhouse.push_to_io("text", io_queue)
                except RuntimeError:
                    print("Error pushing IO text")
                io_queue = ""
        except RuntimeError:
            add_to_io_queue("IO connect error - check secrets file!", True)
            # Turn off WiFi, but leave red led on to indicate IO error
            # funhouse.peripherals.led = False
            funhouse.network.enabled = False
            return
        # Turn off WiFi
        funhouse.peripherals.led = False
        funhouse.network.enabled = False
        print("Push to IO complete")


# Start up with normal constants
IO_update_interval = NORMAL_IO_UPDATE_INTERVAL
sleep_interval = NORMAL_SLEEP_INTERVAL
funhouse.display.brightness = 0.25
dark_limit = DARK_THRESHOLD

IO_update_time = time.time() - IO_update_interval
SGP30_cal_data_save_time = time.time() - SGP30_CAL_DATA_SAVE_INTERVAL

PIR_motion_detected = 0
print("Funhouse start up complete")
while True:
    # Monitor motion detection every loop
    if PIR_motion_detected == 0 and funhouse.peripherals.pir_sensor:
        PIR_motion_detected = 1
        print("PIR Motion detected!")
        if (funhouse.display.brightness == 0 and funhouse.peripherals.light < dark_limit):
            # Night light mode
            funhouse.peripherals.set_dotstars(0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF)
        else:
            funhouse.peripherals.dotstars[2] = (16, 16, 16)

    # Read co2 sensor every loop - better results?
    if SGP30_PRESENT:
        temp_co2 = sgp30.eCO2
        temp_voc = sgp30.TVOC

    # set TFT display and LED brightness with slider value
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

    funhouse.peripherals.led = False
    funhouse.enter_light_sleep(sleep_interval)
    funhouse.peripherals.led = True

    if funhouse.peripherals.button_up:
        # set to fast mode
        IO_update_interval = FAST_IO_UPDATE_INTERVAL
        sleep_interval = FAST_SLEEP_INTERVAL
        funhouse.display.brightness = 0.25
        add_to_io_queue("Switch to fast updates", True)
        sensor_update(PIR_motion_detected, False, False)
        IO_update_time = time.time()
    elif funhouse.peripherals.button_down:
        # set to slow mode
        IO_update_interval = NORMAL_IO_UPDATE_INTERVAL
        sleep_interval = NORMAL_SLEEP_INTERVAL
        funhouse.display.brightness = 0
        add_to_io_queue("Switch to normal updates", True)
        sensor_update(PIR_motion_detected, True, False)
        IO_update_time = time.time()
    elif funhouse.peripherals.button_sel:
        # Toggle nightlight mode (dark_limit)
        if dark_limit == DARK_THRESHOLD:
            dark_limit = 0
            print("night light mode off")
        else:
            dark_limit = DARK_THRESHOLD
            print("night light mode on")
