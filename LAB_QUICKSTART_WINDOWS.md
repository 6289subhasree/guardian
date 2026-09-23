# Lab quickstart (Windows 10)

## Prepare at home, without ESP32 boards

1. Install Docker Desktop, Python 3.11+, Node, Arduino IDE with ESP32 board support and PubSubClient, and Npcap for Scapy capture. Arduino IDE must be able to compile `firmware/guardian_esp32/guardian_esp32.ino` before lab. USB-to-serial drivers depend on your board model.
2. In PowerShell from the repository root:

```powershell
Copy-Item deployment/influxdb/.env.example deployment/influxdb/.env
Copy-Item backend/.env.example backend/app/.env
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
cd frontend
npm ci
cd ..
./scripts/preflight.ps1
```

3. Turn on the intended Windows mobile hotspot at home (if available), set its 2.4 GHz band, and choose an SSID and password now. Put those credentials in the sketch. **Do not hardcode real passwords in a public GitHub commit.** Keep your configured local sketch out of Git or revert it before pushing.

## In the lab (three boards, minimal time)

1. Turn on the same hotspot. Run `ipconfig`, find its IPv4 address, and set `SERVER_IP` in the local sketch. Confirm that Wi-Fi clients can contact the laptop. If the hotspot blocks client communication, use the lab Wi-Fi or an approved local access point.
2. Start services and backend in separate PowerShell windows:

```powershell
docker compose -f deployment/mqtt/docker-compose.yml up -d
docker compose -f deployment/influxdb/docker-compose.yml up -d
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Flash the sketch three times, changing only `DEVICE_ID` to `ESP32-001`, `ESP32-002`, `ESP32-003`. Read each device IP in Serial Monitor. Register each real IP using `POST /devices/register` in `http://localhost:8000/docs`. The firmware posts heartbeats and MQTT demo telemetry every five seconds.
4. Start dashboard: `cd frontend; npm run dev`. Use the network interface name from `python -c "from scapy.all import show_interfaces; show_interfaces()"` and capture with `python -m app.network.network_monitor --interface YOUR_INTERFACE --timeout 60` from `backend` in an administrator terminal. Run `POST /detections/run` in API docs. Check `/network/features`, `/graph`, `/detections`.

**Fast fallback:** If Npcap/hotspot packet capture fails, `backend/demo.py` injects synthetic observations into the API and demonstrates graph, inference, and dashboard while the real ESP32 telemetry still runs. This is a mixed hardware/software demo; describe it honestly.

## Time expectation

With dependencies installed and the sketch compiling **before** lab: 30–60 minutes for three boards and basic telemetry, then another 20–40 minutes for packet capture and end-to-end verification. On an unfamiliar network or with driver/firewall trouble, allow 2+ hours. If you have under one hour, prioritize one board transmitting real telemetry and use the synthetic observation fallback. Actual network quarantine and validated botnet detection require separate engineering and evaluation.
