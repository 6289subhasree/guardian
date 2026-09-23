from fastapi import APIRouter, HTTPException

from app.schemas.device import DeviceResponse
from app.services.recovery_service import recover_device


router = APIRouter(
    prefix="/recovery",
    tags=["Recovery"],
)


@router.post("/{device_id}", response_model=DeviceResponse)
def recover(device_id: str):
    try:
        device = recover_device(device_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return DeviceResponse(
        device_id=device.device_id,
        firmware_version=device.firmware_version,
        ip_address=device.ip_address,
        status=device.status,
        last_seen=device.last_seen.isoformat(),
    )
