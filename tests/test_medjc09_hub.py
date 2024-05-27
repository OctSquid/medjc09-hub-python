import os
import time
from typing import List

import dotenv
import pytest
import serial
from medjc09_hub_python.medjc09_hub import Medjc09, PollingReportType

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
def test_start_polling() -> None:
    """Test for start_polling method."""
    medjc09 = Medjc09(port)
    medjc09.start_polling()
    assert medjc09.is_polling() is True
    medjc09.stop_polling()


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_stop_polling() -> None:
    """Test for stop_polling method."""
    medjc09 = Medjc09(port)
    medjc09.start_polling()
    medjc09.stop_polling()
    assert medjc09.is_polling() is False


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_set_get_polling_interval() -> None:
    """Test for set_polling_interval method."""
    medjc09 = Medjc09(port)
    medjc09.set_polling_interval(100)
    assert medjc09.get_polling_interval() == 100


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_get_polling_report() -> None:
    """Test for get_polling_report method."""
    medjc09 = Medjc09(port)
    timer = time.time()
    report = medjc09.get_polling_report()
    assert valid_polling_report(report)
    timer = time.time() - timer
    assert timer < 1.0


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_polling_mode() -> None:
    """Test for polling mode.
    Polling interval is 50ms and duration is 1001ms.
    """
    interval = 50
    duration = 1001

    count = {"value": 0}
    reports: List[PollingReportType] = []

    def test_polling_report(report: PollingReportType) -> None:
        assert valid_polling_report(report)
        reports.append(report)
        count["value"] += 1

    medjc09 = Medjc09(port, 115200, test_polling_report)
    medjc09.set_polling_interval(interval)
    medjc09.start_polling()
    start_time: float = time.time()
    total_time: float = 0
    while total_time < duration // 1000:
        medjc09.update()
        total_time = time.time() - start_time
    medjc09.stop_polling()

    assert count["value"] == duration // interval


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
def test_close() -> None:
    """Test for close method."""
    medjc09 = Medjc09(port)
    medjc09.close()
    assert medjc09._ser.is_open is False


def valid_polling_report(report: PollingReportType) -> bool:
    """Validate polling report

    Args:
        report (PollingReportType): Polling report

    Returns:
        bool: Validation result
    """
    if "voltage" not in report:
        return False
    if "me" not in report:
        return False
    if "sme" not in report:
        return False
    if not isinstance(report["voltage"], float):
        return False
    if report["voltage"] < 0.0 or report["voltage"] > 5.0:
        return False
    if not isinstance(report["me"], list):
        return False
    if len(report["me"]) != 4:
        return False
    for value in report["me"]:
        if not isinstance(value, int):
            return False
        if value < -32768 or value > 32767:
            return False
    if not isinstance(report["me_voltage"], list):
        return False
    if len(report["me_voltage"]) != 4:
        return False
    for value in report["me_voltage"]:
        if not isinstance(value, float):
            return False
        if value < -5.0 / 2 or value > 5.0 / 2:
            return False
    if not isinstance(report["sme"], list):
        return False
    if len(report["sme"]) != 4:
        return False
    for value in report["sme"]:
        if not isinstance(value, int):
            return False
        if value < 0 or value > 32767:
            return False
    if not isinstance(report["sme_voltage"], list):
        return False
    if len(report["sme_voltage"]) != 4:
        return False
    for value in report["sme_voltage"]:
        if not isinstance(value, float):
            return False
        if value < 0.0 or value > 5.0:
            return False
    if not isinstance(report["timestamp"], int):
        return False
    if report["timestamp"] < 0:
        return False

    return True
