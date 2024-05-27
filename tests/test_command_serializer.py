from medjc09_hub_python.command import (
    Command,
    Protocol,
    serialize,
)


def test_serialize_get_version() -> None:
    """Test for serialize function with CMD_GET_VERSION."""
    assert serialize(Command.CMD_GET_VERSION) == bytes(
        [Protocol.STX.value, Command.CMD_GET_VERSION.value, Protocol.ETX.value]
    )


def test_serialize_get_base_voltage() -> None:
    """Test for serialize function with CMD_GET_BASE_VOLTAGE."""
    assert serialize(Command.CMD_GET_BASE_VOLTAGE) == bytes(
        [Protocol.STX.value, Command.CMD_GET_BASE_VOLTAGE.value, Protocol.ETX.value]
    )


def test_serialize_get_connections() -> None:
    """Test for serialize function with CMD_GET_CONNECTIONS."""
    assert serialize(Command.CMD_GET_CONNECTIONS) == bytes(
        [Protocol.STX.value, Command.CMD_GET_CONNECTIONS.value, Protocol.ETX.value]
    )


def test_serialize_get_me() -> None:
    """Test for serialize function with CMD_GET_ME."""
    assert serialize(Command.CMD_GET_ME) == bytes([Protocol.STX.value, Command.CMD_GET_ME.value, Protocol.ETX.value])


def test_serialize_get_sme() -> None:
    """Test for serialize function with CMD_GET_SME."""
    assert serialize(Command.CMD_GET_SME) == bytes([Protocol.STX.value, Command.CMD_GET_SME.value, Protocol.ETX.value])


def test_serialize_start_polling() -> None:
    """Test for serialize function with CMD_START_POLLING."""
    assert serialize(Command.CMD_START_POLLING) == bytes(
        [Protocol.STX.value, Command.CMD_START_POLLING.value, Protocol.ETX.value]
    )


def test_serialize_stop_polling() -> None:
    """Test for serialize function with CMD_STOP_POLLING."""
    assert serialize(Command.CMD_STOP_POLLING) == bytes(
        [Protocol.STX.value, Command.CMD_STOP_POLLING.value, Protocol.ETX.value]
    )


def test_serialize_set_polling_interval() -> None:
    """Test for serialize function with CMD_SET_POLLING_INTERVAL."""
    # paramsは16bit整数とみなして 100を 2byteに分割
    # uint16_t 100 -> 0x0064 -> 0x64, 0x00
    assert serialize(Command.CMD_SET_POLLING_INTERVAL, bytes([0x64, 0x00])) == bytes(
        [Protocol.STX.value, Command.CMD_SET_POLLING_INTERVAL.value, 0x64, 0x00, Protocol.ETX.value]
    )


def test_serialize_get_polling_interval() -> None:
    """Test for serialize function with CMD_GET_POLLING_INTERVAL."""
    assert serialize(Command.CMD_GET_POLLING_INTERVAL) == bytes(
        [Protocol.STX.value, Command.CMD_GET_POLLING_INTERVAL.value, Protocol.ETX.value]
    )


def test_serialize_get_polling_report() -> None:
    """Test for serialize function with CMD_GET_POLLING_REPORT."""
    assert serialize(Command.CMD_GET_POLLING_REPORT) == bytes(
        [Protocol.STX.value, Command.CMD_GET_POLLING_REPORT.value, Protocol.ETX.value]
    )
