from fastapi import APIRouter

from app.models.telemetry import Telemetry
from app.services.telemetry_service import get_all_telemetry


router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


@router.get("", response_model=list[Telemetry])
def get_telemetry():
    return get_all_telemetry()
