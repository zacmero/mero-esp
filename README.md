# ESP hardware reconnaissance

Evidence collected 2026-11-16 on the connected board. No flash erase, firmware write, or eFuse write was performed. Esptool temporarily loaded its RAM stub and reset the board.

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
| Flash manufacturer ID | `68` (esptool output; vendor not independently identified) |
| Flash device ID | `4016` |
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

## Verification and remaining checks

USB enumeration, serial connection, ROM-loader communication, RAM-stub execution and flash-ID reading passed. A short 115200-baud serial observation captured an ESP-IDF `qa-test-v4.3.3-20220423` bootloader banner; this identifies a banner, not the complete installed application. See raw [evidence](docs/evidence/).

`get-security-info` failed through both stub and ROM paths; the exact errors are preserved. Secure boot and flash encryption status remain unknown. A command-support failure does not establish a security fault.

The [ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) specifies 2.4 GHz 802.11 b/g/n Wi-Fi and Bluetooth 4.2 BR/EDR plus BLE for this chip family. These are hardware capabilities. Wi-Fi association, packet transfer, Bluetooth discovery, BLE connection, antenna performance and coexistence have not been tested. GPIO, power stability and sustained operation also remain unverified. Preserve the installed firmware before loading radio test firmware; then test association and data transfer with an owned access point, BLE advertising/scanning and a connection with a known peer, and Classic Bluetooth discovery/connection with a compatible peer.

## Firmware preservation workflow for later work

For this ESP32, the documented [esptool read-flash command](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html) can capture the detected 4 MB address range. These commands are a future procedure and were not executed in this reconnaissance:

```bash
rtk proxy mkdir -p backups
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 read-flash 0 0x400000 backups/esp32-original-a.bin
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 read-flash 0 0x400000 backups/esp32-original-b.bin
rtk proxy sha256sum backups/esp32-original-a.bin backups/esp32-original-b.bin
rtk proxy cmp backups/esp32-original-a.bin backups/esp32-original-b.bin
```

Check both reads succeeded, each file is 4,194,304 bytes, and hashes match; investigate differences before treating a backup as reliable. Keep dumps private because they may contain credentials. Preserve hashes, tool versions, board markings, wiring photos and command logs alongside each device's backup.

Routers, watches and receivers require individual identification of SoC, storage, interface and electrical levels. Esptool operates Espressif bootloaders; this board is not yet a general-purpose flash programmer. Other targets may require UART console access, SPI NOR, NAND, eMMC or JTAG equipment. Identify ground, pin functions and voltage before wiring; do not connect an unknown voltage or simultaneously power a flash chip from two sources. Do not modify firmware until its original contents are preserved and the recovery path is understood.
