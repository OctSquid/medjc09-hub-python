from typing import Callable, List, TypedDict, Union

import serial
from cobs import cobs

from .command import (
    Command,
    CommandResult,
    GetBaseVoltageResult,
    GetConnectionsResult,
    GetMEResult,
    GetPollingIntervalResult,
    GetPollingReportResult,
    GetSMEResult,
    GetVersionResult,
    deserialize,
    serialize,
)

VersionType = TypedDict("VersionType", {"major": int, "minor": int, "patch": int})
"""Type for version information."""

PollingReportType = TypedDict(
    "PollingReportType",
    {
        "voltage": float,
        "me": List[int],
        "sme": List[int],
        "me_voltage": List[float],
        "sme_voltage": List[float],
        "timestamp": int,
    },
)
"""Type for polling report."""

PollingHandlerType = Callable[[PollingReportType], None]
"""Type for callback functions."""


class Medjc09:
    """A class for handling communication with the Medjc09 device."""

    def __init__(self, port: str, baudrate: int = 115200, polling_handler: Union[PollingHandlerType, None] = None):
        """Initialize the Medjc09 class.

        Args:
            port (str): Serial port name. E.g. "/dev/ttyUSB0"
            baudrate (int, optional): Baudrate. Defaults to 115200.
            polling_handler (PollingHandlerType, optional): Callback function for polling. Defaults to None.
        """
        self._is_polling_mode = False
        self._ser = serial.Serial(port, baudrate, timeout=1)
        self._polling_handler = polling_handler

    def send_command(self, command: Command, params: bytes = bytes([])) -> CommandResult:
        """Send a command to the Medjc09 device and return the result.

        Args:
            command (Command): Command to send.
            params (bytes, optional): Command parameters. Defaults to bytes([]).

        Returns:
            CommandResult: Result of the command.
        """
        packet = serialize(command, params)
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

    def is_polling(self) -> bool:
        """Check if the polling mode is active."""
        return self._is_polling_mode

    def start_polling(self) -> None:
        """Begin watching the polling mode.
        #! Note: that you need to call the `update()` method to receive the polling report.
        """
        self._is_polling_mode = True
        _ = self.send_command(Command.CMD_START_POLLING)

    def stop_polling(self) -> None:
        """Stop watching the polling mode."""
        self._is_polling_mode = False
        _ = self.send_command(Command.CMD_STOP_POLLING)

    def set_polling_interval(self, interval: int) -> None:
        """Set the polling interval.

        Args:
            interval (int): Polling interval in milliseconds.
        """
        params = interval.to_bytes(2, byteorder="big", signed=True)
        _ = self.send_command(Command.CMD_SET_POLLING_INTERVAL, params)

    def get_polling_interval(self) -> int:
        """Get the polling interval.

        Returns:
            int: Polling interval in milliseconds.
        """
        result = self.send_command(Command.CMD_GET_POLLING_INTERVAL)
        if isinstance(result, GetPollingIntervalResult):
            return result.interval
        else:
            raise ValueError("Unexpected result type")

    def get_polling_report(self) -> PollingReportType:
        """Get the polling report.

        Returns:
            dict: Polling report.
        """
        result = self.send_command(Command.CMD_GET_POLLING_REPORT)
        if isinstance(result, GetPollingReportResult):
            return {
                "voltage": result.voltage,
                "me": result.me,
                "sme": result.sme,
                "me_voltage": [result.voltage * (me_value / 32767) for me_value in result.me],
                "sme_voltage": [result.voltage * (sme_value / 32767) for sme_value in result.sme],
                "timestamp": result.timestamp,
            }
        else:
            raise ValueError("Unexpected result type")

    def update(self) -> None:
        """Update the polling mode."""
        if self._is_polling_mode:
            response = self._ser.read_until(bytes([0x00]))
            if response == b"":  # No data
                return
            decoded_response = cobs.decode(response[:-1])
            result = deserialize(decoded_response)
            if isinstance(result, GetPollingReportResult):
                if self._polling_handler is not None:
                    self._polling_handler(
                        {
                            "voltage": result.voltage,
                            "me": result.me,
                            "sme": result.sme,
                            "me_voltage": [result.voltage * (me_value / 32767) for me_value in result.me],
                            "sme_voltage": [result.voltage * (sme_value / 32767) for sme_value in result.sme],
                            "timestamp": result.timestamp,
                        }
                    )
