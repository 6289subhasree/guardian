# GUARDIAN-X Coding Standards

Version: 1.0

Purpose:

Define coding style, naming conventions, project organization, and development practices followed during GUARDIAN-X implementation.

# 1. General Principles


## Readability First

Code should be written for humans first and machines second.


## Single Responsibility

Each module/class/function should perform one specific task.


Example:

Good:
packet_capture.py


Responsible for:

- Capturing packets


Bad:


everything.py


Responsible for:

- Capture
- ML
- Database
- API
Avoid Duplicate Code

Reusable logic should be converted into functions or modules.

Documentation

Important functions and modules must contain comments/docstrings.


---

# Step 0.9.3 — Python Standards

Add:

```markdown
# 2. Python Coding Standards


## Naming Convention


Variables:

snake_case


Example:

```python
packet_size = 512
device_id = "ESP32_001"

Functions:

snake_case

Example:

extract_features()
capture_packets()

Classes:

PascalCase

Example:

ThreatDetector
GraphBuilder
PacketAnalyzer

Constants:

UPPER_CASE

Example:

MAX_PACKET_SIZE = 1500
DEFAULT_TIMEOUT = 30

---

# Step 0.9.4 — Python Project Structure

Add:

```markdown
# 3. Python File Organization


Example:


module_name/

│
├── main.py

├── config.py

├── models/

├── services/

├── utils/

└── tests/


Purpose:

main.py
- Application entry point


config.py
- Configuration values


models/
- Data structures


services/
- Business logic


utils/
- Helper functions


tests/
- Automated testing
Step 0.9.5 — JavaScript / React Standards

Add:

# 4. React Coding Standards


Components:

PascalCase


Example:


DeviceCard.jsx
ThreatGraph.jsx
Dashboard.jsx



Functions:

camelCase


Example:

```javascript
fetchDevices()
calculateRiskScore()

Constants:

UPPER_CASE

Example:

API_URL
MAX_DEVICES

Folder naming:

lowercase

Example:

components/

pages/

services/

---

# Step 0.9.6 — ESP32 / Embedded Standards

Add:

```markdown
# 5. Embedded C++ Standards


Files:

snake_case


Example:


mqtt_client.cpp
sensor_manager.cpp



Functions:

camelCase


Example:

```cpp
connectMQTT();
sendSensorData();

Constants:

UPPER_CASE

Example:

MQTT_PORT
DEVICE_ID

Rules:

Avoid unnecessary global variables
Comment hardware-specific logic
Keep memory usage optimized

---

# Step 0.9.7 — Git Commit Standards

Add:

```markdown
# 6. Git Commit Standards


Commit format:


type: description


Examples:


Feature:


feat: add mqtt communication module



Bug fix:


fix: correct packet parser logic



Documentation:


docs: update architecture document



Testing:


test: add API integration tests



Refactoring:


refactor: improve feature extraction pipeline

Step 0.9.8 — Branching Strategy

Add:

# 7. Git Branching Strategy


Main branch:

main

Purpose:

Stable production-ready code.


Development branch:

develop

Purpose:

Integration of new features.


Feature branches:


Example:


feature/mqtt-communication
feature/graphsage-model
feature/react-dashboard



Bug fixes:


Example:


fix/api-error

Step 0.9.9 — API Naming Rules

Add:

# 8. API Naming Convention


REST endpoints:


Use lowercase:


Good:


/api/devices
/api/threats
/api/network/graph



Avoid:


/GetDevices
/deviceList



HTTP Methods:


GET:
Retrieve data


POST:
Create data


PUT:
Update data


DELETE:
Remove data
Step 0.9.10 — Database Naming Rules


#9. Database Naming Convention


Tables:

snake_case plural


Examples:


devices

network_traffic

threat_events



Columns:

snake_case


Examples:


device_id

risk_score

created_at
