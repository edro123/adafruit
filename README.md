# adafruit Funhouse Air Quality Monitor

Sample built in and add on sensors, print values, upload to Adafruit IO, use dotstars for status

On start up: hold down sel button to calibrate
    cal mode operates normally, except will add cal readings hourly IO text feed 
    exception handles absense of SGP30 add on board
While running:
    expceptions handle network errors and solid red led indicates error
    sensor values posted to IO feeds:
        eCO2 (sgp30)
        humidity (internal)
        PIR (add on)
        temperature (internal)
        TVOC (sgp30)
        barometric pressure (internal)
        light level (internal)
        cpu temperature (internal)
    Also post system info text feed to IO
    Dotstar colors indicate reading levels for some sensors: controlled by constants
        eCO2
        humidity
        PIR
        temperature
        TVOC
    Raw sensor readings are adjusted with offset and slope calibration values
    Slider controls brightness (not very well in low power mode)
    Hold up button to shift to normal mode
        Forces IO update when pressed
        0.2s sleep
        Brightness control with slider, defaults to 0.25
        60s IO update
    Hold down button to shift to low power
        Forces an IO update when pressed
        2.0s sleep
        Brightness control with slider, defaults to 0.0
        Update every 5 minutes?
        Hold a button to go to normal?