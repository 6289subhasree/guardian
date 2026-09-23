from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from app.core.config import (
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
)


client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
)


write_api = client.write_api(write_options=SYNCHRONOUS)


def write_telemetry(
    device_id: str,
    temperature: float,
    humidity: float,
) -> None:

    point = (
        Point("telemetry")
        .tag("device_id", device_id)
        .field("temperature", temperature)
        .field("humidity", humidity)
    )

    write_api.write(
        bucket=INFLUXDB_BUCKET,
        org=INFLUXDB_ORG,
        record=point,
    )
def get_telemetry_from_influx(
    device_id: str | None = None,
) -> list[dict]:
    query = (
        f'from(bucket: "{INFLUXDB_BUCKET}") '
        '|> range(start: -24h) '
        '|> filter(fn: (r) => r._measurement == "telemetry")'
    )

    if device_id:
        query += f' |> filter(fn: (r) => r.device_id == "{device_id}")'

    tables = client.query_api().query(query)

    telemetry = []

    for table in tables:
        for record in table.records:
            telemetry.append(
                {
                    "device_id": record.values.get("device_id"),
                    "temperature": (
                        record.values["_value"]
                        if record.values["_field"] == "temperature"
                        else None
                    ),
                    "humidity": (
                        record.values["_value"]
                        if record.values["_field"] == "humidity"
                        else None
                    ),
                    "timestamp": record.get_time(),
                    "field": record.values["_field"],
                }
            )

    return telemetry
