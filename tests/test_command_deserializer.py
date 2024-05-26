import pytest
from medjc09_hub_python.command import (
    Command,
    GetBaseVoltageResult,
    GetConnectionsResult,
    GetMEResult,
    GetSMEResult,
    GetVersionResult,
    Protocol,
    deserialize,
)


def test_deserialize_get_version() -> None:
    """Test for deserialize function with CMD_GET_VERSION."""
    packet = bytes([Protocol.STX.value, Command.CMD_GET_VERSION.value, 0x01, 0x00, 0x00, Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, GetVersionResult)
    assert result.version.major == 1
    assert result.version.minor == 0
    assert result.version.patch == 0


def test_deserialize_get_base_voltage() -> None:
    """Test for deserialize function with CMD_GET_BASE_VOLTAGE."""
    vb_value = int(32767 / 5)  # Corresponds to 1V
    packet = (
        bytes([Protocol.STX.value, Command.CMD_GET_BASE_VOLTAGE.value])
        + vb_value.to_bytes(2, byteorder="big", signed=True)
        + bytes([Protocol.ETX.value])
    )
    result = deserialize(packet)
    assert isinstance(result, GetBaseVoltageResult)
    assert result.voltage == pytest.approx(1.0, rel=1e-2)


def test_deserialize_get_connections() -> None:
    """Test for deserialize function with CMD_GET_CONNECTIONS."""
    packet = bytes([Protocol.STX.value, Command.CMD_GET_CONNECTIONS.value, 0x01, 0x00, 0x00, 0x00, Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, GetConnectionsResult)
    assert result.connections == [True, False, False, False]


def test_deserialize_get_me() -> None:
    """Test for deserialize function with CMD_GET_ME."""
    me_values = [1000, 1001, 0, 0]
    me_bytes = b"".join([v.to_bytes(2, byteorder="big", signed=True) for v in me_values])
    packet = bytes([Protocol.STX.value, Command.CMD_GET_ME.value]) + me_bytes + bytes([Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, GetMEResult)
    assert result.me == me_values


def test_deserialize_get_sme() -> None:
    """Test for deserialize function with CMD_GET_SME."""
    sme_values = [2000, 2001, 0, 0]
    sme_bytes = b"".join([v.to_bytes(2, byteorder="big", signed=True) for v in sme_values])
    packet = bytes([Protocol.STX.value, Command.CMD_GET_SME.value]) + sme_bytes + bytes([Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, GetSMEResult)
    assert result.sme == sme_values
