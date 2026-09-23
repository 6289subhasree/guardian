from fastapi import APIRouter, HTTPException, Request

from app.models.network_features import NetworkFeatures
from app.models.network_observation import NetworkObservation
from app.services.network_service import network_observation_service


router = APIRouter(
    prefix="/network",
    tags=["Network"],
)


@router.get("/observations", response_model=list[NetworkObservation])
def get_network_observations():
    return network_observation_service.get_observations()


@router.get("/features", response_model=list[NetworkFeatures])
def get_network_features():
    return network_observation_service.get_features()


@router.post("/observations", response_model=NetworkObservation)
def add_network_observation(observation: NetworkObservation, request: Request):
    """Ingest observations from a lab capture process or local demo."""
    if request.client and request.client.host not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(403, "Packet ingestion is local-only")
    try:
        return network_observation_service.add_observation(observation)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
