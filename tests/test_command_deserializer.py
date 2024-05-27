from typing import List

import pytest
from medjc09_hub_python.command import (
    Command,
    GetBaseVoltageResult,
    GetConnectionsResult,
    GetMEResult,
    GetPollingIntervalResult,
    GetPollingReportResult,
    GetSMEResult,
    GetVersionResult,
    Protocol,
    SetPollingIntervalResult,
    StartPollingResult,
    StopPollingResult,
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


def test_deserialize_start_polling() -> None:
    """Test for deserialize function with CMD_START_POLLING."""
    packet = bytes([Protocol.STX.value, Command.CMD_START_POLLING.value, Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, StartPollingResult)


def test_deserialize_stop_polling() -> None:
    """Test for deserialize function with CMD_STOP_POLLING."""
    packet = bytes([Protocol.STX.value, Command.CMD_STOP_POLLING.value, Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, StopPollingResult)


def test_deserialize_set_polling_interval() -> None:
    """Test for deserialize function with CMD_SET_POLLING_INTERVAL."""
    packet = bytes([Protocol.STX.value, Command.CMD_SET_POLLING_INTERVAL.value, Protocol.ETX.value])
    result = deserialize(packet)
    assert isinstance(result, SetPollingIntervalResult)


def test_deserialize_get_polling_interval() -> None:
    """Test for deserialize function with CMD_GET_POLLING_INTERVAL."""
    interval = 100
    params = interval.to_bytes(2, byteorder="big")
    packet = bytes(
        [Protocol.STX.value, Command.CMD_GET_POLLING_INTERVAL.value, params[0], params[1], Protocol.ETX.value]
    )
    result = deserialize(packet)
    assert isinstance(result, GetPollingIntervalResult)
    assert result.interval == interval


def test_deserialize_get_polling_report() -> None:
    """Test for deserialize function with CMD_GET_POLLING_REPORT."""
    BV: float = 5.0
    ME: List[int] = [1000, 1001, 0, 0]
    SME: List[int] = [2000, 2001, 0, 0]
    TIMESTAMP: int = 3500

    packet = bytes(
        [
            Protocol.STX.value,
            Command.CMD_GET_POLLING_REPORT.value,
            int(BV / 5 * 32767).to_bytes(2, byteorder="big", signed=True)[0],
            int(BV / 5 * 32767).to_bytes(2, byteorder="big", signed=True)[1],  # base voltage
            ME[0].to_bytes(2, byteorder="big", signed=True)[0],
            ME[0].to_bytes(2, byteorder="big", signed=True)[1],
            ME[1].to_bytes(2, byteorder="big", signed=True)[0],
            ME[1].to_bytes(2, byteorder="big", signed=True)[1],
            0x00,
            0x00,
            0x00,
            0x00,  # ME
            SME[0].to_bytes(2, byteorder="big", signed=True)[0],
            SME[0].to_bytes(2, byteorder="big", signed=True)[1],
            SME[1].to_bytes(2, byteorder="big", signed=True)[0],
            SME[1].to_bytes(2, byteorder="big", signed=True)[1],
            0x00,
            0x00,
            0x00,
            0x00,  # SME
            TIMESTAMP.to_bytes(4, byteorder="big", signed=False)[0],
            TIMESTAMP.to_bytes(4, byteorder="big", signed=False)[1],
            TIMESTAMP.to_bytes(4, byteorder="big", signed=False)[2],
            TIMESTAMP.to_bytes(4, byteorder="big", signed=False)[3],  # timestamp
            Protocol.ETX.value,
        ]
    )

    result = deserialize(packet)
    assert isinstance(result, GetPollingReportResult)
    assert result.voltage == pytest.approx(BV, rel=1e-2)
    assert result.me == ME
    assert result.sme == SME
    assert result.timestamp == TIMESTAMP
