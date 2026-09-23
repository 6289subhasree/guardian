from app.features.network_features import extract_network_features
from app.features.telemetry_features import extract_telemetry_features


def build_device_features(
    observations: list[dict],
    temperature: float,
    humidity: float,
) -> dict:
    """
    Combine aggregated network and telemetry features
    into a single device-level feature vector.
    """

    network_features = extract_network_features(observations)

    telemetry_features = extract_telemetry_features(
        temperature=temperature,
        humidity=humidity,
    )

    return {
        **network_features,
        **telemetry_features,
    }
