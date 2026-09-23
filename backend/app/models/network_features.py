from dataclasses import dataclass


@dataclass
class NetworkFeatures:
    """Features extracted from network observations for ML processing."""

    device_id: str
    packet_count: int
    total_bytes: int
    average_packet_size: float
    tcp_count: int
    udp_count: int
    connection_count: int
