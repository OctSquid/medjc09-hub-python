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

    CMD_PING = 0x00
    """Ping the MedJC09 Hub."""

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
    id: int = 0


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


class PingResult(CommandResult):
    """Result of the Ping command."""

    command: Command = Command.CMD_PING

    def __init__(self, id: int) -> None:
        self.id = id


class GetVersionResult(CommandResult):
    """Result of the GetVersion command."""

    command: Command = Command.CMD_GET_VERSION
    version: Version
    value: Version

    def __init__(self, id: int, major: int, minor: int, patch: int) -> None:
        self.id = id
        self.version = Version(major, minor, patch)
        self.value = self.version


class GetBaseVoltageResult(CommandResult):
    """Result of the GetBaseVoltage command."""

    command: Command = Command.CMD_GET_BASE_VOLTAGE
    voltage: float
    value: float

    def __init__(self, id: int, voltage: float) -> None:
        self.id = id
        self.voltage = voltage
        self.value = self.voltage


class GetConnectionsResult(CommandResult):
    """Result of the GetConnections command."""

    command: Command = Command.CMD_GET_CONNECTIONS
    connections: List[bool]
    values: List[bool]

    def __init__(self, id: int, connections: List[bool]) -> None:
        self.id = id
        self.connections = connections
        self.value = self.connections


class GetMEResult(CommandResult):
    """Result of the GetME command."""

    command: Command = Command.CMD_GET_ME
    me: List[int]
    values: List[int]

    def __init__(self, id: int, me: List[int]) -> None:
        self.id = id
        self.me = me
        self.value = self.me


class GetSMEResult(CommandResult):
    """Result of the GetSME command."""

    command: Command = Command.CMD_GET_SME
    sme: List[int]
    values: List[int]

    def __init__(self, id: int, sme: List[int]) -> None:
        self.id = id
        self.sme = sme
        self.value = self.sme


class StartPollingResult(CommandResult):
    """Result of the StartPolling command."""

    command: Command = Command.CMD_START_POLLING

    def __init__(self, id: int) -> None:
        self.id = id


class StopPollingResult(CommandResult):
    """Result of the StopPolling command."""

    command: Command = Command.CMD_STOP_POLLING

    def __init__(self, id: int) -> None:
        self.id = id


class SetPollingIntervalResult(CommandResult):
    """Result of the SetPollingInterval command."""

    command: Command = Command.CMD_SET_POLLING_RATE

    def __init__(self, id: int) -> None:
        self.id = id


class GetPollingRateResult(CommandResult):
    """Result of the GetPollingInterval command."""

    command: Command = Command.CMD_GET_POLLING_RATE
    rate: int

    def __init__(self, id: int, interval: int) -> None:
        self.id = id
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
        id: int,
        voltage: float = 0.0,
        me: List[int] = [0, 0, 0, 0],
        sme: List[int] = [0, 0, 0, 0],
        timestamp: int = 0,
    ) -> None:
        self.id = id
        self.voltage = voltage
        self.me = me
        self.sme = sme
        self.timestamp = timestamp


def serialize(command: Command, id: int = 0, params: bytes = bytes([])) -> bytes:
    """Serialize a command and return a packet

    Args:
        command (Command): Command to serialize.
        id (int): ID (16-bit unsigned integer).
        params (bytes): Parameters of the command.

    Returns:
        bytes: Serialized packet.
    """
    if id < 0 or id > 0xFFFF:
        raise ValueError("Command ID must be a 16-bit unsigned integer")

    # Pack command ID as 2 bytes (big-endian)
    id_bytes = id.to_bytes(2, byteorder="big", signed=False)

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

    id = int.from_bytes(packet[1:3], byteorder="big", signed=False)

    if command == Command.CMD_PING:
        return PingResult(id)

    if command == Command.CMD_GET_VERSION:
        major = packet[3]
        minor = packet[4]
        patch = packet[5]
        return GetVersionResult(id, major, minor, patch)

    elif command == Command.CMD_GET_BASE_VOLTAGE:
        vb = int.from_bytes(packet[3:5], byteorder="big", signed=True)
        voltage = 3.3 * vb / 4095
        return GetBaseVoltageResult(id, voltage)

    elif command == Command.CMD_GET_CONNECTIONS:
        connections = [bool(c) for c in [packet[3], packet[4], packet[5], packet[6]]]
        return GetConnectionsResult(id, connections)

    elif command == Command.CMD_GET_ME:
        me = [
            int.from_bytes(packet[3:5], byteorder="big", signed=True),
            int.from_bytes(packet[5:7], byteorder="big", signed=True),
            int.from_bytes(packet[7:9], byteorder="big", signed=True),
            int.from_bytes(packet[9:11], byteorder="big", signed=True),
        ]
        return GetMEResult(id, me)

    elif command == Command.CMD_GET_SME:
        sme = [
            int.from_bytes(packet[3:5], byteorder="big", signed=True),
            int.from_bytes(packet[5:7], byteorder="big", signed=True),
            int.from_bytes(packet[7:9], byteorder="big", signed=True),
            int.from_bytes(packet[9:11], byteorder="big", signed=True),
        ]
        return GetSMEResult(id, sme)

    elif command == Command.CMD_START_POLLING:
        return StartPollingResult(id)

    elif command == Command.CMD_STOP_POLLING:
        return StopPollingResult(id)

    elif command == Command.CMD_SET_POLLING_RATE:
        return SetPollingIntervalResult(id)

    elif command == Command.CMD_GET_POLLING_RATE:
        interval = int.from_bytes(packet[3:5], byteorder="big", signed=False)
        return GetPollingRateResult(id, interval)

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
        return GetPollingReportResult(id, voltage, me, sme, timestamp)

    else:
        raise ValueError(f"Invalid command code: {command}")
