"""Synthetic traffic demo. Run after starting the backend and its services."""

import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def api(method, path, data=None):
    request = Request(BASE + path,
                      data=json.dumps(data).encode() if data is not None else None,
                      headers={"Content-Type": "application/json"}, method=method)
    with urlopen(request, timeout=10) as response:
        return json.load(response)


for device_id, ip in [("ESP32-001", "192.168.29.9"), ("ESP32-002", "192.168.29.95"), ("ESP32-003", "192.168.29.162")]:
    if not any(device["device_id"] == device_id for device in api("GET", "/devices")):
        api("POST", "/devices/register", {"device_id": device_id, "ip_address": ip, "firmware_version": "demo"})

for ip, count, prefix in [("192.168.29.9", 3, 10000), ("192.168.29.162", 45, 20000)]:
    for index in range(count):
        api("POST", "/network/observations", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": ip, "destination_ip": "192.168.29.95",
            "source_port": prefix + index, "destination_port": 1883,
            "protocol": "TCP", "packet_length": 300, "payload_length": 100,
        })

print("Graph:", api("GET", "/graph"))
print("Detections:", api("POST", "/detections/run"))
print("Device states:", api("GET", "/devices"))
