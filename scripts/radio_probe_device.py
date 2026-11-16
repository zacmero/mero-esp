"""Run in RAM with mpremote on temporary ESP32 MicroPython firmware."""
import binascii
import bluetooth
import esp
import gc
import json
import machine
import network
import os
import time

print("IDENTITY", os.uname())
print("FLASH_BYTES", esp.flash_size())
print("CPU_HZ", machine.freq())
print("HEAP_FREE", gc.mem_free())
station = network.WLAN(network.WLAN.IF_STA)
station.active(True)
print("WIFI_MAC", binascii.hexlify(station.config("mac")).decode())
for attempt in range(3):
    networks = station.scan()
    print("WIFI_SCAN", json.dumps({
        "attempt": attempt + 1,
        "count": len(networks),
        "channels": sorted(set(row[2] for row in networks)),
        "strongest_rssi_dbm": max(row[3] for row in networks) if networks else None,
    }))
    time.sleep_ms(300)
access_point = network.WLAN(network.WLAN.IF_AP)
access_point.active(True)
access_point.config(ssid="MERO-ESP32-PROBE", security=3, key="mero-probe-local-only")
print("SOFTAP", access_point.active(), access_point.ifconfig())

ble = bluetooth.BLE()
ble.active(True)
scan_results = 0
writes = 0
connections = 0
connection = None
service = bluetooth.UUID("6d65726f-0001-4000-8000-000000000001")
characteristic = bluetooth.UUID("6d65726f-0001-4000-8000-000000000002")
((value_handle,),) = ble.gatts_register_services(((service, ((characteristic,
    bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY),)),))
ble.gatts_set_buffer(value_handle, 64)
ble.gatts_write(value_handle, b"MERO-PROBE-READY")


def irq(event, data):
    global scan_results, writes, connections, connection
    if event == 5:
        scan_results += 1
    elif event == 1:
        connection = data[0]
        connections += 1
        print("BLE_CONNECTED")
    elif event == 2:
        connection = None
        print("BLE_DISCONNECTED")
    elif event == 3 and data[1] == value_handle:
        payload = ble.gatts_read(value_handle)
        writes += 1
        ble.gatts_notify(data[0], value_handle, payload)


ble.irq(irq)
ble.gap_scan(5000, 30000, 30000, True)
time.sleep(6)
print("BLE_SCAN_REPORTS", scan_results)
name = b"MERO-ESP32-PROBE"
advertisement = b"\x02\x01\x06" + bytes((len(name) + 1, 9)) + name
ble.gap_advertise(100000, adv_data=advertisement)
print("BLE_ADDRESS", binascii.hexlify(ble.config("mac")[1]).decode())
print("BLE_READY")
for second in range(90):
    time.sleep(1)
    if writes >= 20 and connection is None:
        break
print("BLE_RESULT", json.dumps({"connections": connections, "writes": writes}))
ble.gap_advertise(None)
ble.active(False)
access_point.active(False)
station.active(False)
print("RADIOS_STOPPED")
