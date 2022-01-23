# Adafruit Funhouse Air Quality Monitor

This Air Quality Monitor is built using the Adafruit Funhouse microcontroller, an add on PIR sensor, and an SGP30 carbon dioxide / VOC sensor. The code will read each of the sensors, adjust them with predetermined calibration constants, print the values to the Funhouse display, upload them to Adafruit IO, and uses the dotstars for status

## Prerequisites

### Hardware
- Adafruit FunHouse - WiFi Home Automation Development Board (https://www.adafruit.com/product/4985)
- (option) Breadboard-friendly Mini PIR Motion Sensor with 3 Pin Header (https://www.adafruit.com/product/4871)
- (option) SGP30 Air Quality Sensor Breakout - VOC and eCO2 - STEMMA QT / Qwiic (https://www.adafruit.com/product/3709)
- (option) Adafruit FunHouse Mounting Plate and Yellow Brick Stand (https://www.adafruit.com/product/4962)

### Software

#### Setting up CircuitPython:
Follow the steps on Adafruit's page to install CircuitPython: https://learn.adafruit.com/adafruit-funhouse/circuitpython

#### Installing required CircuitPython libraries:
CircuitPython Libraries required for this project and their source / locations are:
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
the source code (aqm_code.py) is available on github at: https://github.com/edro123/adafruit

#### Secrets file
You will need to edit a secrets.py file to input your information for wifi, Adafruit IO, and timezone.

#### Project bundle
You can install the source code and libraries as a bundle. Download funhouse_aqm_bundle.zip from xxx. unzip it and copy it to the device.

#### Factory reset:
The Adafruit Funhouse comes with an Arduino Self Test example pre-loaded. You can reload it by following the instructions at this link: https://learn.adafruit.com/adafruit-funhouse/factory-reset

### Adafruit IO
To use Adafruit IO, you'll need to sign up for an account at https://io.adafruit.com. There are free and paid versions. This project can use the free tier.

#### Feeds
Once youf're signed up, create a set of feeds to match the feed names for each sensor  listed in the table below.

#### Dashboard
Once your feeds are set up, add them to a Dashboard. You can set up warning values to match the red-green-blue alerts in the code.

## Operation:
### Initialization:
#### Tests for presence of SGP30 and ignores if not present

### Calibrate mode:
#### On start up: hold down sel button to put into calibrate mode
#### Output sensor values will be raw, not adjusted
#### SGP30 will not have initialization values loaded. Initialization values will be read and uploaded to IO hourly

### While running:

#### Exceptions should handle network errors

#### Sensor values are printed to the TFT display and posted to IO feeds. The dotstar LEDs are also used for status for a subset of the sensors. System messages are also sent to the text feed

Sensor| Feed Name | LED | Blue | Green | Red
---------|----------|---------|---------|---------|---------
CO2 (sgp30) | c02 | 0 | <800 | between | >2500
TVOC (sgp30) | voc | 1 | <200 | between | >2500
PIR | pir | 2 | white only
temperature | temperature | 3 | <62 | between | >80
humidity | humidity | 4 |  <42 | between | >53
barometric pressure | pressure | n/a | n/a  | n/a | n/a 
light level | lightlevel | n/a | n/a | n/a  | n/a | n/a 
cpu temperature | cputemp | n/a | n/a | n/a  | n/a | n/a 
System messages | text | n/a | n/a  | n/a | n/a 

If in calibrate mode, raw sensor readings are recorded. If not, they're adjusted with a linear regression that was developed offline to calibrate the readings to know references. The linear regression slope and intercept values that used in the source code  will likely require revision for your own sensors. An example regression:

<img src="./co2-regression.jpg" alt="co2 regression" style="height: 534px; width:1024px;"/>

#### Controls
Use the slider control to vary brightness. Note: this will not work very well in normal  update mode

Hold the up button to shift to fast mode:
- Forces IO update when pressed
- Sets brightness to 0.25
- Faster updates

Hold down button to shift to normal mode:
- Forces an IO update when pressed
- Sets brightness to zero
- slower updates

Night light mode:
- The PIR motion sensor can trigger the LEDs to act as a night light.
- Only works if the display brightness is zero.
- Can be toggled while running with the select switch.

The Funhouse red led is on when code is executing, off when sleeping

## Version:
0.1 - released 1/31/22

## Author: 
Ed Rosack - (https://github.com/edro123/)

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











