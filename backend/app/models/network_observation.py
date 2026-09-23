from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NetworkObservation:
    timestamp: datetime
    source_ip: str
    destination_ip: str
    protocol: str
    packet_length: int
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    tcp_flags: Optional[str] = None
    payload_length: int = 0
    device_id: Optional[str] = None
