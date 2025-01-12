import asyncio
import random
import time
from collections import deque
from typing import Callable, List, Optional, TypedDict

import serial_asyncio
from cobs import cobs

from .command import (
  Command,
  CommandResult,
  GetBaseVoltageResult,
  GetConnectionsResult,
  GetMEResult,
  GetPollingRateResult,
  GetPollingReportResult,
  GetSMEResult,
  GetVersionResult,
  deserialize,
  serialize,
)

VersionType = TypedDict("VersionType", {"major": int, "minor": int, "patch": int})
PollingReportType = TypedDict(
  "PollingReportType",
  {
    "voltage": float,
    "me": List[int],
    "sme": List[int],
    "me_voltage": List[float],
    "sme_voltage": List[float],
    "timestamp": int,
  },
)
PollingHandlerType = Callable[[PollingReportType], None]


class Medjc09:
  """MED-JC09デバイスとの通信を管理するクラス"""

  def __init__(self, port: str, baudrate: int = 921600, polling_handler: Optional[PollingHandlerType] = None):
    self._port = port
    self._baudrate = baudrate
    self._polling_handler = polling_handler
    self._is_polling_mode = False
    self._reader: Optional[asyncio.StreamReader] = None
    self._writer: Optional[asyncio.StreamWriter] = None
    self._response_queue = deque()
    self._pending_commands = {}
    self._running = False
    self._polling_id = None

  async def connect(self):
    """シリアル接続を非同期に初期化します。

    Raises:
        serial_asyncio.SerialException: シリアルポートのオープンに失敗した場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
    """
    self._reader, self._writer = await serial_asyncio.open_serial_connection(
      url=self._port,
      baudrate=self._baudrate,
    )
    self._running = True
    asyncio.create_task(self._read_loop())

  async def _read_loop(self):
    """Background task to handle incoming data"""
    while self._running:
      try:
        data = await self._reader.readuntil(b"\x00")
        if not data:
          continue

        decoded = cobs.decode(data[:-1])
        result = deserialize(decoded)

        if self._is_polling_mode and result.id == 0:
          if not isinstance(result, GetPollingReportResult):
            continue
          if self._polling_handler:
            report = {
              "voltage": result.voltage,
              "me": result.me,
              "sme": result.sme,
              "me_voltage": [result.voltage * (me_value / 4095) for me_value in result.me],
              "sme_voltage": [result.voltage * (sme_value / 4095) for sme_value in result.sme],
              "timestamp": result.timestamp,
            }
            self._polling_handler(report)
        else:
          if result.id in self._pending_commands:
            self._pending_commands[result.id].set_result(result)
            del self._pending_commands[result.id]

      except Exception as e:
        print(f"Error in read loop: {e}")
        continue

  def _generate_id(self) -> int:
    """Generate a unique 2-byte ID"""
    while True:
      new_id = random.randint(1, 0xFFFF)
      if new_id not in self._pending_commands:
        return new_id

  async def send_command(self, command: Command, params: bytes = bytes([])) -> CommandResult:
    """Send a command asynchronously and wait for response"""
    if not self._running or not self._writer:
      raise RuntimeError("Device not connected")

    command_id = self._generate_id()
    packet = serialize(command, command_id, params)
    encoded_packet = cobs.encode(packet)

    future = asyncio.get_running_loop().create_future()
    self._pending_commands[command_id] = future

    self._writer.write(encoded_packet + b"\x00")
    await self._writer.drain()

    try:
      return await asyncio.wait_for(future, timeout=5.0)
    except asyncio.TimeoutError:
      del self._pending_commands[command_id]
      raise TimeoutError("Command timed out")

  async def ping(self) -> int:
    """デバイスへのPingを送信し、応答時間を返します。

    Returns:
        int: 応答時間（ミリ秒）

    Raises:
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> latency = await device.ping()
        >>> print(f"Ping latency: {latency}ms")
    """
    start = time.time()
    await self.send_command(Command.CMD_PING)
    return int((time.time() - start) * 1000)

  async def get_version(self) -> str:
    """デバイスのファームウェアバージョンを取得します。

    Returns:
        str: バージョン文字列（例: "1.2.3"）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> version = await device.get_version()
        >>> print(f"Firmware version: {version}")
    """
    result = await self.send_command(Command.CMD_GET_VERSION)
    if isinstance(result, GetVersionResult):
      return f"{result.version.major}.{result.version.minor}.{result.version.patch}"
    raise ValueError("Unexpected result type")

  async def get_base_voltage(self) -> float:
    """ベース電圧を取得します。

    Returns:
        float: ベース電圧値（ボルト）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> voltage = await device.get_base_voltage()
        >>> print(f"Base voltage: {voltage}V")
    """
    result = await self.send_command(Command.CMD_GET_BASE_VOLTAGE)
    if isinstance(result, GetBaseVoltageResult):
      return result.voltage
    raise ValueError("Unexpected result type")

  async def get_connections(self) -> List[bool]:
    """各チャンネルの接続状態を取得します。

    Returns:
        List[bool]: 各チャンネルの接続状態（True: 接続済み, False: 未接続）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> connections = await device.get_connections()
        >>> print(f"Connections: {connections}")
    """
    result = await self.send_command(Command.CMD_GET_CONNECTIONS)
    if isinstance(result, GetConnectionsResult):
      return result.connections
    raise ValueError("Unexpected result type")

  async def get_me(self) -> List[int]:
    """ME（Main Electrode）の測定値を取得します。

    Returns:
        List[int]: 各MEチャンネルの測定値（0-4095）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> me_values = await device.get_me()
        >>> print(f"ME values: {me_values}")
    """
    result = await self.send_command(Command.CMD_GET_ME)
    if isinstance(result, GetMEResult):
      return result.me
    raise ValueError("Unexpected result type")

  async def get_sme(self) -> List[int]:
    """SME（Sub Electrode）の測定値を取得します。

    Returns:
        List[int]: 各SMEチャンネルの測定値（0-4095）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> sme_values = await device.get_sme()
        >>> print(f"SME values: {sme_values}")
    """
    result = await self.send_command(Command.CMD_GET_SME)
    if isinstance(result, GetSMEResult):
      return result.sme
    raise ValueError("Unexpected result type")

  async def get_polling_rate(self) -> int:
    """現在のポーリングレートを取得します。

    Returns:
        int: ポーリングレート（Hz）

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> rate = await device.get_polling_rate()
        >>> print(f"Current polling rate: {rate}Hz")
    """
    result = await self.send_command(Command.CMD_GET_POLLING_RATE)
    if isinstance(result, GetPollingRateResult):
      return result.rate
    raise ValueError("Unexpected result type")

  async def set_polling_rate(self, rate: int) -> None:
    """ポーリングレートを設定します。

    Args:
        rate (int): 設定するポーリングレート（Hz）

    Raises:
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> await device.set_polling_rate(100)  # 100Hzに設定
    """
    await self.send_command(Command.CMD_SET_POLLING_RATE, rate.to_bytes(2, byteorder="big"))

  async def get_polling_report(self) -> PollingReportType:
    """最新のポーリングレポートを取得します。

    Returns:
        PollingReportType: ポーリングレポートを含む辞書。以下のキーを含む:
            - voltage (float): ベース電圧
            - me (List[int]): ME測定値
            - sme (List[int]): SME測定値
            - me_voltage (List[float]): ME電圧値
            - sme_voltage (List[float]): SME電圧値
            - timestamp (int): タイムスタンプ

    Raises:
        ValueError: 予期しない結果タイプが返された場合
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> report = await device.get_polling_report()
        >>> print(f"Voltage: {report['voltage']}V")
        >>> print(f"ME voltages: {report['me_voltage']}")
    """
    result = await self.send_command(Command.CMD_GET_POLLING_REPORT)
    if isinstance(result, GetPollingReportResult):
      return {
        "voltage": result.voltage,
        "me": result.me,
        "sme": result.sme,
        "me_voltage": [result.voltage * (me_value / 4095) for me_value in result.me],
        "sme_voltage": [result.voltage * (sme_value / 4095) for sme_value in result.sme],
        "timestamp": result.timestamp,
      }
    raise ValueError("Unexpected result type")

  async def start_polling(self) -> None:
    """ポーリングモードを開始します。

    Raises:
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> await device.start_polling()
    """
    self._is_polling_mode = True
    result = await self.send_command(Command.CMD_START_POLLING)
    self._polling_id = result.id

  async def stop_polling(self) -> None:
    """ポーリングモードを停止します。

    Raises:
        TimeoutError: コマンドがタイムアウトした場合
        RuntimeError: デバイスが接続されていない場合

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> await device.start_polling()
        >>> # 何らかの処理
        >>> await device.stop_polling()
    """
    self._is_polling_mode = False
    await self.send_command(Command.CMD_STOP_POLLING)
    self._polling_id = None

  async def close(self) -> None:
    """接続を閉じてリソースを解放します。

    Example:
        >>> device = Medjc09('/dev/tty.usbserial-1234')
        >>> await device.connect()
        >>> # 何らかの処理
        >>> await device.close()
    """
    self._running = False
    if self._writer:
      self._writer.close()
      await self._writer.wait_closed()
