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
