from app.models.device_graph import DeviceGraph, GraphEdge, GraphNode
from app.services.device_service import get_all_devices
from app.services.network_service import network_observation_service


class DeviceGraphService:
    """Build a device communication graph from network observations."""

    def build_graph(self) -> DeviceGraph:
        """Build the current device communication graph."""

        features = network_observation_service.get_features()
        observations = network_observation_service.get_observations()
        devices = get_all_devices()

        feature_map = {
            feature.device_id: feature
            for feature in features
        }

        nodes = []

        for device in devices:
            feature = feature_map.get(device.device_id)

            if feature is None:
                continue

            nodes.append(
                GraphNode(
                    device_id=device.device_id,
                    features=[
                        float(feature.packet_count),
                        float(feature.total_bytes),
                        feature.average_packet_size,
                        float(feature.tcp_count),
                        float(feature.udp_count),
                        float(feature.connection_count),
                    ],
                )
            )

        device_by_ip = {
            device.ip_address: device.device_id
            for device in devices
        }

        edge_counts: dict[tuple[str, str], int] = {}
        shared_destinations: dict[str, set[str]] = {}

        for observation in observations:
            source_device_id = observation.device_id
            destination_device_id = device_by_ip.get(
                observation.destination_ip
            )

            if source_device_id:
                shared_destinations.setdefault(observation.destination_ip, set()).add(source_device_id)

            if (
                source_device_id is None
                or destination_device_id is None
                or source_device_id == destination_device_id
            ):
                continue

            edge = (source_device_id, destination_device_id)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

        # ESP32 boards often only connect to the laptop broker, not directly
        # to each other. Link boards sharing a destination so their common
        # communication pattern remains visible to the graph model.
        for devices_at_destination in shared_destinations.values():
            ids = sorted(devices_at_destination)
            for index, source_id in enumerate(ids):
                for target_id in ids[index + 1:]:
                    edge = (source_id, target_id)
                    edge_counts[edge] = edge_counts.get(edge, 0) + 1

        edges = [
            GraphEdge(
                source_device_id=source_device_id,
                destination_device_id=destination_device_id,
                connection_count=count,
            )
            for (
                source_device_id,
                destination_device_id,
            ), count in edge_counts.items()
        ]

        return DeviceGraph(
            nodes=nodes,
            edges=edges,
        )


device_graph_service = DeviceGraphService()
