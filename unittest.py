#!/usr/bin/python3

import unittest
from unittest.mock import MagicMock, patch
from SHT4x import SHT4x


class SHT4xTestCase(unittest.TestCase):

    @patch('smbus2.SMBus')
    def setUp(self, mock_smbus):
        self.sensor = SHT4x()

    def tearDown(self):
        self.sensor = None

    def test_reset_success(self):
        self.sensor._write_command = MagicMock()
        self.assertTrue(self.sensor.reset())
        self.sensor._write_command.assert_called_once_with(SHT4x.CMD_SOFT_RESET)

    def test_reset_failure(self):
        self.sensor._write_command = MagicMock(side_effect=Exception())
        self.assertFalse(self.sensor.reset())
        self.sensor._write_command.assert_called_once_with(SHT4x.CMD_SOFT_RESET)

    def test_update_success(self):
        self.sensor._write_command = MagicMock()
        self.sensor._read_data_with_crc = MagicMock(return_value=[0x1234, 0x5678])
        self.assertTrue(self.sensor.update())
        self.sensor._write_command.assert_called_once_with(self.sensor._mode)
        self.sensor._read_data_with_crc.assert_called_once()

    def test_update_failure(self):
        self.sensor._write_command = MagicMock()
        self.sensor._read_data_with_crc = MagicMock(side_effect=Exception())
        self.assertFalse(self.sensor.update())
        self.sensor._write_command.assert_called_once_with(self.sensor._mode)
        self.sensor._read_data_with_crc.assert_called_once()

    def test_mode_setter_valid_mode(self):
        mode = 'high'
        self.sensor.mode = mode
        self.assertEqual(self.sensor._mode, SHT4x.VALID_MODES[mode][0])
        self.assertEqual(self.sensor._delay, SHT4x.VALID_MODES[mode][1])

    def test_mode_setter_invalid_mode(self):
        with self.assertRaises(ValueError):
            self.sensor.mode = 'invalid_mode'

    def test_mode_getter(self):
        self.sensor._mode = SHT4x.VALID_MODES['high'][0]
        self.assertEqual(self.sensor.mode, 'high')

    def test_serial_number(self):
        self.sensor._serial_number = '0x12345678'
        self.assertEqual(self.sensor.serial_number, '0x12345678')

    def test_temperature(self):
        self.sensor._temperature = 0x1234
        self.assertAlmostEqual(self.sensor.temperature, -32.6, places=1)

    def test_humidity(self):
        self.sensor._humidity = 0x5678
        self.assertAlmostEqual(self.sensor.humidity, 36.2, places=1)


if __name__ == '__main__':
    unittest.main()
