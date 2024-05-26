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


def serialize(command: Command) -> bytes:
    """Serialize a command and return a packet

    Args:
        command (Command): Command to serialize.

    Returns:
        bytes: Serialized packet.
    """
    packet: bytes = bytes([Protocol.STX.value, command.value, Protocol.ETX.value])

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
        connections = [packet[2], packet[3], packet[4], packet[5]]
        return GetConnectionsResult([bool(c) for c in connections])

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

    else:
        raise ValueError(f"Invalid command code: {command}")
