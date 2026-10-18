from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import psutil

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
    return{
    }
@app.get("/api/server/hardware")
def hardware_status():
    return{
    }
@app.get("/api/server/resources")
def resources_status():
    return{
    }
@app.get("/api/server/storage")
def storage_status():
    return{
    }
@app.get("api/server/network")
def network_status():
    return{
    }
@app.get("/api/server/service")
def service_status():
    return{
    }

@app.get("/dashboard")
def dashboard():
    return FileResponse(BASE_DIR/"dashboard.html")
