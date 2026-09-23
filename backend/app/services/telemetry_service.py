from datetime import datetime
from app.models.telemetry import Telemetry
from app.services.influx_service import write_telemetry


telemetry_store: list[Telemetry] = []


def store_telemetry(
    device_id: str,
    temperature: float,
    humidity: float,
) -> Telemetry:
    telemetry = Telemetry(
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
        timestamp=datetime.now(),
    )

    telemetry_store.append(telemetry)

    write_telemetry(
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
    )

    return telemetry


def get_all_telemetry() -> list[Telemetry]:
    return telemetry_store
