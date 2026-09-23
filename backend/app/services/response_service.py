from app.ml.detection_service import DetectionResult
from app.services.device_service import isolate_device


class ResponseResult:
    """Result produced by the GUARDIAN-X response service."""

    def __init__(
        self,
        device_id: str,
        action: str,
        status: str,
    ):
        self.device_id = device_id
        self.action = action
        self.status = status

    def __repr__(self):
        return (
            f"ResponseResult("
            f"device_id='{self.device_id}', "
            f"action='{self.action}', "
            f"status='{self.status}'"
            f")"
        )


class ResponseService:
    """Execute an autonomous response based on ML detection."""

    def respond(
        self,
        detection_result: DetectionResult,
    ) -> ResponseResult:
        """Respond to a detection result."""

        if detection_result.status == "SUSPICIOUS":
            device = isolate_device(
                detection_result.device_id
            )

            if device is None:
                return ResponseResult(
                    device_id=detection_result.device_id,
                    action="ISOLATION_FAILED",
                    status="UNKNOWN",
                )

            return ResponseResult(
                device_id=detection_result.device_id,
                action="ISOLATE",
                status=device.status,
            )

        return ResponseResult(
            device_id=detection_result.device_id,
            action="NONE",
            status="NORMAL",
        )


response_service = ResponseService()