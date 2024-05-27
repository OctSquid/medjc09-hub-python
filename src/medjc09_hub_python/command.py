from dataclasses import dataclass
from enum import Enum
from typing import List


class Protocol(Enum):
    """Protocol codes for the MedJC09 Hub."""

    STX = 0x02
    """Start of the command."""

    ETX = 0x03
    """End of the command."""

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

    CMD_SET_POLLING_INTERVAL = 0x42
    """Set the polling interval of the MedJC09 Hub."""

    CMD_GET_POLLING_INTERVAL = 0x43
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

    command: Command = Command.CMD_SET_POLLING_INTERVAL

    def __init__(self) -> None:
        pass


class GetPollingIntervalResult(CommandResult):
    """Result of the GetPollingInterval command."""

    command: Command = Command.CMD_GET_POLLING_INTERVAL
    interval: int

    def __init__(self, interval: int) -> None:
        self.interval = interval


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


def serialize(command: Command, params: bytes = bytes([])) -> bytes:
    """Serialize a command and return a packet

    Args:
        command (Command): Command to serialize.
        params (bytes): Parameters of the command.

    Returns:
        bytes: Serialized packet.
    """
    packet: bytes = bytes([Protocol.STX.value, command.value] + list(params) + [Protocol.ETX.value])

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
    command: Command = Command(packet[1])

    if command == Command.CMD_GET_VERSION:
        major = packet[2]
        minor = packet[3]
        patch = packet[4]
        return GetVersionResult(major, minor, patch)

    elif command == Command.CMD_GET_BASE_VOLTAGE:
        vb = int.from_bytes(packet[2:4], byteorder="big", signed=True)
        voltage = (5 / 32767) * vb
        return GetBaseVoltageResult(voltage)

    elif command == Command.CMD_GET_CONNECTIONS:
        connections = [bool(c) for c in [packet[2], packet[3], packet[4], packet[5]]]
        return GetConnectionsResult(connections)

    elif command == Command.CMD_GET_ME:
        me = [
            int.from_bytes(packet[2:4], byteorder="big", signed=True),
            int.from_bytes(packet[4:6], byteorder="big", signed=True),
            int.from_bytes(packet[6:8], byteorder="big", signed=True),
            int.from_bytes(packet[8:10], byteorder="big", signed=True),
        ]
        return GetMEResult(me)

    elif command == Command.CMD_GET_SME:
        sme = [
            int.from_bytes(packet[2:4], byteorder="big", signed=True),
            int.from_bytes(packet[4:6], byteorder="big", signed=True),
            int.from_bytes(packet[6:8], byteorder="big", signed=True),
            int.from_bytes(packet[8:10], byteorder="big", signed=True),
        ]
        return GetSMEResult(sme)

    elif command == Command.CMD_START_POLLING:
        return StartPollingResult()

    elif command == Command.CMD_STOP_POLLING:
        return StopPollingResult()

    elif command == Command.CMD_SET_POLLING_INTERVAL:
        return SetPollingIntervalResult()

    elif command == Command.CMD_GET_POLLING_INTERVAL:
        interval = int.from_bytes(packet[2:4], byteorder="big", signed=False)
        return GetPollingIntervalResult(interval)

    elif command == Command.CMD_GET_POLLING_REPORT:
        voltage = (5 / 32767) * int.from_bytes(packet[2:4], byteorder="big", signed=True)
        me = [
            int.from_bytes(packet[4:6], byteorder="big", signed=True),
            int.from_bytes(packet[6:8], byteorder="big", signed=True),
            int.from_bytes(packet[8:10], byteorder="big", signed=True),
            int.from_bytes(packet[10:12], byteorder="big", signed=True),
        ]
        sme = [
            int.from_bytes(packet[12:14], byteorder="big", signed=True),
            int.from_bytes(packet[14:16], byteorder="big", signed=True),
            int.from_bytes(packet[16:18], byteorder="big", signed=True),
            int.from_bytes(packet[18:20], byteorder="big", signed=True),
        ]
        timestamp = int.from_bytes(packet[20:24], byteorder="big", signed=False)
        return GetPollingReportResult(voltage, me, sme, timestamp)

    else:
        raise ValueError(f"Invalid command code: {command}")
