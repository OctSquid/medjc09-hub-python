"""Test for Medjc09 class.

実機を接続してテストするため，環境変数 TEST_PORT に接続するポート名を設定してください．
また，環境変数 TEST_BAUTRATE にボーレートを設定してください．
それらが設定されていない場合は，テストはスキップされます．
"""

import asyncio
import os
import time
from typing import List

import dotenv
import pytest
import serial
from medjc09 import Medjc09, PollingReportType

dotenv.load_dotenv()


@pytest.fixture(scope="module")
def event_loop():
  """Create an instance of the default event loop for each test case."""
  loop = asyncio.get_event_loop_policy().new_event_loop()
  yield loop
  loop.close()


# 実機の接続情報が設定されているか確認
port = os.environ.get("TEST_PORT")
_bautrate = os.environ.get("TEST_BAUTRATE")
bautrate = int(_bautrate) if _bautrate is not None else None
is_not_connected = True
try:
  if port is None:
    raise ValueError("TEST_PORT is not set.")
  if bautrate is None:
    raise ValueError("TEST_BAUTRATE is not set.")
  ser = serial.Serial(port, bautrate, timeout=1)
  is_not_connected = False
except serial.SerialException:
  is_not_connected = True
except ValueError:
  is_not_connected = True
finally:
  if is_not_connected is False:
    ser.close()


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_connect() -> None:
  """Test for connect method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  assert medjc09._running is True
  medjc09.close()


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_ping() -> None:
  """Test for ping method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_get_version() -> None:
  """Test for get_version method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  version = await medjc09.get_version()
  assert isinstance(version, str)
  assert version.startswith("1.")


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_get_base_voltage() -> None:
  """Test for get_base_voltage method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  voltage = await medjc09.get_base_voltage()
  assert isinstance(voltage, float)
  assert voltage >= 0.0
  assert voltage <= 5.0


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_get_me() -> None:
  """Test for get_me method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  me = await medjc09.get_me()
  assert isinstance(me, list)
  assert len(me) == 4
  for value in me:
    assert isinstance(value, int)
    assert value >= -32768
    assert value <= 32767


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_get_sme() -> None:
  """Test for get_sme method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  sme = await medjc09.get_sme()
  assert isinstance(sme, list)
  assert len(sme) == 4
  for value in sme:
    assert isinstance(value, int)
    assert value >= 0
    assert value <= 32767


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_start_polling() -> None:
  """Test for start_polling method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  await medjc09.start_polling()
  assert medjc09._is_polling_mode is True
  await asyncio.sleep(0.2)
  await medjc09.stop_polling()
  assert medjc09._is_polling_mode is False


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_stop_polling() -> None:
  """Test for stop_polling method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  await medjc09.start_polling()
  await medjc09.stop_polling()
  assert medjc09._is_polling_mode is False


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_set_get_polling_rate() -> None:
  """Test for set_polling_rate method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  await medjc09.set_polling_rate(100)
  assert await medjc09.get_polling_rate() == 100
  await medjc09.set_polling_rate(1000)
  assert await medjc09.get_polling_rate() == 1000


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_get_polling_report() -> None:
  """Test for get_polling_report method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  timer = time.time()
  report = await medjc09.get_polling_report()
  assert valid_polling_report(report)
  timer = time.time() - timer
  assert timer < 1.0


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_polling_mode() -> None:
  """Test for polling mode.
  Polling rate is 1000Hz and duration is 1001ms.
  """
  rate = 1000
  duration = 1500

  count = {"value": 0}
  reports: List[PollingReportType] = []

  def test_polling_report(report: PollingReportType) -> None:
    assert valid_polling_report(report)
    reports.append(report)
    count["value"] += 1

  medjc09 = Medjc09(port, 921600, test_polling_report)
  await medjc09.connect()
  await medjc09.set_polling_rate(rate)
  await medjc09.start_polling()
  await asyncio.sleep(duration / 1000)
  medjc09.stop_polling()

  # ポーリングレポート間の平均時間差を検証
  if len(reports) > 1:
    diff = [reports[i + 1]["timestamp"] - reports[i]["timestamp"] for i in range(len(reports) - 1)]
    avg = sum(diff) / len(diff)
    assert avg >= 1 / rate * 0.9

  assert count["value"] >= rate


@pytest.mark.skipif(is_not_connected, reason="Device is not connected.")
@pytest.mark.asyncio
async def test_close() -> None:
  """Test for close method."""
  medjc09 = Medjc09(port, bautrate)
  await medjc09.connect()
  await medjc09.close()
  assert medjc09._running is False


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
