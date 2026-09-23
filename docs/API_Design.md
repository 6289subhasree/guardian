# GUARDIAN-X API Design Document

Version: 1.0

Backend Framework:
FastAPI

Communication:
REST API + JSON

These APIs handle IoT devices.

Register Device
POST /api/devices/register

Purpose:

Register a new ESP32 device.

Request:

{
 "device_id": "ESP32_001",
 "device_name": "Temperature Sensor",
 "ip_address": "192.168.1.10",
 "mac_address": "AA:BB:CC:DD"
}

Response:

{
 "status": "registered",
 "device_id": "ESP32_001"
}
Get All Devices
GET /api/devices

Purpose:

Display all connected IoT devices.

Response:

[
 {
  "device_id":"ESP32_001",
  "status":"active",
  "risk_score":0.05
 }
]
Get Device Details
GET /api/devices/{device_id}

Example:

GET /api/devices/ESP32_001

Returns:

Device information
Traffic history
Threat score
Step 0.6.3 — Network Monitoring APIs
Get Network Traffic
GET /api/traffic

Purpose:

Retrieve captured network information.

Data:

Source device
Destination device
Protocol
Packet size
Timestamp
Get Network Graph
GET /api/network/graph

Purpose:

Send graph data to React visualization.

Example:

{
 "nodes":[
   "ESP32_001",
   "ESP32_002"
 ],

 "edges":[
   {
    "source":"ESP32_001",
    "target":"ESP32_002"
   }
 ]
}
Step 0.6.4 — Threat Detection APIs
Get Threat List
GET /api/threats

Returns:

[
{
 "device":"ESP32_002",
 "risk_score":0.92,
 "status":"malicious"
}
]
Get Device Risk
GET /api/threats/{device_id}

Example:

GET /api/threats/ESP32_002

Returns:

Risk score
Prediction
Attack type
Step 0.6.5 — Response APIs
Quarantine Device
POST /api/device/quarantine

Purpose:

Disconnect malicious device.

Request:

{
 "device_id":"ESP32_002"
}
Generate Alert
POST /api/alerts/create

Purpose:

Create security alert.

Step 0.6.6 — Dashboard APIs

Frontend will consume:

GET /api/dashboard/status

Returns:

{
 "total_devices":10,
 "active_threats":2,
 "network_status":"secure"
}
