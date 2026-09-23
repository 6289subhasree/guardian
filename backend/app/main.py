import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.devices import router as devices_router
from app.api.telemetry import router as telemetry_router
from app.api.network import router as network_router
from app.api.graph import router as graph_router
from app.core.config import APP_NAME, APP_VERSION
from app.services.device_service import update_device_statuses
from app.mqtt.client import start_mqtt
from app.api.recovery import router as recovery_router
from app.api.detections import router as detections_router
from app.api.responses import router as responses_router
from app.database.init_db import initialize_database
from app.core.config import MQTT_ENABLED, AUTO_DETECTION
from app.database.connection import get_connection
from app.services.detection_pipeline import run_detection
import logging

logger = logging.getLogger(__name__)

async def status_monitor():
    last_id = 0
    while True:
        update_device_statuses()
        if AUTO_DETECTION:
            conn = get_connection()
            try:
                newest = conn.execute("SELECT COALESCE(MAX(id),0) FROM observations").fetchone()[0]
            finally:
                conn.close()
            if newest > last_id:
                try:
                    await asyncio.to_thread(run_detection)
                    last_id = newest
                except Exception:
                    logger.exception("Detection cycle failed; will retry")
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    mqtt_client = start_mqtt() if MQTT_ENABLED else None
    app.state.mqtt_client = mqtt_client

    task = asyncio.create_task(status_monitor())

    yield

    task.cancel()
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-Powered IoT Botnet Detection and Autonomous Response Platform",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(devices_router)
app.include_router(telemetry_router)
app.include_router(graph_router)
app.include_router(network_router)
app.include_router(recovery_router)
app.include_router(detections_router)
app.include_router(responses_router)

@app.get("/")
def root():
    return {
        "project": "GUARDIAN-X",
        "status": "Backend Running",
        "version": APP_VERSION,
    }
