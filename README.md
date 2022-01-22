# Adafruit Funhouse Air Quality Monitor

This project builds an Air Quality Monitor using the Adafruit Funhouse microcontroller, an add on PIR sensor, and an SGP30 carbon dioxide / VOC sensor. The code will read each of the built in and add on sensors, adjust them with predetermined calibration constants, print the values to the Funstar display, upload them Adafruit IO, and use the dotstars for status

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc





# adafruit Funhouse Air Quality Monitor

### Project Description

Sample built in and add on sensors, print values, upload to Adafruit IO, use dotstars for status

### Prerequisites

### Installing

### Processing

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
    
    Raw sensor readings are adjusted with slope and intercept values determined with an offline linear regression
    
    Slider controls brightness (not very well in low power mode)
    
    Hold up button to shift to fast mode
        Forces IO update when pressed
        Faster updates
    
    Hold down button to shift to low power
        Forces an IO update when pressed
        slower updates

### Acknowledgements
