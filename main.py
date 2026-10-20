from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import psutil

import get_status


BASE_DIR=Path(__file__).resolve().parent

app = FastAPI(
    title="Personal API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "API service is running"}

@app.get("/api/status")
def api_status():
    return get_status.api_info() 
@app.get("/api/server/hardware")
def hardware_status():
    return get_status.get_hardware()
@app.get("/api/server/resources")
def resources_status():
    return get_status.get_resources()
@app.get("/api/server/storage")
def storage_status():
    return get_status.get_storage()
@app.get("/api/server/network")
def network_status():
    return get_status.get_network()
@app.get("/api/server/service")
def service_status():
    return get_status.get_service()

@app.get("/dashboard")
def dashboard():
    return FileResponse(BASE_DIR/"dashboard.html")
