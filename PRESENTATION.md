# How to present GUARDIAN-X

## A clear 4-minute story

1. **Problem (25 seconds):** "IoT devices often send traffic without a central view of who is communicating or whether a device's pattern changed. We want one place to collect traffic evidence, identify unusual devices, and record a reversible response."
2. **Architecture (45 seconds):** Point to three ESP32 boards. "They publish MQTT demo telemetry and HTTP heartbeats. A laptop captures network packet metadata, maps source IPs to registered devices, aggregates a five-minute feature window, and builds a graph of direct or shared-destination relationships. GraphSAGE produces a per-device score. The API records detections and the dashboard shows the trail."
3. **Live demo (100 seconds):** Show device registration and three online statuses. Show a new MQTT reading and packet count rising. Open the graph, then press **Run detection** and show a score and audit entry. Point out whether the input is real captured traffic or `demo.py` synthetic observations. If firewall mode is armed and tested, manually block one registered device's MQTT ingress, show the action log, then recover it. Do not say a firewall rule kills an already established MQTT session instantly.
4. **Engineering choices (45 seconds):** "We persist observations and telemetry in SQLite, keep the packet API local to the laptop, restrict firewall rules to one device IP and TCP/1883, and record failures as well as successful actions. Labeled sessions are split by capture session when retraining so packets from the same run do not leak into evaluation."
5. **Limits and next experiment (25 seconds):** "The bundled model is trained on synthetic samples. Its score is a demonstration of the pipeline, not validated botnet accuracy. We need independently labeled traffic from more devices and environments before enabling automatic blocking in production."

## What to show on screen

- Frontend: graph, current device states, readings, risk scores, response timeline.
- API docs: `/health`, `/network/features`, `/graph`, `/detections`.
- Optional: `captures.jsonl` session labels and `.evaluation.json` if you truly collected labeled sessions and evaluated them.

## Honest answers to likely questions

| Question | Answer |
|---|---|
| Does the model actually detect botnets? | It runs GraphSAGE on device traffic features, but the bundled checkpoint is only a synthetic proof of pipeline. Real detection quality is unproven. |
| What does an edge mean? | Direct communication if both IPs are registered, or a shared destination if both devices contacted the same IP. We do not equate the latter with direct communication. |
| Is isolation real? | In firewall mode on a supported host with admin rights, we add a rule for inbound MQTT TCP/1883 from the registered IP. It is not router-wide isolation. The default mode records alerts only. |
| How are false positives handled? | Automatic firewall response needs two suspicious runs, a high threshold and enough packets; actions are logged and reversible. The thresholds are safeguards, not proof of low false-positive rates. |
| Why three ESP32s? | They demonstrate multiple independent clients and a communication graph. If the lab network does not expose every packet, the API can receive controlled synthetic observations, clearly labeled as such. |

## Contingency if lab time is short

Show one physical ESP32 publishing MQTT and heartbeats, then run `demo.py` for graph/risk/response software. Say which part is hardware and which is synthetic. Do not claim all three boards or physical packet capture worked if they were not verified.
