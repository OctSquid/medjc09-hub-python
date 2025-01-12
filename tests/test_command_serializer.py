from medjc09 import (
    Command,
    serialize,
)


def test_serialize_pint() -> None:
    """Test for serialize function with CMD_PING."""
    assert serialize(Command.CMD_PING, 0x1234) == bytes([Command.CMD_PING.value, 0x12, 0x34])


def test_serialize_get_version() -> None:
    """Test for serialize function with CMD_GET_VERSION."""
    assert serialize(Command.CMD_GET_VERSION, 0x1234) == bytes([Command.CMD_GET_VERSION.value, 0x12, 0x34])


def test_serialize_get_base_voltage() -> None:
    """Test for serialize function with CMD_GET_BASE_VOLTAGE."""
    assert serialize(Command.CMD_GET_BASE_VOLTAGE, 0x1234) == bytes([Command.CMD_GET_BASE_VOLTAGE.value, 0x12, 0x34])


def test_serialize_get_connections() -> None:
    """Test for serialize function with CMD_GET_CONNECTIONS."""
    assert serialize(Command.CMD_GET_CONNECTIONS, 0x1234) == bytes([Command.CMD_GET_CONNECTIONS.value, 0x12, 0x34])


def test_serialize_get_me() -> None:
    """Test for serialize function with CMD_GET_ME."""
    assert serialize(Command.CMD_GET_ME, 0x1234) == bytes([Command.CMD_GET_ME.value, 0x12, 0x34])


def test_serialize_get_sme() -> None:
    """Test for serialize function with CMD_GET_SME."""
    assert serialize(Command.CMD_GET_SME, 0x1234) == bytes([Command.CMD_GET_SME.value, 0x12, 0x34])


def test_serialize_start_polling() -> None:
    """Test for serialize function with CMD_START_POLLING."""
    assert serialize(Command.CMD_START_POLLING, 0x1234) == bytes([Command.CMD_START_POLLING.value, 0x12, 0x34])


def test_serialize_stop_polling() -> None:
    """Test for serialize function with CMD_STOP_POLLING."""
    assert serialize(Command.CMD_STOP_POLLING, 0x1234) == bytes([Command.CMD_STOP_POLLING.value, 0x12, 0x34])


def test_serialize_set_polling_rate() -> None:
    """Test for serialize function with CMD_SET_POLLING_RATE."""
    # paramsは16bit整数とみなして 100を 2byteに分割
    # uint16_t 100 -> 0x0064 -> 0x64, 0x00
    assert serialize(Command.CMD_SET_POLLING_RATE, 0x1234, bytes([0x64, 0x00])) == bytes(
        [Command.CMD_SET_POLLING_RATE.value, 0x12, 0x34, 0x64, 0x00]
    )


def test_serialize_get_polling_interval() -> None:
    """Test for serialize function with CMD_GET_POLLING_INTERVAL."""
    assert serialize(Command.CMD_GET_POLLING_RATE, 0x1234) == bytes([Command.CMD_GET_POLLING_RATE.value, 0x12, 0x34])


def test_serialize_get_polling_report() -> None:
    """Test for serialize function with CMD_GET_POLLING_REPORT."""
    assert serialize(Command.CMD_GET_POLLING_REPORT, 0x1234) == bytes(
        [Command.CMD_GET_POLLING_REPORT.value, 0x12, 0x34]
    )
