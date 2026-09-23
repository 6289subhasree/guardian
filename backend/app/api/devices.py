from fastapi import APIRouter, HTTPException, Request
from app.api.responses import require_local

from app.schemas.device import (
    DeviceRegistrationRequest,
    DeviceResponse,
)
from app.services.device_service import (
    get_all_devices,
    get_device,
    register_device,
    heartbeat_device,
)

router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post("/register", response_model=DeviceResponse)
def register(
    request: DeviceRegistrationRequest,
    http_request: Request,
):
    require_local(http_request)
    try:
        device = register_device(
            device_id=request.device_id,
            firmware_version=request.firmware_version,
            ip_address=request.ip_address,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    return DeviceResponse(
        device_id=device.device_id,
        firmware_version=device.firmware_version,
        ip_address=device.ip_address,
        status=device.status,
        last_seen=device.last_seen.isoformat(),
    )


@router.get("", response_model=list[DeviceResponse])
def get_devices():
    devices = get_all_devices()

    return [
        DeviceResponse(
            device_id=device.device_id,
            firmware_version=device.firmware_version,
            ip_address=device.ip_address,
            status=device.status,
            last_seen=device.last_seen.isoformat(),
        )
        for device in devices
    ]


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device_by_id(device_id: str):
    device = get_device(device_id)

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


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse)
def heartbeat(device_id: str):
    device = heartbeat_device(device_id)

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
