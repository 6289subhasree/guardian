from fastapi import APIRouter
from app.core.config import MQTT_ENABLED, RESPONSE_MODE, AUTO_DETECTION

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "GUARDIAN-X Backend",
        "mqtt_enabled": MQTT_ENABLED,
        "auto_detection": AUTO_DETECTION,
        "response_mode": RESPONSE_MODE,
    }
