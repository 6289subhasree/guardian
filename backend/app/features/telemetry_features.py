def extract_telemetry_features(
    temperature: float,
    humidity: float,
) -> dict:
    """
    Convert telemetry measurements into numerical features.
    """

    return {
        "temperature": float(temperature),
        "humidity": float(humidity),
    }
