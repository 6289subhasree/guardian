from ipaddress import IPv4Address
from pydantic import BaseModel, Field, field_validator


class DeviceRegistrationRequest(BaseModel):
    device_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    firmware_version: str = Field(min_length=1, max_length=64)
    ip_address: str

    @field_validator("ip_address")
    @classmethod
    def valid_ip(cls, value: str) -> str:
        return str(IPv4Address(value))


class DeviceResponse(BaseModel):
    device_id: str
    firmware_version: str
    ip_address: str
    status: str
    last_seen: str
