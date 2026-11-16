#!/usr/bin/env python3
"""Verify Bluetooth Classic RFCOMM echo on the supplied diagnostic board."""
import argparse
import json
import socket


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", required=True)
    parser.add_argument("--channel", type=int, default=1)
    args = parser.parse_args()
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as client:
        client.settimeout(20)
        client.connect((args.address, args.channel))
        transferred = 0
        for sequence in range(20):
            payload = ("mero-classic-%02d\n" % sequence).encode()
            client.sendall(payload)
            received = b""
            while len(received) < len(payload):
                chunk = client.recv(len(payload) - len(received))
                if not chunk:
                    raise RuntimeError("RFCOMM connection closed before echo completed")
                received += chunk
            if received != payload:
                raise RuntimeError("RFCOMM echo mismatch at " + str(sequence))
            transferred += len(payload)
        print(json.dumps({"classic_rfcomm": "PASS", "round_trips": 20,
                          "bytes_each_direction": transferred}))
