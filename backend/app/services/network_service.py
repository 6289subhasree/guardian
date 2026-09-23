"""Persist bounded packet metadata; never store packet payloads."""
from datetime import datetime, timedelta, timezone

from app.database.connection import get_connection
from app.models.network_observation import NetworkObservation
from app.services.device_service import get_device_by_ip
from app.services.feature_service import feature_extraction_service


class NetworkObservationService:
    def add_observation(self, observation: NetworkObservation) -> NetworkObservation:
        if observation.packet_length < 0 or observation.payload_length < 0:
            raise ValueError("Packet lengths must be nonnegative")
        device = get_device_by_ip(observation.source_ip)
        observation.device_id = device.device_id if device else None
        stamp = observation.timestamp
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        observation.timestamp = stamp.astimezone(timezone.utc)
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO observations
                (timestamp,source_ip,destination_ip,protocol,packet_length,
                 source_port,destination_port,tcp_flags,payload_length,device_id)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (observation.timestamp.isoformat(), observation.source_ip,
                 observation.destination_ip, observation.protocol,
                 observation.packet_length, observation.source_port,
                 observation.destination_port, observation.tcp_flags,
                 observation.payload_length, observation.device_id),
            )
            conn.commit()
        finally:
            conn.close()
        return observation

    def get_observations(self, seconds: int = 300, limit: int = 5000) -> list[NetworkObservation]:
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT timestamp,source_ip,destination_ip,protocol,packet_length,
                   source_port,destination_port,tcp_flags,payload_length,device_id
                   FROM observations WHERE timestamp >= ? ORDER BY id DESC LIMIT ?""",
                (cutoff, limit),
            ).fetchall()
        finally:
            conn.close()
        return [NetworkObservation(timestamp=datetime.fromisoformat(row["timestamp"]),
                                   **{key: row[key] for key in row.keys() if key != "timestamp"})
                for row in reversed(rows)]

    def get_features(self):
        return feature_extraction_service.extract_features(self.get_observations())

    def clear_observations(self):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM observations")
            conn.commit()
        finally:
            conn.close()


network_observation_service = NetworkObservationService()
