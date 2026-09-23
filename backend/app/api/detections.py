from fastapi import APIRouter, HTTPException, Request
from app.api.responses import require_local

from app.services.detection_pipeline import get_detections, run_detection

router = APIRouter(prefix="/detections", tags=["Detection"])


@router.post("/run")
def detect_now(request: Request):
    require_local(request)
    try:
        return run_detection()
    except FileNotFoundError as exc:
        raise HTTPException(503, "Model checkpoint missing; train the model first") from exc


@router.get("")
def history(limit: int = 100):
    if not 1 <= limit <= 500:
        raise HTTPException(422, "limit must be between 1 and 500")
    return get_detections(limit)
