#!/usr/bin/env python3
"""Read UART output or send explicitly supplied text commands; never flash."""
import argparse
import sys
import time

import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AC9040906-if00")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--seconds", type=float, default=3)
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--reset", action="store_true", help="pulse RTS to reboot this board before capture")
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    with serial.Serial(port=None, baudrate=args.baud, timeout=0.1) as uart:
        uart.dtr = False
        uart.rts = False
        uart.port = args.port
        uart.open()
        if args.reset:
            uart.rts = True
            time.sleep(0.1)
            uart.rts = False

        def receive():
            end = time.monotonic() + args.seconds
            while time.monotonic() < end:
                data = uart.read(uart.in_waiting or 1)
                if data:
                    sys.stdout.write(data.decode("utf-8", errors="backslashreplace"))
                    sys.stdout.flush()

        receive()
        for command in args.command:
            print("\n>>> " + repr(command), flush=True)
            uart.write((command + "\r\n").encode())
            uart.flush()
            receive()


if __name__ == "__main__":
    main()
