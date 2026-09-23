"""Response decisions with an auditable, opt-in host firewall path."""
from datetime import datetime, timezone

from app.core.config import AUTO_CONFIDENCE, AUTO_MIN_PACKETS, AUTO_FIREWALL, RESPONSE_MODE
from app.database.connection import get_connection
from app.services.device_service import get_device, isolate_device
from app.services.firewall_service import set_mqtt_block


class ResponseResult:
    def __init__(self, device_id: str, action: str, status: str):
        self.device_id = device_id
        self.action = action
        self.status = status


def log_action(device_id: str, action: str, outcome: str, detail: str):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO response_actions (device_id, action, outcome, detail, created_at) VALUES (?,?,?,?,?)",
                     (device_id, action, outcome, detail, datetime.now(timezone.utc).isoformat()))
        conn.commit()
    finally:
        conn.close()


def get_actions(limit: int = 100):
    conn = get_connection()
    try:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM response_actions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
    finally:
        conn.close()


def enforce_device(device_id: str):
    device = get_device(device_id)
    if device is None:
        raise ValueError("Device not registered")
    if device.status == "isolated":
        return ResponseResult(device_id, "ALREADY_ISOLATED", device.status)
    if RESPONSE_MODE != "firewall":
        raise ValueError("Firewall mode is not armed; set RESPONSE_MODE=firewall and restart backend")
    try:
        detail = set_mqtt_block(device.device_id, device.ip_address, True)
    except (RuntimeError, ValueError, OSError) as exc:
        log_action(device_id, "BLOCK_MQTT", "FAILED", str(exc))
        return ResponseResult(device_id, "FIREWALL_FAILED", device.status)
    isolate_device(device_id)
    log_action(device_id, "BLOCK_MQTT", "SUCCESS", detail)
    return ResponseResult(device_id, "BLOCK_MQTT", "isolated")


class ResponseService:
    def respond(self, detection_result, packet_count: int) -> ResponseResult:
        device_id = detection_result.device_id
        if detection_result.status != "SUSPICIOUS":
            return ResponseResult(device_id, "NONE", "NORMAL")
        # A prior suspicious run is required before automatic enforcement.
        conn = get_connection()
        try:
            previous = conn.execute(
                "SELECT classification FROM detections WHERE device_id=? ORDER BY id DESC LIMIT 1",
                (device_id,),
            ).fetchone()
        finally:
            conn.close()
        if (RESPONSE_MODE == "firewall" and AUTO_FIREWALL and detection_result.risk_score >= AUTO_CONFIDENCE
                and packet_count >= AUTO_MIN_PACKETS and previous
                and previous["classification"] == "SUSPICIOUS"):
            return enforce_device(device_id)
        log_action(device_id, "ALERT", "RECORDED",
                   f"Risk {detection_result.risk_score:.3f}; firewall mode={RESPONSE_MODE}")
        return ResponseResult(device_id, "ALERT", "suspicious")


response_service = ResponseService()
