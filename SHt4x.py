# SHT4x.py
# intended for reading Sensirion SHT4x device family through the i2c bus
# use: from SHT4x import SHT4x

__author__ = "Thorsten Schnebeck"
__date__ = "2023-05-29"


from smbus2 import SMBus, i2c_msg
import time


class SHT4x:
    """
    Class to interface with the Sensirion SHT4x temperature and humidity sensor family.

    This class provides methods to control the sensor, such as setting the measurement mode, retrieving temperature
    and humidity readings, resetting the sensor, and retrieving the serial number.
    """
    
    ADDRESS = 0x44         # I2C addresses (by order) of the SHT40 sensor: 0x44 or 0x45
    VALID_MODES = {
        "high":            [0xFD, 0.01],
        "medium":          [0xF6, 0.01],
        "low":             [0xE0, 0.01],
        "heat 1s 200mW":   [0x39, 1.01],
        "heat 0.1s 200mW": [0x32, 0.11],
        "heat 1s 110mW":   [0x2F, 1.01],
        "heat 0.1s 110mW": [0x24, 0.11],
        "heat 1s 20mW":    [0x1E, 1.01],
        "heat 0.1s 20mW":  [0x15, 0.11],
    }
    CMD_SOFT_RESET = 0x94
    CMD_READ_SERIAL_NUMBER = 0x89

    def __init__(self, bus=1, address=ADDRESS, mode="high"):
        self._i2c_bus = bus
        self._i2c_address = address
        self._bus = SMBus(self._i2c_bus)
        self._valid = False
        self._serial_number = "None"
        self._mode = 0
        self._delay = 0.0
        self._temperature = None
        self._humidity = None

        self.reset()
        data = self._get_serial_number()
        if len(data) != 0:
            self._serial_number = f"{hex(data[0])[2:].zfill(4) + hex(data[1])[2:].zfill(4)}"
        self.mode = mode

    def __repr__(self) -> str:
        if self._serial_number == "":
            return f"no sensor found"
        elif self._valid:
            return f"serial number: {self._serial_number} | temperature: {self.temperature}°C humidity: {self.humidity}% RH"
        else:
            return f"serial number: {self._serial_number} | no valid data!"

    def _write_command(self, command):
        self._bus.write_byte(self._i2c_address, command)

    def _read_data_with_crc(self):
        read = i2c_msg.read(self._i2c_address, 6)
        self._bus.i2c_rdwr(read)
        data = list(read)
        crc1 = SHT4x._calculate_crc8(data[0:2])
        crc2 = SHT4x._calculate_crc8(data[3:5])
        if crc1 == data[2] and crc2 == data[5]:
            return [data[0] << 8 | data[1], data[3] << 8 | data[4]]
        else:
            raise ValueError("CRC8 check failed")

    def _get_serial_number(self) -> list:
        try:
            self._write_command(self.CMD_READ_SERIAL_NUMBER)
            time.sleep(0.01)
            return self._read_data_with_crc()
        except:
            return []

    def reset(self) -> bool:
        """
        Resets the SHT4x sensor.
        This method sends the soft reset command to the SHT40 sensor, which initializes the sensor to its default state.
        :return: True when send comand was ok, False when send comand failed
        """

        try:
            self._write_command(SHT4x.CMD_SOFT_RESET)
            time.sleep(0.01)
            return True
        except:
            return False

    def update(self) -> bool:
        """
        Updates the temperature and humiditiy readings from the sensor
        This methods tries to read the current temperature and humidity data from the SHT4x sensor and stores the data in attributes

        :returns: True when updating was ok and False when updating failed
        """

        try:
            self._write_command(self._mode)
            time.sleep(self._delay)
            self._temperature, self._humidity = self._read_data_with_crc()
            self._valid = True
            return True
        except:
            self._valid = False
            return False

    @property
    def mode(self):
        for this_mode in SHT4x.VALID_MODES:
            if SHT4x.VALID_MODES[this_mode][0] == self._mode:
                return f"{this_mode}"
        return ""

    @mode.setter
    def mode(self, mode):
        """
        Sets the measurement mode of the SHT4x sensor.
        This method sets the measurement mode of the sensor to the specified accuracy level or to use the heater.

        :param mode: The desired measurement mode ("high", "medium", "low" or a heater option; see VALID_MODES).
        :return: None
        :raises ValueError: If an invalid mode is provided.
        """

        self._mode = None
        for this_mode in SHT4x.VALID_MODES:
            if this_mode == mode:
                self._mode = SHT4x.VALID_MODES[mode][0]
                self._delay = SHT4x.VALID_MODES[mode][1]
                break
        if self._mode == None:
            raise ValueError("Invalid mode setting")

    @property
    def serial_number(self):
        return f"{self._serial_number}"

    @property
    def temperature(self):
        """
        Get the temperature reading from the SHT4x sensor.
        This method returns the temperature in degrees Celsius of the last measurement update.

        :return: The temperature in degrees Celsius or None if there was no update.
        """

        temperature = None
        if self._temperature != None:
            temperature = round(-45.0 + 175.0 * self._temperature / 65535.0, 1)
        return temperature

    @property
    def humidity(self):
        """
        Get the humidity reading from the SHT4x sensor.
        This method returns the relative humidity as a percentage of the last measurement update.

        :return: The relative humidity as a percentage or None if there was no upate
        """

        humidity = None
        if self._humidity != None:
            humidity = -6.0 + 125.0 * self._humidity / 65535.0
            humidity = round(humidity, 1)
            humidity = max(min(humidity, 100.0), 0.0)
        return humidity

    @staticmethod
    def _calculate_crc8(data):
        CRC8_POLYNOMIAL = 0x31
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ CRC8_POLYNOMIAL
                else:
                    crc <<= 1
        return crc & 0xFF
