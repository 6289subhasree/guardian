# GUARDIAN-X Development Roadmap

Version: 1.0

Project Goal:

Build an AI-powered IoT botnet detection and autonomous response platform using network monitoring, graph learning, and cybersecurity automation.

# Phase 1: Environment Setup


## Objective

Prepare the complete development environment.


## Tasks

- Setup Python environment
- Install required libraries
- Configure VS Code
- Setup Docker
- Setup Git workflow
- Configure ESP32 development environment


## Deliverables

- Working development environment
- Dependency files
- Initial Docker configuration


## Completion Criteria

All developers can run the project environment successfully.

# Phase 2: IoT Device Communication


## Objective

Create IoT devices capable of generating network traffic.


## Tasks

- Program ESP32 devices
- Configure MQTT client
- Send sensor/device data
- Create normal behaviour patterns
- Create simulated attack behaviour


## Deliverables

ESP32 → MQTT Broker communication


## Completion Criteria

ESP32 devices successfully publish and receive MQTT messages.

# Phase 3: MQTT Infrastructure


## Objective

Build reliable IoT communication infrastructure.


## Tasks

- Setup Mosquitto broker
- Configure MQTT topics
- Handle device messages
- Monitor communication


## Deliverables

Working MQTT communication system


## Completion Criteria

Multiple ESP32 devices communicate through MQTT.

# Phase 4: Packet Monitoring System


## Objective

Capture and analyze IoT network traffic.


## Tasks

- Implement packet capture
- Parse packets
- Extract network information
- Store traffic records


## Deliverables

Packet monitoring engine


## Completion Criteria

System captures and records IoT traffic.

# Phase 5: Feature Extraction


## Objective

Convert network traffic into ML-ready data.


## Tasks

Extract:

- Packet size
- Protocol
- Frequency
- Communication pattern
- Timing behaviour


## Deliverables

Feature extraction pipeline


## Completion Criteria

Raw packets are converted into structured features.

# Phase 6: Network Graph Creation


## Objective

Represent IoT communication as graphs.


## Tasks

Create:

Nodes:
- IoT devices

Edges:
- Communication relationships


## Deliverables

Dynamic IoT network graph


## Completion Criteria

Network communication can be represented mathematically as a graph.

# Phase 7: GraphSAGE Threat Detection


## Objective

Detect botnet behaviour using Graph Neural Networks.


## Tasks

- Prepare training data
- Implement GraphSAGE model
- Train model
- Evaluate performance
- Generate risk scores


## Deliverables

AI-based botnet detection model


## Completion Criteria

Model identifies malicious device behaviour.

# Phase 8: Autonomous Response


## Objective

Respond to detected threats.


## Tasks

- Generate alerts
- Maintain threat logs
- Implement quarantine mechanism


## Deliverables

Automated security response system


## Completion Criteria

Detected threats trigger appropriate actions.

# Phase 9: Backend API


## Objective

Create the central application server.


## Tasks

- Build FastAPI backend
- Implement REST APIs
- Connect databases
- Manage application logic


## Deliverables

Functional backend service

# Phase 10: React Dashboard


## Objective

Create visualization interface.


## Tasks

- Device dashboard
- Threat visualization
- Network graph display
- Alert management


## Deliverables

Security monitoring dashboard

# Phase 11: Deployment and Testing


## Objective

Deploy and validate complete system.


## Tasks

- Dockerize services
- Integration testing
- Security testing
- Performance testing
- Documentation


## Deliverables

Complete GUARDIAN-X prototype