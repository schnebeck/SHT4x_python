# SHT4x-python
SHT4x.py is a Python class for interfacing with the Sensirion SHT4x temperature and humidity sensor family via the I²C bus. This library provides methods to control the sensor, retrieve temperature and humidity readings, reset the sensor, and obtain the serial number.

## Installation

Make sure you have Python 3.x installed. You can install the depending smbus2-library using pip:

pip install smbus2

## Usage

### Import the `SHT4x` class from the library:

```python

from SHT4x import SHT4x
```
### Create an instance of the SHT4x class:

```python

sensor = SHT4x()
```
### Reading Temperature and Humidity

To retrieve temperature and humidity readings from the sensor, call the update() method:

```python

if sensor.update():
    temperature = sensor.temperature
    humidity = sensor.humidity
    print(f"Temperature: {temperature}°C")
    print(f"Humidity: {humidity}% RH")
else:
    print("Failed to read data from the sensor.")
```
### Setting the Measurement Mode

You can set the measurement mode using the mode property. Valid modes are "high", "medium", and "low". For example:

```python

sensor.mode = "high"
```
### Resetting the Sensor

To reset the sensor to its default state, use the reset() method:

```python

if sensor.reset():
    print("Sensor reset successful.")
else:
    print("Failed to reset the sensor.")
```
### Retrieving the Serial Number

You can obtain the serial number of the sensor using the serial_number property:

```python

serial_number = sensor.serial_number
print(f"Serial Number: {serial_number}")
```
Please refer to the inline code comments and the class definition for detailed information about each method and property.

## License

This library is released under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions to the SHT4x class are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## Author

    Thorsten Schnebeck

## Acknowledgments

Special thanks to the authors and contributors of the smbus2 library for providing the I2C communication functionality.
This documentation was generated by ChatGPT 3.5
