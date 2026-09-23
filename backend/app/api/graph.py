from fastapi import APIRouter

from app.models.device_graph import DeviceGraph
from app.services.graph_service import device_graph_service

router = APIRouter(
    prefix="/graph",
    tags=["Graph"],
)


@router.get("", response_model=DeviceGraph)
def get_device_graph():
    return device_graph_service.build_graph()
