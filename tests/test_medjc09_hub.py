import os

import dotenv
import pytest
import serial
from medjc09_hub_python.medjc09_hub import Medjc09

dotenv.load_dotenv()


port = os.environ.get("TEST_PORT")
is_not_connected = True
try:
    if port is None:
        raise ValueError("TEST_PORT is not set.")
    ser = serial.Serial(port, 115200, timeout=1)
    is_not_connected = False
except serial.SerialException:
    is_not_connected = True
except ValueError:
    is_not_connected = True
finally:
    if is_not_connected is False:
        ser.close()


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_base_voltage() -> None:
    """Test for get_base_voltage method."""
    medjc09 = Medjc09(port)
    voltage = medjc09.get_base_voltage()
    assert isinstance(voltage, float)
    assert voltage >= 0.0
    assert voltage <= 5.0


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_connections() -> None:
    """Test for get_connections method."""
    medjc09 = Medjc09(port)
    connections = medjc09.get_connections()
    assert isinstance(connections, list)
    assert len(connections) == 4
    for connection in connections:
        assert isinstance(connection, bool)


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_me() -> None:
    """Test for get_me method."""
    medjc09 = Medjc09(port)
    me = medjc09.get_me()
    assert isinstance(me, list)
    assert len(me) == 4
    for value in me:
        assert isinstance(value, int)
        assert value >= -32768
        assert value <= 32767


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_me_as_voltage() -> None:
    """Test for get_me_as_voltage method."""
    medjc09 = Medjc09(port)
    me_voltage = medjc09.get_me_as_voltage()
    assert isinstance(me_voltage, list)
    assert len(me_voltage) == 4
    for value in me_voltage:
        assert isinstance(value, float)
        assert value >= -5.0 / 2
        assert value <= 5.0 / 2


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_sme() -> None:
    """Test for get_sme method."""
    medjc09 = Medjc09(port)
    sme = medjc09.get_sme()
    assert isinstance(sme, list)
    assert len(sme) == 4
    for value in sme:
        assert isinstance(value, int)
        assert value >= 0
        assert value <= 32767


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_sme_as_voltage() -> None:
    """Test for get_sme_as_voltage method."""
    medjc09 = Medjc09(port)
    sme_voltage = medjc09.get_sme_as_voltage()
    assert isinstance(sme_voltage, list)
    assert len(sme_voltage) == 4
    for value in sme_voltage:
        assert isinstance(value, float)
        assert value >= 0.0
        assert value <= 5.0


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_close() -> None:
    """Test for close method."""
    medjc09 = Medjc09(port)
    medjc09.close()
    assert medjc09._ser.is_open is False
