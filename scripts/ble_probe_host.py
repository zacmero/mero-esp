#!/usr/bin/env python3
"""Connect only to the explicitly supplied ESP32 BLE address and verify echo."""
import argparse
import asyncio
import json

from bleak import BleakClient, BleakScanner

CHARACTERISTIC = "6d65726f-0001-4000-8000-000000000002"


async def probe(address):
    device = await BleakScanner.find_device_by_address(address, timeout=45)
    if device is None:
        raise RuntimeError("ESP32 advertisement not found at " + address)
    notifications = asyncio.Queue()
    async with BleakClient(device, timeout=20) as client:
        initial = bytes(await client.read_gatt_char(CHARACTERISTIC))
        if initial != b"MERO-PROBE-READY":
            raise RuntimeError("Unexpected probe characteristic value: " + repr(initial))
        await client.start_notify(CHARACTERISTIC,
            lambda _, data: notifications.put_nowait(bytes(data)))
        for index in range(20):
            payload = ("mero-probe-%02d" % index).encode()
            await client.write_gatt_char(CHARACTERISTIC, payload, response=True)
            echoed = await asyncio.wait_for(notifications.get(), timeout=5)
            if echoed != payload:
                raise RuntimeError("BLE notification mismatch at sequence %d: sent=%r notified=%r" %
                    (index, payload, echoed))
        await client.stop_notify(CHARACTERISTIC)
        # BlueZ reads can also update Value properties; read outside subscription.
        read_back = bytes(await client.read_gatt_char(CHARACTERISTIC))
        if read_back != payload:
            raise RuntimeError("BLE final read mismatch: " + repr(read_back))
        print(json.dumps({"advertisement": "PASS", "connection": "PASS",
            "gatt_read": "PASS", "gatt_write": "PASS", "notifications": "PASS",
            "round_trips": 20}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", required=True)
    asyncio.run(probe(parser.parse_args().address))
