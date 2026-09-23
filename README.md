# GUARDIAN-X

An IoT network security research prototype built from [Anushka Mukherjee's guardian-x project](https://github.com/anushka04-bs/guardian-x). The architecture connects ESP32 MQTT telemetry and host packet observation to a device graph, GraphSAGE risk scores, an auditable response service, and a React dashboard. Original contributors listed in the source: Anushka Mukherjee and Subhasree Paul.

![Data flow](https://img.shields.io/badge/ESP32_%E2%86%92_MQTT_%E2%86%92_Packets_%E2%86%92_GraphSAGE_%E2%86%92_Response-Prototype-28b99a)

## Implemented

- Device registration and heartbeats in SQLite; offline detection after 15 seconds without a heartbeat.
- ESP32 Arduino sketch with configurable Wi-Fi/host settings, MQTT demo readings and HTTP heartbeat.
- Scapy packet monitor that posts metadata to the local API. SQLite retains packet observations and telemetry; InfluxDB receives a secondary telemetry copy if available.
- Five-minute feature windows, direct/shared-destination graph edges, GraphSAGE inference, persisted detections, and automatic detection cycles when new observations arrive.
- Recorded alerts by default. An **explicit opt-in** `RESPONSE_MODE=firewall` permits a local manual action that adds a host firewall rule blocking TCP/1883 from one registered device IP. A second opt-in `AUTO_FIREWALL=true` enables automatic blocking after two suspicious detection cycles with sufficient packets and score. Recovery removes the rule. The rule is scoped to this laptop's MQTT port; existing TCP sessions may remain active until they reconnect.
- React dashboard with device graph, risk per device, alerts, action timeline, telemetry readings, registration, manual detection, optional MQTT block and recovery.
- Software integration tests and a session-based training/evaluation script for separately labeled captures.

## What this does not establish

The bundled checkpoint was trained on **80 synthetic three-device graphs**, with 20 separately generated graphs held out for a synthetic-only check. Its score is not calibrated, and it has no measured accuracy on real botnet traffic. Do not claim live botnet detection accuracy without collecting real labeled sessions and reporting independent evaluation. The included ESP32 sketch sends **fixed demo readings**, not physical sensor measurements. Firewall commands and real packet visibility require validation on the actual lab laptop and network. This blocks MQTT ingress on the host, not all possible traffic, and cannot quarantine a device at the router. The supplied Mosquitto broker permits anonymous clients to simplify a closed lab demo; add broker authentication and access controls before using an untrusted network.

## Quick start

Requirements: Python 3.11+, Node, Docker Desktop for Mosquitto and InfluxDB, and Arduino IDE + PubSubClient + ESP32 board package for hardware. On Windows follow [LAB_QUICKSTART_WINDOWS.md](LAB_QUICKSTART_WINDOWS.md). For a software-only run, Docker, MQTT and InfluxDB are optional.

```sh
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
MQTT_ENABLED=false uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then in separate terminals:

```sh
cd backend && .venv/bin/python demo.py   # Windows: .venv\Scripts\python.exe demo.py
cd frontend && npm ci && npm run dev
```

Open `http://localhost:5173` and `http://127.0.0.1:8000/docs`. The demo posts clearly synthetic observations; it does not simulate physical packet capture. The app creates its SQLite tables on startup. For lab MQTT, copy `backend/.env.example` to `backend/app/.env` and start the Docker Compose services as described in the lab guide.

## Detection and response

`POST /network/observations` is local-only. Captures are attributed using the registered source IP; the packet's claimed device ID is ignored. Each recent five-minute window is aggregated to six features per registered device and its direct/shared-destination relationships. The checkpoint runs GraphSAGE and returns a score in `[0,1]`. Shared destination means two devices contacted the same endpoint, **not** that they spoke directly. Every score and response decision is recorded.

By default, a suspicious result records an alert only. `RESPONSE_MODE=firewall` must be set in the backend environment and the backend restarted on a host with firewall administrator permissions. The `POST /responses/{id}/enforce` endpoint is a deliberate manual trigger in firewall mode. Automatic blocking additionally requires `AUTO_FIREWALL=true`, a score of at least `AUTO_CONFIDENCE` (default 0.95), at least `AUTO_MIN_PACKETS` (default 20) in the window, and a previous suspicious detection. **Leave automatic blocking off for the bundled synthetic model.** The recovery endpoint removes the rule before marking the device online. These control endpoints only accept requests from the local machine.

Do not turn on firewall mode while connected to an untrusted or shared network, and validate the selected device IP first. The firmware does not currently act on the database's `isolated` state; it may keep an existing MQTT socket until reconnection.

## Training on captured sessions

Use `python export_capture.py --label normal --session normal-01 --output captures.jsonl` after a controlled benign capture. For a separately controlled suspicious run, use `--label suspicious --suspicious-device ESP32-003 --session test-01`: only that known device is labeled suspicious, while other observed nodes are normal. Record the conditions and source of each label. At least **four all-normal and four suspicious sessions** are required. Do not perform traffic attacks on a shared lab network without authorization.

```sh
cd backend
python -m app.ml.train_dataset captures.jsonl --output app/ml/guardian_model.pt
python -m unittest discover -s tests -v  # install requirements-dev.txt first
```

The trainer splits by session, normalizes using training data only, writes a checkpoint and an adjacent `.evaluation.json` with TP/FP/FN/TN and precision/recall on held-out sessions. With a tiny or artificial dataset those metrics are only about that dataset. Back up the bundled checkpoint before replacing it. Do not commit private lab captures or credentials; `.gitignore` excludes `captures.jsonl` and `.env` files.

The default synthetic checkpoint can be reproduced with `python -m app.ml.training`. Its synthetic holdout report is generated next to the checkpoint; it must not be presented as botnet detection accuracy.

## Lab and presentation

- [Windows lab quickstart](LAB_QUICKSTART_WINDOWS.md)
- [Lab validation checklist](LAB_CHECKLIST.md)
- [Presentation and live demo script](PRESENTATION.md)

The API includes `/health`, `/devices`, `/telemetry`, `/network/observations`, `/network/features`, `/graph`, `/detections`, `/responses`, and `/recovery/{device_id}`. Vite runs on `localhost:5173`; FastAPI on `127.0.0.1:8000`. Hardware devices require the backend to bind to `0.0.0.0` and a laptop firewall rule allowing their heartbeat access to TCP/8000.
