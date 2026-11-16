# Probe the board yourself

Run these from `/home/zacmero/projects/mero-esp`. Close serial monitors before running esptool; only one process should own the port.

## Identify without changing firmware

```bash
rtk proxy .venv/bin/python -m serial.tools.list_ports -v
rtk proxy udevadm info --query=property --name=/dev/ttyACM1
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 flash-id
rtk proxy .venv/bin/esptool --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 read-mac
rtk proxy .venv/bin/espefuse --port /dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00 summary
rtk proxy .venv/bin/python scripts/serial_probe.py --reset --seconds 8
rtk proxy .venv/bin/python scripts/serial_probe.py --seconds 2 --command AT --command AT+GMR --command help
```

`flash-id` prints the silicon model, revision, features, crystal, MAC and flash identification. Expected silicon: **ESP32-D0WD-V3 revision v3.1**, flash **4 MB**. `espefuse summary` only reads; never substitute a burn command. Keep a full eFuse summary private because other boards can expose sensitive provisioned data.

The USB identity describes the bridge. The silicon model describes the chip. The application banner reports `WROOM-32`; verify the shield silkscreen to establish the precise module and carrier-board name. Software cannot reliably identify a generic development board's vendor or PCB revision.

An absent AT response on this USB connection does not prove broken firmware: standard ESP-AT uses a separate command UART. See [Espressif's UART wiring documentation](https://docs.espressif.com/projects/esp-at/en/latest/esp32/Get_Started/Hardware_connection.html). Avoid guessing GPIO wiring.

## Check the local backups

These files remain on this machine under ignored `backups/`; they are not uploaded to GitHub.

```bash
rtk proxy wc -c backups/esp32-original-a.bin backups/esp32-original-b.bin
rtk proxy sha256sum backups/esp32-original-a.bin backups/esp32-original-b.bin
rtk proxy cmp backups/esp32-original-a.bin backups/esp32-original-b.bin
rtk proxy .venv/bin/esptool image-info backups/original-app.bin
```

Each full dump must be 4,194,304 bytes; both original hashes must match. `cmp` succeeds silently. `original-app.bin` is the application extracted from the original dump at offset `0x100000`. Its metadata describes the installed software, not the silicon model.

## Repeat the temporary radio diagnostics

This procedure erases the current firmware. First capture and compare two fresh full-flash backups if the board has changed since this session. Do not overwrite the preserved originals. Only continue when both backups match and you have a verified recovery image. The following commands use the original image preserved during this session.

Download the [official ESP32 generic MicroPython v1.29.0 image](https://micropython.org/download/ESP32_GENERIC/) if absent:

```bash
rtk proxy curl --fail --location --output backups/ESP32_GENERIC-20260824-v1.29.0.bin https://micropython.org/resources/firmware/ESP32_GENERIC-20260824-v1.29.0.bin
rtk proxy sha256sum backups/ESP32_GENERIC-20260824-v1.29.0.bin
```

Expected diagnostic image SHA-256: `e67ad6015a0a504c1fec9aa9bbf589d0432ed28e62546f4f8dd8a147f8bd95f6`.

```bash
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 erase-flash
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 --baud 921600 write-flash 0x1000 backups/ESP32_GENERIC-20260824-v1.29.0.bin
rtk proxy .venv/bin/python scripts/run_device.py scripts/radio_probe_device.py
```

The device script runs in RAM, prints identity and aggregate Wi-Fi scan results, starts a temporary WPA2 SoftAP, scans BLE advertisements and then advertises `MERO-ESP32-PROBE` for up to 90 seconds. It switches the radios off afterward. The wrapper releases DTR/RTS before entering the REPL, which is necessary for reliable access on this board.

When `BLE_READY` appears, run this in a second terminal:

```bash
rtk proxy .venv/bin/python scripts/ble_probe_host.py --address 88:57:21:70:81:02
```

After the BLE script exits, this command tests association, DHCP, DNS and an HTTP request using a readable saved NetworkManager PSK profile that matches a visible network. It sends credentials to the diagnostic interpreter in RAM and does not print or save them:

```bash
rtk proxy .venv/bin/python scripts/wifi_probe_host.py
```

## Repeat the Bluetooth Classic probe

This is a separate temporary firmware image. The same verified-backup requirement applies. The build pins [PlatformIO espressif32 6.9.0 and Arduino 2.0.17](https://github.com/platformio/platform-espressif32/releases/tag/v6.9.0). It provides a temporary unauthenticated SPP echo service; stop testing and restore the original afterward.

```bash
rtk proxy uv tool install platformio==6.1.19
rtk proxy platformio run -d diagnostics/classic
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 erase-flash
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 --baud 921600 write-flash 0x1000 diagnostics/classic/.pio/build/esp32dev/bootloader.bin 0x8000 diagnostics/classic/.pio/build/esp32dev/partitions.bin 0xe000 /home/zacmero/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin 0x10000 diagnostics/classic/.pio/build/esp32dev/firmware.bin
rtk proxy .venv/bin/python scripts/serial_probe.py --reset --seconds 8
rtk proxy python scripts/classic_probe_host.py --address 88:57:21:70:81:02
```

Expected startup name is `MERO-ESP32-CLASSIC`. Use system Python for the host script: this machine's system Python includes `socket.AF_BLUETOOTH`, while the uv Python in `.venv` does not. No third-party Python dependency is needed. The host script opens RFCOMM channel 1 and verifies 20 exact echo round trips. This checks a Classic SPP link, not pairing security or audio profiles.

## Restore and verify the original

Restore the original image after the device script exits, even if diagnostics fail:

```bash
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 --baud 921600 --after no-reset write-flash 0 backups/esp32-original-a.bin
rtk proxy .venv/bin/esptool --port /dev/ttyACM1 --baud 921600 --before no-reset read-flash 0 0x400000 backups/esp32-restored-check.bin
rtk proxy cmp backups/esp32-original-a.bin backups/esp32-restored-check.bin
rtk proxy .venv/bin/python scripts/serial_probe.py --reset --seconds 8
```

Keeping the board in download mode between the restore and readback avoids application writes before comparison. A successful full readback comparison establishes that restoration preserved all flash bytes.
