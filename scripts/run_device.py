#!/usr/bin/env python3
"""Run a MicroPython file in RAM, releasing this board's DTR/RTS reset lines."""
import argparse
import sys
import time
from pathlib import Path

from mpremote.transport_serial import SerialTransport


DEFAULT_PORT = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00"


def run(code, port=DEFAULT_PORT):
    transport = SerialTransport(port)
    try:
        transport.serial.dtr = False
        transport.serial.rts = False
        time.sleep(1)
        transport.enter_raw_repl()

        def output(data):
            sys.stdout.buffer.write(data.replace(b"\x04", b""))
            sys.stdout.buffer.flush()

        _, error = transport.exec_raw(code, timeout=120, data_consumer=output)
        if error:
            sys.stderr.buffer.write(error)
            raise SystemExit(1)
        transport.exit_raw_repl()
    finally:
        transport.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--port", default=DEFAULT_PORT)
    args = parser.parse_args()
    run(args.file.read_bytes(), args.port)
