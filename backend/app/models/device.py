from dataclasses import dataclass
from datetime import datetime
@dataclass
class Device:
    device_id: str
    firmware_version: str
    ip_address: str
    status: str
    last_seen: datetime