# GUARDIAN-X Database Design Document

Version: 1.0

## Database Architecture

GUARDIAN-X uses two types of storage:

1. Relational Database
2. Time-Series Database


Relational Database:
- SQLite (initial development)
- PostgreSQL (production)


Time-Series Database:
- InfluxDB

# 1. Database Selection Reason


## Relational Database

Purpose:

Store structured application information.

Examples:

- IoT devices
- Users
- Threat records
- System configuration


Technology:

SQLite → PostgreSQL


---

## Time-Series Database

Purpose:

Store continuous network monitoring data.

Examples:

- Packet events
- Traffic volume
- Device behaviour over time


Technology:

InfluxDB

# 2. Database Schema


## Device Table


Table Name:

devices


Purpose:

Store registered IoT devices.


Columns:


| Column | Type | Description |
|---|---|---|
| device_id | String | Unique device identifier |
| device_name | String | Device name |
| ip_address | String | Network address |
| mac_address | String | Hardware address |
| device_type | String | IoT device category |
| status | String | Active/Inactive |
| risk_score | Float | Current threat probability |
| created_at | Timestamp | Registration time |

## Traffic Table


Table Name:

network_traffic


Purpose:

Store captured network communication.


Columns:


| Column | Type | Description |
|---|---|---|
| traffic_id | Integer | Unique traffic record |
| source_device | String | Sender device |
| destination_device | String | Receiver device |
| protocol | String | MQTT/TCP/UDP |
| packet_size | Integer | Packet size |
| timestamp | Timestamp | Capture time |

## Feature Table


Table Name:

device_features


Purpose:

Store ML-ready extracted features.


Columns:


| Column | Type | Description |
|---|---|---|
| feature_id | Integer | Unique ID |
| device_id | String | Related device |
| packet_frequency | Float | Packets per time period |
| average_packet_size | Float | Average size |
| communication_count | Integer | Number of connections |
| extraction_time | Timestamp | Feature generation time |

## Threat Table


Table Name:

threat_events


Purpose:

Store AI detection results.


Columns:


| Column | Type | Description |
|---|---|---|
| threat_id | Integer | Unique threat ID |
| device_id | String | Suspected device |
| risk_score | Float | AI confidence score |
| attack_type | String | Botnet category |
| detection_time | Timestamp | Detection time |
| status | String | Open/Resolved |

## Response Table


Table Name:

response_actions


Purpose:

Store automated security actions.


Columns:


| Column | Type | Description |
|---|---|---|
| action_id | Integer | Action ID |
| device_id | String | Target device |
| action_type | String | Alert/Block/Quarantine |
| executed_time | Timestamp | Action time |
| result | String | Success/Failure |

# 3. Database Relationships

devices
   |
   |
   | 1:N
   |
network_traffic


devices
   |
   |
   | 1:N
   |
device_features


devices
   |
   |
   | 1:N
   |
threat_events


devices
   |
   |
   | 1:N
   |
response_actions

