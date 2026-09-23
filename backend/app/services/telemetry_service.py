"""SQLite is the durable source for dashboard telemetry; InfluxDB is optional."""
import logging
from datetime import datetime, timezone

from app.database.connection import get_connection
from app.models.telemetry import Telemetry

logger = logging.getLogger(__name__)


def store_telemetry(device_id: str, temperature: float, humidity: float) -> Telemetry:
    telemetry = Telemetry(device_id=device_id, temperature=temperature,
                          humidity=humidity, timestamp=datetime.now(timezone.utc))
    conn = get_connection()
    try:
        conn.execute("INSERT INTO telemetry (device_id, temperature, humidity, timestamp) VALUES (?,?,?,?)",
                     (device_id, temperature, humidity, telemetry.timestamp.isoformat()))
        conn.commit()
    finally:
        conn.close()
    try:
        from app.services.influx_service import write_telemetry
        write_telemetry(device_id, temperature, humidity)
    except Exception as exc:
        logger.warning("InfluxDB mirror unavailable; SQLite copy retained: %s", exc)
    return telemetry


def get_all_telemetry(limit: int = 100) -> list[Telemetry]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT device_id,temperature,humidity,timestamp FROM telemetry ORDER BY id DESC LIMIT ?",
                            (limit,)).fetchall()
        return [Telemetry(device_id=row['device_id'], temperature=row['temperature'],
                          humidity=row['humidity'], timestamp=datetime.fromisoformat(row['timestamp']))
                for row in rows]
    finally:
        conn.close()
