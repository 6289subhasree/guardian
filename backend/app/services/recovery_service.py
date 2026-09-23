"""Remove our host MQTT rule before clearing an isolated device status."""
from app.core.config import RESPONSE_MODE
from app.database.connection import get_connection
from app.services.device_service import get_device, row_to_device
from app.services.firewall_service import set_mqtt_block
from app.services.response_service import log_action


def recover_device(device_id: str):
    device = get_device(device_id)
    if device is None:
        return None
    if device.status != "isolated":
        raise ValueError("Device is not isolated")
    if RESPONSE_MODE != "firewall":
        raise ValueError("Restart backend with RESPONSE_MODE=firewall to remove its rule")
    try:
        detail = set_mqtt_block(device.device_id, device.ip_address, False)
    except (RuntimeError, ValueError, OSError) as exc:
        log_action(device_id, "UNBLOCK_MQTT", "FAILED", str(exc))
        raise ValueError(f"Firewall removal failed; device remains isolated: {exc}") from exc
    conn = get_connection()
    try:
        conn.execute("UPDATE devices SET status='online' WHERE device_id=?", (device_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM devices WHERE device_id=?", (device_id,)).fetchone()
    finally:
        conn.close()
    log_action(device_id, "UNBLOCK_MQTT", "SUCCESS", detail)
    return row_to_device(row)
