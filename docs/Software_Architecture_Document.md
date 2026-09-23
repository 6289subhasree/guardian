# GUARDIAN-X
## Software Architecture Document

Version: 1.0  
Project Type: AI-powered IoT Cybersecurity Platform  
Status: Architecture Finalized# 1. Project Overview

## 1.1 Introduction

GUARDIAN-X is an AI-powered IoT botnet detection and autonomous response platform designed to identify malicious behaviour in IoT networks.

The system monitors IoT device communication, analyzes network behaviour, constructs device interaction graphs, applies Graph Neural Networks for threat detection, and performs automated response actions.

The platform combines:

- IoT hardware
- Network monitoring
- Machine Learning
- Graph Neural Networks
- Cybersecurity automation
- Real-time visualization

# 2. Problem Statement

The rapid growth of IoT devices has increased the attack surface of modern networks.

Traditional security solutions struggle with:

- Unknown botnet behaviour
- Large numbers of connected devices
- Dynamic communication patterns
- Zero-day attacks

GUARDIAN-X aims to detect abnormal IoT communication patterns by learning device behaviour and identifying malicious network relationships.

# 3. System Goals

The primary objectives of GUARDIAN-X are:

1. Monitor IoT device communication in real time.

2. Extract meaningful network behaviour features.

3. Represent IoT communication as a graph structure.

4. Detect botnet behaviour using GraphSAGE-based machine learning.

5. Generate threat intelligence and risk scores.

6. Automatically respond to malicious devices.

7. Provide a security dashboard for monitoring and analysis.

# 4. High-Level Architecture
                    IoT Device Layer

        ESP32 Device 1
              |
        ESP32 Device 2
              |
        ESP32 Device N

              |
              ↓

             MQTT Layer

          Mosquitto Broker

              |
              ↓

       Network Monitoring Layer

              |
          Scapy Packet Capture

              |
              ↓

       Feature Extraction Layer

              |
              ↓

       Graph Construction Layer

              |
              ↓

       AI Detection Engine

          GraphSAGE Model

              |
              ↓

       Threat Intelligence Layer

              |
              ↓

       Response Engine

       Alert / Quarantine

              |
              ↓

          Backend API

            FastAPI

              |
              ↓

       Database Layer

 SQLite + InfluxDB

              |
              ↓

       React Dashboard

     
     
  # 5. Component Description

## 5.1 IoT Device Layer

Technology:
- ESP32

Responsibilities:
- Generate IoT traffic
- Publish MQTT messages
- Simulate normal and malicious behaviour


## 5.2 MQTT Communication Layer

Technology:
- Mosquitto MQTT Broker

Responsibilities:
- Device communication
- Message routing
- IoT network management


## 5.3 Network Monitoring Layer

Technology:
- Python
- Scapy

Responsibilities:
- Capture network packets
- Analyze communication patterns
- Generate raw traffic data


## 5.4 Feature Engineering Layer

Responsibilities:

Convert raw packets into machine learning features:

- Packet size
- Protocol type
- Source device
- Destination device
- Communication frequency
- Time intervals


## 5.5 Graph Construction Layer

Responsibilities:

Convert network communication into graph representation.

Graph:

Nodes:
- IoT devices

Edges:
- Communication relationships


## 5.6 AI Detection Engine

Technology:
- PyTorch
- PyTorch Geometric
- GraphSAGE

Responsibilities:

- Learn device behaviour
- Detect anomalies
- Generate botnet probability score


## 5.7 Response Engine

Responsibilities:

- Generate alerts
- Mark suspicious devices
- Perform quarantine actions


## 5.8 Dashboard

Technology:
- React

Responsibilities:

- Display devices
- Show threats
- Visualize network graphs





                         IoT Network Layer
                              |
        ---------------------------------------------
        |                    |                      |
      ESP32-1             ESP32-2              ESP32-N
        |
        |
        ↓

                 MQTT Communication Layer

                    Mosquitto Broker

                         |
                         ↓

                 Network Monitoring Layer

                  Packet Capture Engine
                       (Scapy)

                         |
                         ↓

                 Feature Extraction Layer

        ------------------------------------
        |                                  |
 Packet Features                  Device Behaviour
        |
        ↓

                 Graph Construction Engine

        Nodes:
        - IoT Devices

        Edges:
        - Communication relationships


                         |
                         ↓


              Graph Neural Network Model

                    GraphSAGE

                         |
                         ↓


                  Threat Intelligence Engine

             Botnet Probability Score
             Anomaly Detection
             Device Risk Ranking


                         |
                         ↓


              Autonomous Response System

        -----------------------------------
        |                                 |
      Alert                         Quarantine
        |
        ↓


                Backend API Layer

                     FastAPI


                         |
                         ↓


                 Database Layer

        -----------------------------------
        |                                 |
     SQLite/PostgreSQL              InfluxDB


                         |
                         ↓


                  Frontend Dashboard

                       React


                         |
                         ↓


              Deployment Infrastructure

                  Docker + Linux