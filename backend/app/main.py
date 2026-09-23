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
from app.database.init_db import initialize_database

async def status_monitor():
    while True:
        update_device_statuses()
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    mqtt_client = start_mqtt()
    app.state.mqtt_client = mqtt_client

    task = asyncio.create_task(status_monitor())

    yield

    task.cancel()
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
    allow_origins=["http://localhost:5173"],
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

@app.get("/")
def root():
    return {
        "project": "GUARDIAN-X",
        "status": "Backend Running",
        "version": APP_VERSION,
    }
