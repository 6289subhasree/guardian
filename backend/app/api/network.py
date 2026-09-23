from fastapi import APIRouter

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
def add_network_observation(observation: NetworkObservation):
    """Ingest observations from a lab capture process or local demo."""
    network_observation_service.add_observation(observation)
    return observation
