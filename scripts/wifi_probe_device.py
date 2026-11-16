"""Run via wifi_probe_host.py; profiles are injected in RAM, never logged."""
import network
import socket
import time

station = network.WLAN(network.WLAN.IF_STA)
station.active(True)
try:
    visible = {row[0] for row in station.scan()}
    candidates = [(ssid, key) for ssid, key in profiles if ssid.encode() in visible]
    print("WIFI_SAVED_PROFILE_MATCHES", len(candidates))
    if not candidates:
        raise RuntimeError("No saved Wi-Fi profile matches a visible SSID")
    for ssid, key in candidates:
        station.connect(ssid, key)
        for _ in range(25):
            if station.isconnected():
                break
            time.sleep(1)
        if station.isconnected():
            break
        station.disconnect()
    if not station.isconnected():
        raise RuntimeError("Saved Wi-Fi profiles did not establish a connection")
    print("WIFI_ASSOCIATION PASS")
    print("WIFI_DHCP", station.ifconfig()[0] != "0.0.0.0")
    print("WIFI_RSSI_DBM", station.status("rssi"))
    print("WIFI_PROTOCOL_MASK", station.config("protocol"))
    address = socket.getaddrinfo("example.com", 80, 0, socket.SOCK_STREAM)[0][-1]
    print("WIFI_DNS PASS")
    client = socket.socket()
    try:
        client.settimeout(15)
        client.connect(address)
        client.sendall(b"GET / HTTP/1.0\r\nHost: example.com\r\nConnection: close\r\n\r\n")
        response = client.recv(128)
        if not response.startswith(b"HTTP/"):
            raise RuntimeError("No HTTP response received over Wi-Fi")
        print("WIFI_TCP_HTTP PASS", response.split(b"\r\n", 1)[0].decode())
    finally:
        client.close()
finally:
    station.disconnect()
    station.active(False)
    print("WIFI_STOPPED")
