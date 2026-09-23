from dataclasses import dataclass
from datetime import datetime


@dataclass
class Telemetry:
    device_id: str
    temperature: float
    humidity: float
    timestamp: datetime
