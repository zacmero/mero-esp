# Findings

- Chip and flash identification passed: ESP32-D0WD-V3 rev 3.1, 4 MB.
- Host has BlueZ controller hci0, powered on, central/peripheral roles. No host Wi-Fi interface is present.
- Original boot output reports WROOM-32 and 2.4.0; application identity is unconfirmed.
- Standard ESP-AT may use a separate UART for commands: https://docs.espressif.com/projects/esp-at/en/latest/esp32/Get_Started/Hardware_connection.html
- Official MicroPython generic ESP32 image supports WROOM with at least 4 MiB and supplies Wi-Fi and BLE: https://micropython.org/download/ESP32_GENERIC/
- `get-security-info` failed on the initial stub and ROM paths. Use read-only eFuse summary to investigate.
- Two 4,194,304-byte reads match: SHA-256 d380d8c94ee05959cab390e909cc9c2c3b85f4a8c9079df1f8f9d2788c7fdaf0.
- Read-only eFuse summary: FLASH_CRYPT_CNT=0, ABS_DONE_0=False, ABS_DONE_1=False, UART_DOWNLOAD_DIS=False. Secure boot and flash encryption disabled at capture.
- UART0 probe of AT, AT+GMR and help produced no command response; startup banner appeared during capture.
- Wi-Fi network test passed using a locally saved profile injected only in RAM: association, DHCP, RSSI -46 dBm, protocol mask 7, DNS resolution and HTTP/1.1 200 OK from example.com.
- BLE passed 20 verified write/notification round trips, initial and final GATT reads, discovery and connection. Device recorded 20 writes and radio shutdown.
- Interleaved GATT reads produced duplicate Value callbacks on the host. Keeping reads outside notification subscription gives a clean notification test.
- MicroPython cannot test Bluetooth Classic. Building a minimal Arduino BluetoothSerial echo probe, pinned PlatformIO espressif32 6.9.0 / Arduino 2.0.17.
- Classic probe built successfully and passed 20 RFCOMM echo round trips (320 bytes in each direction). Host discovered the board as MERO-ESP32-CLASSIC. System Python 3.14.7 has AF_BLUETOOTH; uv Python 3.13.13 does not, so use system Python for the stdlib Classic host probe.
- Original firmware restored. Full readback before boot matched all 4,194,304 bytes and original SHA-256. No diagnostic image remains installed.
