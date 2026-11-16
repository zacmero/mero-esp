# Progress

2026-11-16: Initial identification committed and pushed. Continuing with active radio probes and local firmware preservation. First full read running at 460800 baud. Host Bluetooth discovery started; raw nearby device data retained only under ignored backups/.

Both full reads complete and matching. Original UART probes captured. Read-only eFuse summary resolves security state despite unsupported get-security-info. Official MicroPython v1.29.0 downloaded to ignored backups/ and hashed. Temporary firmware installation follows verified backups; restore original full image after radio tests.

First diagnostic run: repeated Wi-Fi scans succeeded. SoftAP configuration before activating the interface raised `OSError: Wifi Invalid Mode`; corrected order to activate before configuring. Retain the failed attempt separately. Original app metadata identifies project esp-at, built May 20 2022, checksum and validation hash valid; app version contains esp32c3 despite confirmed ESP32 silicon, so use esptool chip detection as authoritative chip identity.

The mpremote CLI repeatedly failed entering raw REPL. Explicitly releasing DTR/RTS through its existing SerialTransport solved this; scripts/run_device.py preserves the workaround. BLE connected and wrote successfully, but interleaved reads generated duplicate notification callbacks (previous payload notified, current payload read correctly). Moved read checks outside the notification subscription to isolate notifications. Host NetworkManager contains saved Wi-Fi profiles despite no currently attached Wi-Fi adapter; investigating local credential availability without recording secrets.

Wi-Fi association/DHCP/DNS/HTTP passed; one saved profile matched a visible network. No SSIDs or PSKs written to evidence. BLE clean run passed 20 write/notification round trips and initial/final reads. Added a minimal Bluetooth Classic RFCOMM probe and started its pinned PlatformIO build in isolated uv tool environment.

Classic build passed. Toolchain mirror connection failure was handled by PlatformIO's next mirror. Initial host probe failed because uv Python lacks AF_BLUETOOTH; system Python provides it. Classic discovery and 20 RFCOMM round trips passed, 320 bytes in each direction. Restoring full original image with no-reset afterward, then reading it back before application startup.

Original full-image write verified by esptool. Subsequent full readback before application startup matched byte for byte; original and restored SHA-256 identical. Saved credential scan over all proposed repository files passed. Python compilation and diff whitespace checks passed. User command guide includes identification, security readout, serial queries, both radio diagnostic workflows and recovery.

Restored boot capture confirms the original ESP-IDF/ESP-AT startup banner and WROOM-32/2.4.0 output. All planned bench probes and recovery complete. Publishing source, sanitized evidence and command guide; raw dumps and nearby-device scans remain excluded.
