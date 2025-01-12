from typing import List

import pytest
from medjc09 import (
  Command,
  ErrorCodes,
  ErrorResponse,
  GetBaseVoltageResult,
  GetConnectionsResult,
  GetMEResult,
  GetPollingRateResult,
  GetPollingReportResult,
  GetSMEResult,
  GetVersionResult,
  PingResult,
  SetPollingIntervalResult,
  StartPollingResult,
  StopPollingResult,
  deserialize,
)


def test_deserialize_ping() -> None:
  """Test for deserialize function with CMD_PING."""
  packet = bytes([Command.CMD_PING.value, 0x12, 0x34])
  result = deserialize(packet)
  assert isinstance(result, PingResult)
  assert result.id == 0x1234


def test_deserialize_get_version() -> None:
  """Test for deserialize function with CMD_GET_VERSION."""
  packet = bytes([Command.CMD_GET_VERSION.value, 0x12, 0x34, 0x01, 0x00, 0x00])
  result = deserialize(packet)
  assert isinstance(result, GetVersionResult)
  assert result.id == 0x1234
  assert result.version.major == 1
  assert result.version.minor == 0
  assert result.version.patch == 0


def test_deserialize_get_base_voltage() -> None:
  """Test for deserialize function with CMD_GET_BASE_VOLTAGE."""
  vb_value = 4095  # Max value corresponds to 3.3V
  packet = bytes([Command.CMD_GET_BASE_VOLTAGE.value, 0x12, 0x34]) + vb_value.to_bytes(2, byteorder="big", signed=True)
  result = deserialize(packet)
  assert isinstance(result, GetBaseVoltageResult)
  assert result.id == 0x1234
  assert result.voltage == pytest.approx(3.3, rel=1e-2)


def test_deserialize_get_connections() -> None:
  """Test for deserialize function with CMD_GET_CONNECTIONS."""
  packet = bytes([Command.CMD_GET_CONNECTIONS.value, 0x12, 0x34, 0x01, 0x00, 0x00, 0x00])
  result = deserialize(packet)
  assert isinstance(result, GetConnectionsResult)
  assert result.id == 0x1234
  assert result.connections == [True, False, False, False]


def test_deserialize_get_me() -> None:
  """Test for deserialize function with CMD_GET_ME."""
  me_values = [1000, 1001, 0, 0]
  me_bytes = b"".join([v.to_bytes(2, byteorder="big", signed=True) for v in me_values])
  packet = bytes([Command.CMD_GET_ME.value, 0x12, 0x34]) + me_bytes
  result = deserialize(packet)
  assert isinstance(result, GetMEResult)
  assert result.id == 0x1234
  assert result.me == me_values


def test_deserialize_get_sme() -> None:
  """Test for deserialize function with CMD_GET_SME."""
  sme_values = [2000, 2001, 0, 0]
  sme_bytes = b"".join([v.to_bytes(2, byteorder="big", signed=True) for v in sme_values])
  packet = bytes([Command.CMD_GET_SME.value, 0x12, 0x34]) + sme_bytes
  result = deserialize(packet)
  assert isinstance(result, GetSMEResult)
  assert result.id == 0x1234
  assert result.sme == sme_values


def test_deserialize_start_polling() -> None:
  """Test for deserialize function with CMD_START_POLLING."""
  packet = bytes([Command.CMD_START_POLLING.value, 0x12, 0x34])
  result = deserialize(packet)
  assert isinstance(result, StartPollingResult)
  assert result.id == 0x1234


def test_deserialize_stop_polling() -> None:
  """Test for deserialize function with CMD_STOP_POLLING."""
  packet = bytes([Command.CMD_STOP_POLLING.value, 0x12, 0x34])
  result = deserialize(packet)
  assert isinstance(result, StopPollingResult)
  assert result.id == 0x1234


def test_deserialize_set_polling_rate() -> None:
  """Test for deserialize function with CMD_SET_POLLING_RATE."""
  packet = bytes([Command.CMD_SET_POLLING_RATE.value, 0x12, 0x34])
  result = deserialize(packet)
  assert isinstance(result, SetPollingIntervalResult)
  assert result.id == 0x1234


def test_deserialize_get_polling_rate() -> None:
  """Test for deserialize function with CMD_GET_POLLING_RATE."""
  rate = 100
  params = rate.to_bytes(2, byteorder="big")
  packet = bytes([Command.CMD_GET_POLLING_RATE.value, 0x12, 0x34, params[0], params[1]])
  result = deserialize(packet)
  assert isinstance(result, GetPollingRateResult)
  assert result.id == 0x1234
  assert result.rate == rate


def test_deserialize_get_polling_report() -> None:
  """Test for deserialize function with CMD_GET_POLLING_REPORT."""
  BV: float = 3.3
  ME: List[int] = [1000, 1001, 0, 0]
  SME: List[int] = [2000, 2001, 0, 0]
  TIMESTAMP: int = 3500

  packet = bytes(
    [
      Command.CMD_GET_POLLING_REPORT.value,
      0x12,
      0x34,
      int(BV / 3.3 * 4095).to_bytes(2, byteorder="big", signed=True)[0],
      int(BV / 3.3 * 4095).to_bytes(2, byteorder="big", signed=True)[1],  # base voltage
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
    ]
  )

  result = deserialize(packet)
  assert isinstance(result, GetPollingReportResult)
  assert result.voltage == pytest.approx(BV, rel=1e-2)
  assert result.me == ME
  assert result.sme == SME
  assert result.timestamp == TIMESTAMP


def test_deserialize_error_response() -> None:
  """Test for deserialize function with error response."""
  # Test all error codes
  error_codes = [
    (ErrorCodes.ERR_SYNTAX, 0x01),
    (ErrorCodes.ERR_INVALID_CMD, 0x11),
    (ErrorCodes.ERR_INVALID_PARAM, 0x21),
  ]

  for error_code, code_value in error_codes:
    packet = bytes([0xFE, code_value, 0xFD])
    result = deserialize(packet)
    assert isinstance(result, ErrorResponse)
    assert result.error_code == error_code

  # Test boundary cases
  # Minimum valid error code
  packet = bytes([0xFE, 0x01, 0xFD])
  result = deserialize(packet)
  assert isinstance(result, ErrorResponse)
  assert result.error_code == ErrorCodes.ERR_SYNTAX

  # Maximum valid error code
  packet = bytes([0xFE, 0x21, 0xFD])
  result = deserialize(packet)
  assert isinstance(result, ErrorResponse)
  assert result.error_code == ErrorCodes.ERR_INVALID_PARAM

  # Invalid error packet length (too short)
  with pytest.raises(ValueError, match="Invalid error packet length"):
    packet = bytes([0xFE, 0x01])
    deserialize(packet)

  # Invalid error packet length (too long)
  with pytest.raises(ValueError, match="Invalid error packet length"):
    packet = bytes([0xFE, 0x01, 0xFD, 0x00])
    deserialize(packet)

  # Invalid error code (below minimum)
  with pytest.raises(ValueError, match="Invalid error code"):
    packet = bytes([0xFE, 0x00, 0xFD])
    deserialize(packet)

  # Invalid error code (above maximum)
  with pytest.raises(ValueError, match="Invalid error code"):
    packet = bytes([0xFE, 0x22, 0xFD])
    deserialize(packet)

  # Invalid start byte
  with pytest.raises(ValueError):
    packet = bytes([0xFF, 0x01, 0xFD])
    deserialize(packet)

  # Invalid end byte
  with pytest.raises(ValueError, match="Invalid error packet end byte"):
    packet = bytes([0xFE, 0x01, 0xFF])
    deserialize(packet)

  # Test error code validation
  with pytest.raises(ValueError, match="Invalid error code"):
    packet = bytes([0xFE, 0x00, 0xFD])
    deserialize(packet)

  with pytest.raises(ValueError, match="Invalid error code"):
    packet = bytes([0xFE, 0x22, 0xFD])
    deserialize(packet)
