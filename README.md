# Adafruit Funhouse Air Quality Monitor

This project builds an Air Quality Monitor using the Adafruit Funhouse microcontroller, an add on PIR sensor, and an SGP30 carbon dioxide / VOC sensor. The code will read each of the sensors, adjust them with predetermined calibration constants, print the values to the Funstar display, upload them Adafruit IO, and uses the dotstars for status

## Prerequisites

### Hardware
- Adafruit FunHouse - WiFi Home Automation Development Board (https://www.adafruit.com/product/4985)
- Breadboard-friendly Mini PIR Motion Sensor with 3 Pin Header (https://www.adafruit.com/product/4871)
- SGP30 Air Quality Sensor Breakout - VOC and eCO2 - STEMMA QT / Qwiic (https://www.adafruit.com/product/3709)
- Adafruit FunHouse Mounting Plate and Yellow Brick Stand (https://www.adafruit.com/product/4962)

### Software

#### Setting up CircuitPython:
Follow the steps on this page to install CircuitPython: https://learn.adafruit.com/adafruit-funhouse/circuitpython

#### CircuitPython libraries:
The CircuitPython Libraries required for this project are:

Library | Source
---------|----------
adafruit_ahtx0.mpy | https://circuitpython.org/libraries
adafruit_bitmap_font | https://circuitpython.org/libraries
adafruit_bus_device |https://circuitpython.org/libraries
adafruit_display_text | https://circuitpython.org/librarie
adafruit_dotstar.mpy | https://circuitpython.org/libraries
adafruit_dps310.mpy | https://circuitpython.org/libraries
adafruit_fakerequests.mpy | https://circuitpython.org/libraries
adafruit_funhouse | https://circuitpython.org/libraries
adafruit_io | https://circuitpython.org/libraries
adafruit_minimqtt | https://circuitpython.org/libraries
adafruit_portalbase | https://circuitpython.org/libraries
adafruit_register | https://circuitpython.org/libraries
adafruit_requests.mpy | https://circuitpython.org/libraries
adafruit_sgp30.mpy | https://github.com/adafruit/Adafruit_CircuitPython_SGP30/releases
simpleio.mpy | https://circuitpython.org/libraries

#### Source Code
Available on github at: https://github.com/edro123/adafruit

#### Project bundle
You can also install the source code and libraries as a bundle. Download funhouse_aqm_bundle.zip from xxx.

#### Factory reset:
The Adafruit Funhouse comes with an Arduino Self Test Example pre-loaded. You  can reload it by following the examples at this link: https://learn.adafruit.com/adafruit-funhouse/factory-reset

### Adafruit IO setup
#### Set up feeds
#### Set up the dashboard

## Operation:
### Initialization:
#### Tests for presence of SGP30 and ignores if not present

### Calibrate mode:
#### On start up: hold down sel button to put into calibrate mode
#### Output sensor values will be raw, not adjusted
#### SGP30 will not have initialization values loaded. Initialization values will be read and uploaded to IO hourly

### While running:

#### Exceptions should handle network errors

#### Sensor values are printed to the TFT display and posted to IO feeds:

Sensor| Feed Name | Dotstar LED
---------|----------|---------
CO2 (sgp30) | c02 | 0, low-normal-high / blue-green-red
TVOC (sgp30) | voc | 1, low-normal-high / blue-green-red
PIR | pir | 2, white only
temperature | temperature | 3, low-normal-high / blue-green-red
humidity | humidity | 4, low-normal-high / blue-green-red
barometric pressure | pressure | n/a
light level | lightlevel | n/a
cpu temperature | cputemp | n/a

Also posts some system status info to the IO text feed

If not in calibrate mode, raw sensor readings are adjusted. A linear regression was used offline to calibrate the reading and generate slope and intercept values used in the code. Your sensors will likely require your own calibration efforts.

Use the slider control to vary brightness. Note: this will not work very well in slow update mode

Hold the up button to shift to fast mode
    Forces IO update when pressed
    Sets brightness to 0.25
    Faster updates

Hold down button to shift to low power
    Forces an IO update when pressed
    Sets brightness to zero
    slower updates

Night light mode:
    The PIR motion sensor can trigger the LEDs to act as a night light.
    Only works if the display brightness is zero.
    Can be toggled while running with the select switch.

The Funhouse red led is on when code is executing, off when sleeping

## Version: 0.1

## Author: Ed Rosack - (https://github.com/edro123/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Many thanks to Adafruit for their documentation and sample code

## References
* Funhouse overview: https://learn.adafruit.com/adafruit-funhouse
* Guides for product: Adafruit FunHouse: https://learn.adafruit.com/products/4985/guides
* Funhouse Library: https://circuitpython.readthedocs.io/projects/funhouse/en/latest/
* Creating FunHouse Projects with CircuitPython: https://learn.adafruit.com/creating-funhouse-projects-with-circuitpython/code-examples
* Adafruit SGP30 Library: https://circuitpython.readthedocs.io/projects/sgp30/en/2.3.5/api.html
* Adafruit SGP30 TVOC/eCO2 Gas Sensor Overview: https://learn.adafruit.com/adafruit-sgp30-gas-tvoc-eco2-mox-sensor
* Sensirion SGP30 datasheet: https://sensirion.com/media/documents/984E0DD5/61644B8B/Sensirion_Gas_Sensors_Datasheet_SGP30.pdf











