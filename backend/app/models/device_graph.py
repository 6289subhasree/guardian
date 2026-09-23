from dataclasses import dataclass


@dataclass
class GraphNode:
    """A device node with its extracted ML features."""

    device_id: str
    features: list[float]


@dataclass
class GraphEdge:
    """A communication relationship between two registered devices."""

    source_device_id: str
    destination_device_id: str
    connection_count: int


@dataclass
class DeviceGraph:
    """Device communication graph for ML processing."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
