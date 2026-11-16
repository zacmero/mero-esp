# ESP hardware reconnaissance

Evidence collected 2026-11-16 on the connected board. The original flash was read twice and compared before temporarily installing diagnostic firmware. No eFuses were written. See the active test results below and the recovery record in `docs/evidence/`.

**Final board state:** original firmware restored. A full 4,194,304-byte readback matched the original dump byte for byte, with SHA-256 `d380d8c94ee05959cab390e909cc9c2c3b85f4a8c9079df1f8f9d2788c7fdaf0`. Temporary diagnostic firmware is no longer installed.

For copy-and-paste identification, serial, backup, radio-test and recovery commands, see [Probe the board yourself](docs/probe-commands.md).

## Identified hardware

| Item | Observed value |
| --- | --- |
| Serial port | `/dev/ttyACM1` |
| Persistent device path | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00` |
| USB bridge identity | `1a86 USB Single Serial` |
| Chip | ESP32-D0WD-V3, revision v3.1 |
| CPU | Dual core plus LP core, 240 MHz reported |
| Crystal | 40 MHz |
| MAC reported by esptool | `88:57:21:70:81:00` |
| Flash manufacturer ID | `0x68` (esptool prints hexadecimal; vendor not independently identified) |
| Flash device ID | `0x4016` |
| Flash capacity | 4 MB |
| Flash voltage | 3.3 V, strapping-pin selection reported |

`/dev/ttyACM0` is a Turing UsbMonitor, not this board. Device numbers can change after reconnecting. Exact development-board/module model remains unknown without inspecting its markings.

## Tool installation and reproduction

The supplied pacman transaction failed with package-download 404s. Stale repository metadata or mirror synchronization is a likely explanation, not a confirmed diagnosis. An isolated uv environment installed esptool 5.6.0 and pyserial successfully without changing system packages. Exact installed versions are recorded in `requirements-tools.txt`.

```bash
rtk proxy uv venv .venv
rtk proxy uv pip install --python .venv/bin/python -r requirements-tools.txt
rtk proxy .venv/bin/python -m serial.tools.list_ports -v
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 flash-id
```

## Verification

USB enumeration, serial connection, ROM-loader communication, RAM-stub execution and flash-ID reading passed. Two complete 4,194,304-byte backups matched byte for byte. Their SHA-256 is `d380d8c94ee05959cab390e909cc9c2c3b85f4a8c9079df1f8f9d2788c7fdaf0`. Dumps remain local under ignored `backups/`.

The installed application at `0x100000` identifies project `esp-at`, compiled May 20 2022 11:11:58, with ESP-IDF `qa-test-v4.3.3-20220423`. Its checksum and validation hash are valid. App version is `v2.3.0.0_esp32c3-142-g5641e0a-d`; that software label does not override the detected ESP32-D0WD-V3 silicon. The serial application banner reports `WROOM-32`, `2.4.0`, and `max tx power=78,ret=0`. The precise module/carrier model still requires checking its markings. Original partition and image metadata are retained in [evidence](docs/evidence/).

`get-security-info` failed through stub and ROM paths, but read-only `espefuse summary` resolved the security state: `FLASH_CRYPT_CNT=0`, `ABS_DONE_0=False`, `ABS_DONE_1=False`, `UART_DOWNLOAD_DIS=False`. Flash encryption and secure boot were disabled at capture; UART download was enabled. Exact errors and selected eFuse fields are preserved.

The [ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) specifies 2.4 GHz 802.11 b/g/n Wi-Fi and Bluetooth 4.2 BR/EDR plus BLE. Active tests used temporary official MicroPython v1.29.0:

| Test | Result |
| --- | --- |
| Repeated Wi-Fi scans | Passed; multiple networks detected, only aggregate counts/channels/RSSI logged |
| Wi-Fi association and DHCP | Passed using one locally saved matching NetworkManager profile |
| Wi-Fi DNS and TCP data | Passed; HTTP request to example.com returned `HTTP/1.1 200 OK` |
| Wi-Fi RSSI during network test | -46 dBm |
| Wi-Fi protocol mask | 7 reported by the driver; enabled b/g/n capabilities, not negotiated PHY proof |
| SoftAP initialization | Passed; local interface at 192.168.4.1; external client association not measured |
| BLE scan | Passed; advertisement reports received |
| BLE advertising and connection | Passed using the host's BlueZ adapter |
| BLE GATT reads/writes/notifications | Passed; 20 checked write/notification round trips plus initial/final reads |
| Bluetooth Classic discovery | Passed; host discovered `MERO-ESP32-CLASSIC` |
| Bluetooth Classic SPP/RFCOMM | Passed; 20 exact echo round trips, 320 bytes each direction |

Scripts retain no nearby SSIDs, BSSIDs or peer addresses in public scan evidence. Wi-Fi credentials are read locally and injected into the diagnostic interpreter in RAM; they are not printed or written to host files or Git. The MicroPython device scripts turn off their radios afterward; the Classic echo service ends when its temporary firmware is replaced.

Classic testing used a separate minimal Arduino BluetoothSerial echo image under `diagnostics/classic/`, pinned to PlatformIO espressif32 6.9.0 / Arduino 2.0.17. This temporary SPP test checks unauthenticated data transfer; it does not establish pairing security or audio-profile behavior. The Classic host script uses system Python because the uv Python lacks `socket.AF_BLUETOOTH`.

The DTR/RTS behavior of this USB bridge caused the mpremote CLI to fail entering raw REPL after the first run. `scripts/run_device.py` releases both lines before using mpremote's transport. Initial SoftAP activation-order and BLE callback-test issues were corrected; unsuccessful attempts remain in evidence. On this host, interleaving GATT reads during a notification subscription produced duplicate Value callbacks, so the final test checks reads outside that subscription.

These are functional bench checks. They do not certify RF range, every Bluetooth profile, each Wi-Fi PHY mode, simultaneous loaded coexistence, all GPIOs, or long-term power stability.

## Firmware preservation workflow for later work

For this ESP32, the documented [esptool read-flash command](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html) captures the detected 4 MB address range. Two matching full reads were performed in this session. To repeat on an unchanged board:

```bash
rtk proxy mkdir -p backups
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 read-flash 0 0x400000 backups/esp32-capture-a.bin
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 read-flash 0 0x400000 backups/esp32-capture-b.bin
rtk proxy sha256sum backups/esp32-capture-a.bin backups/esp32-capture-b.bin
rtk proxy cmp backups/esp32-capture-a.bin backups/esp32-capture-b.bin
```

Check both reads succeeded, each file is 4,194,304 bytes, and hashes match; investigate differences before treating a backup as reliable. Keep dumps private because they may contain credentials. Preserve hashes, tool versions, board markings, wiring photos and command logs alongside each device's backup.

Routers, watches and receivers require individual identification of SoC, storage, interface and electrical levels. Esptool operates Espressif bootloaders; this board is not yet a general-purpose flash programmer. Other targets may require UART console access, SPI NOR, NAND, eMMC or JTAG equipment. Identify ground, pin functions and voltage before wiring; do not connect an unknown voltage or simultaneously power a flash chip from two sources. Do not modify firmware until its original contents are preserved and the recovery path is understood.
