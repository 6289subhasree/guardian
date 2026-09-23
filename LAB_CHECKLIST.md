# Lab validation checklist

1. Put laptop and ESP32 boards on the same approved lab network. Confirm the laptop IP, three device IPs, and whether client-to-client traffic is allowed. A mobile hotspot may block peer communication.
2. Start Mosquitto, InfluxDB, FastAPI, and the frontend as in README. Open `/health` and `/docs` first. Allow inbound TCP 1883 and 8000 on the lab machine if needed.
3. Flash `firmware/guardian_esp32/guardian_esp32.ino` onto each ESP32 with a unique ID, Wi-Fi credentials, and laptop IP. Install Arduino PubSubClient. The sketch sends **fixed demonstration values**, not sensor measurements. Test reception with `mosquitto_sub -h localhost -t guardian/devices/telemetry -v`.
4. Register devices with their *actual* DHCP IPs through `POST /devices/register`, then send regular `POST /devices/{id}/heartbeat` calls from firmware or another client. Verify `/devices` and `/telemetry` independently.
5. Choose the correct capture interface (`ipconfig` on Windows, `ip addr` on Linux; `python -c "from scapy.all import show_interfaces; show_interfaces()"` lists Scapy names). From the backend directory run `python -m app.network.network_monitor --interface YOUR_INTERFACE --timeout 60`. Use Npcap/admin rights on Windows or suitable capture permissions on Linux. Confirm `/network/observations` increases.
6. Confirm `/network/features` attributes packets to registered device IPs and `/graph` contains expected nodes and edges. If traffic is absent, capture on the correct interface or post controlled test observations through the API.
7. Call `POST /detections/run`, inspect `/detections` and the dashboard, and manually verify the database-only isolation state. Do not claim physical quarantine or model accuracy from this test.
8. Record screenshots, timing, observed packets, actual device IDs and IPs, and failures. Do not run simulated hostile traffic on a shared network without lab authorization.
