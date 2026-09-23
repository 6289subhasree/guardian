"""Connect captured observations to model inference and auditable response."""

from datetime import datetime, timezone

from app.database.connection import get_connection
from app.ml.detection_service import DetectionService
from app.services.device_service import get_all_devices
from app.services.graph_service import device_graph_service
from app.services.network_service import network_observation_service
from app.services.response_service import response_service


def run_detection() -> list[dict]:
    """Score a five-minute observation window and record every decision."""
    model = DetectionService()
    features = {f.device_id: f for f in network_observation_service.get_features()}
    graph = device_graph_service.build_graph()
    edges = [(edge.source_device_id, edge.destination_device_id) for edge in graph.edges]
    scored = {result.device_id: result for result in model.detect_graph(list(features.values()), edges)}
    results = []
    conn = get_connection()
    try:
        for device in get_all_devices():
            if device.device_id not in features:
                continue
            detection = scored[device.device_id]
            response = response_service.respond(detection, features[device.device_id].packet_count)
            result = {
                "device_id": device.device_id,
                "risk_score": detection.risk_score,
                "classification": detection.status,
                "action": response.action,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            conn.execute(
                "INSERT INTO detections (device_id, risk_score, classification, action, created_at) VALUES (?, ?, ?, ?, ?)",
                tuple(result.values()),
            )
            results.append(result)
        conn.commit()
    finally:
        conn.close()
    return results


def get_detections(limit: int = 100) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, device_id, risk_score, classification, action, created_at "
            "FROM detections ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
