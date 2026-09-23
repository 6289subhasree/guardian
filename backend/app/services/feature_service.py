from collections import defaultdict

from app.models.network_features import NetworkFeatures
from app.models.network_observation import NetworkObservation


class FeatureExtractionService:
    """Extract numerical ML features from network observations."""

    def extract_features(
        self, observations: list[NetworkObservation]
    ) -> list[NetworkFeatures]:
        """Aggregate network observations by device and calculate features."""

        grouped: dict[str, list[NetworkObservation]] = defaultdict(list)

        for observation in observations:
            if observation.device_id is not None:
                grouped[observation.device_id].append(observation)

        features = []

        for device_id, device_observations in grouped.items():
            packet_count = len(device_observations)

            total_bytes = sum(
                observation.packet_length
                for observation in device_observations
            )

            average_packet_size = (
                total_bytes / packet_count
                if packet_count > 0
                else 0.0
            )

            tcp_count = sum(
                1
                for observation in device_observations
                if observation.protocol == "TCP"
            )

            udp_count = sum(
                1
                for observation in device_observations
                if observation.protocol == "UDP"
            )

            connections = {
                (
                    observation.source_ip,
                    observation.destination_ip,
                    observation.source_port,
                    observation.destination_port,
                )
                for observation in device_observations
            }

            features.append(
                NetworkFeatures(
                    device_id=device_id,
                    packet_count=packet_count,
                    total_bytes=total_bytes,
                    average_packet_size=average_packet_size,
                    tcp_count=tcp_count,
                    udp_count=udp_count,
                    connection_count=len(connections),
                )
            )

        return features


feature_extraction_service = FeatureExtractionService()
