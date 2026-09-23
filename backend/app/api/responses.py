from fastapi import APIRouter, HTTPException, Request

from app.core.config import RESPONSE_MODE, AUTO_FIREWALL
from app.services.response_service import enforce_device, get_actions

router = APIRouter(prefix="/responses", tags=["Response"])


def require_local(request: Request):
    if request.client and request.client.host not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(403, "Control actions are local-only")


@router.get("")
def actions(limit: int = 100):
    return get_actions(max(1, min(limit, 500)))


@router.get("/mode")
def mode():
    return {"mode": RESPONSE_MODE, "automatic_firewall": AUTO_FIREWALL, "port": 1883,
            "scope": "host MQTT ingress only; existing sessions may persist"}


@router.post("/{device_id}/enforce")
def enforce(device_id: str, request: Request):
    require_local(request)
    try:
        result = enforce_device(device_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if result.action == "FIREWALL_FAILED":
        raise HTTPException(503, "Firewall command failed; see /responses for details")
    return {"device_id": result.device_id, "action": result.action, "status": result.status}
