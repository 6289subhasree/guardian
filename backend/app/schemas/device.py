from pydantic import BaseModel


class DeviceRegistrationRequest(BaseModel):
    device_id: str
    firmware_version: str
    ip_address: str


class DeviceResponse(BaseModel):
    device_id: str
    firmware_version: str
    ip_address: str
    status: str
    last_seen: str