from app.models.network_observation import NetworkObservation
from app.services.device_service import get_device_by_ip
from app.services.feature_service import feature_extraction_service

class NetworkObservationService:
    """Service for collecting and associating network observations."""

    def __init__(self):
        self.observations: list[NetworkObservation] = []

    def associate_device(self, observation: NetworkObservation) -> NetworkObservation:
        """Associate an observation with a registered device using its source IP."""
        device = get_device_by_ip(observation.source_ip)

        if device is not None:
            observation.device_id = device.device_id

        return observation

    def add_observation(self, observation: NetworkObservation) -> None:
        """Associate and store a network observation."""
        self.associate_device(observation)
        self.observations.append(observation)

    def get_observations(self) -> list[NetworkObservation]:
        """Return all stored network observations."""
        return self.observations
    def get_features(self):
        """Extract ML features from the currently stored observations."""
        return feature_extraction_service.extract_features(self.observations)
    def clear_observations(self) -> None:
        """Clear all stored network observations."""
        self.observations.clear()


network_observation_service = NetworkObservationService()
