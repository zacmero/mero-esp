#!/usr/bin/env python3
"""Use readable saved NetworkManager PSKs for this board's Wi-Fi test in RAM."""
import argparse
import subprocess
from pathlib import Path

from run_device import DEFAULT_PORT, run


def nmcli(*args):
    return subprocess.check_output(["nmcli", "--escape", "no", *args], text=True).rstrip("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default=DEFAULT_PORT)
    args = parser.parse_args()
    profiles = []
    for row in nmcli("-t", "-f", "UUID,TYPE", "connection", "show").splitlines():
        uuid, kind = row.split(":", 1)
        if kind != "802-11-wireless":
            continue
        ssid = nmcli("-g", "802-11-wireless.ssid", "connection", "show", uuid)
        key = nmcli("--show-secrets", "-g", "802-11-wireless-security.psk", "connection", "show", uuid)
        if ssid and key:
            profiles.append((ssid, key))
    if not profiles:
        raise SystemExit("No readable saved Wi-Fi PSK profiles available")
    source = Path(__file__).with_name("wifi_probe_device.py").read_text()
    # Credentials travel only over the local USB serial connection and Wi-Fi auth.
    run(("profiles = " + repr(profiles) + "\n" + source).encode(), args.port)
