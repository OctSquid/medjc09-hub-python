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
