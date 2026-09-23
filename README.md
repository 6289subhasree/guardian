# GUARDIAN-X

An experimental IoT monitoring prototype. It registers ESP32 devices, accepts MQTT telemetry, captures network observations, builds a device communication graph, scores traffic features with a small demonstration model, records detections, and displays device state in a React dashboard.

## Current limits

- The included GraphSAGE checkpoint was trained on eight synthetic examples. Inference passes direct communication and shared-destination edges to GraphSAGE. Shared-destination edges mean devices contacted the same IP; they do **not** mean direct traffic between those devices. The model is **not a validated botnet classifier**.
- `isolated` is a database status, **not a firewall rule**. No traffic is blocked.
- Network observations are kept in backend process memory and disappear on restart. Device registrations and detection history use SQLite; telemetry is written to InfluxDB, while the telemetry endpoint reads process memory.
- Packet capture requires permission to sniff the chosen interface. On a switched or hotspot network it may only see traffic visible to the capture computer.
- The example ESP32 IPs in `backend/demo.py` are illustrative; determine actual lab IPs tomorrow.

## Run locally before the lab

From the repository root, with Python 3.11+ and Node installed:

```sh
cp deployment/influxdb/.env.example deployment/influxdb/.env
cp backend/.env.example backend/app/.env
docker compose -f deployment/mqtt/docker-compose.yml up -d
docker compose -f deployment/influxdb/docker-compose.yml up -d
cd backend
python -m venv .venv
source .venv/bin/activate     # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In separate terminals:

```sh
cd backend && .venv/bin/python demo.py
cd frontend && npm ci && npm run dev
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`. The API docs are at `http://127.0.0.1:8000/docs`; the Vite dashboard is at `http://localhost:5173`.

The demo registers three synthetic devices and posts normal and high-volume traffic observations, then calls `POST /detections/run`. Risk outputs are experimental and should be inspected rather than assumed accurate. Use `POST /recovery/{device_id}` to reset an app-isolated device.

## Lab procedure

See [LAB_CHECKLIST.md](LAB_CHECKLIST.md). Do not use the sample IPs until confirmed on the lab network. An [ESP32 demo sketch](firmware/guardian_esp32/guardian_esp32.ino) publishes fixed example readings and heartbeats; configure each device ID, Wi-Fi, and host address before flashing. The API needs the MQTT broker reachable at localhost:1883; ESP32 devices publish to the host's actual reachable IP on topic `guardian/devices/telemetry` with JSON fields `device_id`, `temperature`, and `humidity`.

## Main API routes

`POST /devices/register`, `POST /devices/{id}/heartbeat`, `GET /devices`, `GET /telemetry`, `POST /network/observations`, `GET /network/features`, `GET /graph`, `POST /detections/run`, `GET /detections`, `POST /recovery/{id}`.

Authors listed in the original repository: Anushka Mukherjee and Subhasree Paul.
