# MEDJC09 Hub Python

[![PyPI](https://img.shields.io/pypi/v/medjc09-hub-python)](https://pypi.org/project/medjc09-hub-python/)
[![Python](https://img.shields.io/pypi/pyversions/medjc09-hub-python)](https://pypi.org/project/medjc09-hub-python/)

MED-JC09デバイスと通信するためのPythonライブラリです。

## 概要

このライブラリは、MED-JC09ハブデバイスとシリアル通信を行うための非同期Pythonインターフェースを提供します。以下の機能をサポートしています：

- デバイスとの接続管理
- コマンド送信とレスポンス処理
- ポーリングモードによる定期的なデータ取得
- 各種センサーデータの取得

## インストール方法

Ryeを使用してインストールします：

```bash
rye add medjc09-hub-python
```

または、pipを使用する場合：

```bash
pip install medjc09-hub-python
```

## 使用方法

### 基本的な使い方

```python
import asyncio
from medjc09 import Medjc09

async def main():
    device = Medjc09('/dev/tty.usbserial-1234')
    await device.connect()
    
    # バージョン情報の取得
    version = await device.get_version()
    print(f"Firmware version: {version}")
    
    # ベース電圧の取得
    voltage = await device.get_base_voltage()
    print(f"Base voltage: {voltage}V")
    
    await device.close()

asyncio.run(main())
```

### ポーリングモードの使用

デバイスの初期化時にポーリングハンドラーを指定することで、ポーリングモードを使用できます。

```python
def polling_handler(report):
    print(f"Voltage: {report['voltage']}V")
    print(f"ME voltages: {report['me_voltage']}")

async def main():
    device = Medjc09('/dev/tty.usbserial-1234', polling_handler=polling_handler)
    await device.connect()
    
    # ポーリングモード開始
    await device.start_polling()
    
    # 10秒間ポーリング
    await asyncio.sleep(10)
    
    # ポーリングモード停止
    await device.stop_polling()
    
    await device.close()

asyncio.run(main())
```

## 主要な機能

- `connect()`: デバイスに接続
- `close()`: 接続を閉じる
- `get_version()`: ファームウェアバージョンを取得
- `get_base_voltage()`: ベース電圧を取得
- `get_connections()`: 各チャンネルの接続状態を取得
- `get_me()`: ME（Main Electrode）の測定値を取得
- `get_sme()`: SME（Sub Electrode）の測定値を取得
- `start_polling()`: ポーリングモードを開始
- `stop_polling()`: ポーリングモードを停止

## テストの実行

プロジェクトのテストを実行するには、以下のコマンドを使用します：

```bash
rye run pytest
```

## ビルド方法

```bash
rye build --wheel
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
