from typing import List

import serial
from cobs import cobs

from .command import (
    Command,
    CommandResult,
    GetBaseVoltageResult,
    GetConnectionsResult,
    GetMEResult,
    GetSMEResult,
    GetVersionResult,
    deserialize,
    serialize,
)


class Medjc09:
    """A class for handling communication with the Medjc09 device."""

    def __init__(self, port: str, baudrate: int = 115200):
        """Initialize the Medjc09 class.

        Args:
            port (str): Serial port name. E.g. "/dev/ttyUSB0"
            baudrate (int, optional): Baudrate. Defaults to 115200.
        """
        self._ser = serial.Serial(port, baudrate, timeout=1)

    def send_command(self, command: Command) -> CommandResult:
        """Send a command to the Medjc09 device and return the result.

        Args:
            command (Command): Command to send.

        Returns:
            CommandResult: Result of the command.
        """
        packet = serialize(command)
        encoded_packet = cobs.encode(packet)
        self._ser.write(encoded_packet + bytes([0x00]))

        response = self._ser.read_until(bytes([0x00]))
        decoded_response = cobs.decode(response[:-1])  # Remove the trailing 0x00
        result = deserialize(decoded_response)

        return result

    def get_version(self) -> str:
        """Get the firmware version of the Medjc09 device.

        Returns:
            str: Firmware version. E.g. "v1.0.0"
        """
        result = self.send_command(Command.CMD_GET_VERSION)
        if isinstance(result, GetVersionResult):
            return f"v{result.version.major}.{result.version.minor}.{result.version.patch}"
        else:
            raise ValueError("Unexpected result type")

    def get_base_voltage(self) -> float:
        """Get the base voltage of the Medjc09 device.

        Returns: float: Base voltage. E.g. 5.0
        """
        result = self.send_command(Command.CMD_GET_BASE_VOLTAGE)
        if isinstance(result, GetBaseVoltageResult):
            return result.voltage
        else:
            raise ValueError("Unexpected result type")

    def get_connections(self) -> List[bool]:
        """Get the connection status of sensors.

        Returns:
            List[bool]: Connection status of sensors. E.g. [True, False, False, False]
        """
        result = self.send_command(Command.CMD_GET_CONNECTIONS)
        if isinstance(result, GetConnectionsResult):
            return result.connections
        else:
            raise ValueError("Unexpected result type")

    def get_me(self) -> List[int]:
        """Get the ME values of sensors.

        Returns:
            List[int]: ME values of sensors. E.g. [1000, 1001, 0, 0]
        """
        result = self.send_command(Command.CMD_GET_ME)
        if isinstance(result, GetMEResult):
            return result.me
        else:
            raise ValueError("Unexpected result type")

    def get_me_as_voltage(self) -> List[float]:
        """Get the ME values of sensors as voltage.

        Returns:
            List[float]: ME values of sensors as voltage. E.g. [1.52587890625, 1.52587890625, 0.0, 0.0]
        """
        bv_value = self.get_base_voltage()
        me_values = self.get_me()
        return [bv_value * (me_value / 32767) for me_value in me_values]

    def get_sme(self) -> List[int]:
        """Get the SME values of sensors.

        Returns:
            List[int]: SME values of sensors. E.g. [1000, 1001, 0, 0]
        """
        result = self.send_command(Command.CMD_GET_SME)
        if isinstance(result, GetSMEResult):
            return result.sme
        else:
            raise ValueError("Unexpected result type")

    def get_sme_as_voltage(self) -> List[float]:
        """Get the SME values of sensors as voltage.

        Returns:
            List[float]: SME values of sensors as voltage. E.g. [1.52587890625, 1.52587890625, 0.0, 0.0]
        """
        bv_value = self.get_base_voltage()
        sme_values = self.get_sme()
        return [bv_value * (sme_value / 32767) for sme_value in sme_values]

    def close(self) -> None:
        """Close the serial connection."""
        self._ser.close()

    def is_open(self) -> bool:
        """Check if the serial connection is open."""
        value = self._ser.is_open
        return bool(value)
