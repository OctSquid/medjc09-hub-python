from dataclasses import dataclass
from enum import Enum
from typing import List


class Protocol(Enum):
    """Protocol codes for the MedJC09 Hub."""

    SETX = 0xFE
    """Start of the error response."""

    EETX = 0xFF
    """End of the error response."""


class Command(Enum):
    """Command codes for the MedJC09 Hub."""

    CMD_GET_VERSION = 0x01
    """Get the version of the MedJC09 Hub."""

    CMD_GET_BASE_VOLTAGE = 0x02
    """Get the base voltage of the MedJC09 Hub."""

    CMD_GET_CONNECTIONS = 0x20
    """Get the connections of the MedJC09 Hub."""

    CMD_GET_ME = 0x30
    """Get the ME values of the MedJC09 Hub."""

    CMD_GET_SME = 0x31
    """Get the SME values of the MedJC09 Hub."""

    CMD_START_POLLING = 0x40
    """Start polling the MedJC09 Hub."""

    CMD_STOP_POLLING = 0x41
    """Stop polling the MedJC09 Hub."""

    CMD_SET_POLLING_RATE = 0x42
    """Set the polling interval of the MedJC09 Hub."""

    CMD_GET_POLLING_RATE = 0x43
    """Get the polling interval of the MedJC09 Hub."""

    CMD_GET_POLLING_REPORT = 0x4F
    """Get the polling report of the MedJC09 Hub."""


@dataclass
class CommandResult:
    """Result of a command."""

    command: Command


@dataclass
class Version:
    """Version of the MedJC09 Hub."""

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch


class GetVersionResult(CommandResult):
    """Result of the GetVersion command."""

    command: Command = Command.CMD_GET_VERSION
    version: Version
    value: Version

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.version = Version(major, minor, patch)
        self.value = self.version


class GetBaseVoltageResult(CommandResult):
    """Result of the GetBaseVoltage command."""

    command: Command = Command.CMD_GET_BASE_VOLTAGE
    voltage: float
    value: float

    def __init__(self, voltage: float) -> None:
        self.voltage = voltage
        self.value = self.voltage


class GetConnectionsResult(CommandResult):
    """Result of the GetConnections command."""

    command: Command = Command.CMD_GET_CONNECTIONS
    connections: List[bool]
    values: List[bool]

    def __init__(self, connections: List[bool]) -> None:
        self.connections = connections
        self.value = self.connections


class GetMEResult(CommandResult):
    """Result of the GetME command."""

    command: Command = Command.CMD_GET_ME
    me: List[int]
    values: List[int]

    def __init__(self, me: List[int]) -> None:
        self.me = me
        self.value = self.me


class GetSMEResult(CommandResult):
    """Result of the GetSME command."""

    command: Command = Command.CMD_GET_SME
    sme: List[int]
    values: List[int]

    def __init__(self, sme: List[int]) -> None:
        self.sme = sme
        self.value = self.sme


class StartPollingResult(CommandResult):
    """Result of the StartPolling command."""

    command: Command = Command.CMD_START_POLLING

    def __init__(self) -> None:
        pass


class StopPollingResult(CommandResult):
    """Result of the StopPolling command."""

    command: Command = Command.CMD_STOP_POLLING

    def __init__(self) -> None:
        pass


class SetPollingIntervalResult(CommandResult):
    """Result of the SetPollingInterval command."""

    command: Command = Command.CMD_SET_POLLING_RATE

    def __init__(self) -> None:
        pass


class GetPollingRateResult(CommandResult):
    """Result of the GetPollingInterval command."""

    command: Command = Command.CMD_GET_POLLING_RATE
    rate: int

    def __init__(self, interval: int) -> None:
        self.rate = interval


class GetPollingReportResult(CommandResult):
    """Result of the GetPollingReport command."""

    command: Command = Command.CMD_START_POLLING
    voltage: float
    me: List[int]
    sme: List[int]
    timestamp: int

    def __init__(
        self,
        voltage: float = 0.0,
        me: List[int] = [0, 0, 0, 0],
        sme: List[int] = [0, 0, 0, 0],
        timestamp: int = 0,
    ) -> None:
        self.voltage = voltage
        self.me = me
        self.sme = sme
        self.timestamp = timestamp


def serialize(command: Command, command_id: int = 0, params: bytes = bytes([])) -> bytes:
    """Serialize a command and return a packet

    Args:
        command (Command): Command to serialize.
        command_id (int): Command ID (16-bit unsigned integer).
        params (bytes): Parameters of the command.

    Returns:
        bytes: Serialized packet.
    """
    if command_id < 0 or command_id > 0xFFFF:
        raise ValueError("Command ID must be a 16-bit unsigned integer")

    # Pack command ID as 2 bytes (big-endian)
    id_bytes = command_id.to_bytes(2, byteorder="big")

    packet: bytes = bytes([command.value]) + id_bytes + params

    return packet


def deserialize(packet: bytes) -> CommandResult:
    """Deserialize a packet and return a command result.

    Args:
        packet (bytes): Packet to deserialize.

    Returns:
        CommandResult: Result of the command.

    Raises:
        ValueError: If the command code is invalid.
    """
    command: Command = Command(packet[0])

    if command == Command.CMD_GET_VERSION:
        major = packet[3]
        minor = packet[4]
        patch = packet[5]
        return GetVersionResult(major, minor, patch)

    elif command == Command.CMD_GET_BASE_VOLTAGE:
        vb = int.from_bytes(packet[3:5], byteorder="big", signed=True)
        voltage = 3.3 * vb / 4095
        return GetBaseVoltageResult(voltage)

    elif command == Command.CMD_GET_CONNECTIONS:
        connections = [bool(c) for c in [packet[3], packet[4], packet[5], packet[6]]]
        return GetConnectionsResult(connections)

    elif command == Command.CMD_GET_ME:
        me = [
            int.from_bytes(packet[3:5], byteorder="big", signed=True),
            int.from_bytes(packet[5:7], byteorder="big", signed=True),
            int.from_bytes(packet[7:9], byteorder="big", signed=True),
            int.from_bytes(packet[9:11], byteorder="big", signed=True),
        ]
        return GetMEResult(me)

    elif command == Command.CMD_GET_SME:
        sme = [
            int.from_bytes(packet[3:5], byteorder="big", signed=True),
            int.from_bytes(packet[5:7], byteorder="big", signed=True),
            int.from_bytes(packet[7:9], byteorder="big", signed=True),
            int.from_bytes(packet[9:11], byteorder="big", signed=True),
        ]
        return GetSMEResult(sme)

    elif command == Command.CMD_START_POLLING:
        return StartPollingResult()

    elif command == Command.CMD_STOP_POLLING:
        return StopPollingResult()

    elif command == Command.CMD_SET_POLLING_RATE:
        return SetPollingIntervalResult()

    elif command == Command.CMD_GET_POLLING_RATE:
        interval = int.from_bytes(packet[3:5], byteorder="big", signed=False)
        return GetPollingRateResult(interval)

    elif command == Command.CMD_GET_POLLING_REPORT:
        voltage = (3.3 / 4095) * int.from_bytes(packet[3:5], byteorder="big", signed=True)
        me = [
            int.from_bytes(packet[5:7], byteorder="big", signed=True),
            int.from_bytes(packet[7:9], byteorder="big", signed=True),
            int.from_bytes(packet[9:11], byteorder="big", signed=True),
            int.from_bytes(packet[11:13], byteorder="big", signed=True),
        ]
        sme = [
            int.from_bytes(packet[13:15], byteorder="big", signed=True),
            int.from_bytes(packet[15:17], byteorder="big", signed=True),
            int.from_bytes(packet[17:19], byteorder="big", signed=True),
            int.from_bytes(packet[19:21], byteorder="big", signed=True),
        ]
        timestamp = int.from_bytes(packet[21:25], byteorder="big", signed=False)
        return GetPollingReportResult(voltage, me, sme, timestamp)

    else:
        raise ValueError(f"Invalid command code: {command}")
