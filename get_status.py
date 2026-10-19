import os
import time
import platform
import subprocess
import socket
import psutil

from pathlib import Path

START_TIME = psutil.Process(os.getpid()).create_time()

def api_info():
    return {
        "status": "ok",
        "uptime": round(time.time() - START_TIME, 1)
    }

def get_hardware():
    model_path = Path("/proc/device-tree/model")

    model = (
        model_path.read_bytes().decode().strip("\x00")
        if model_path.exists()
        else platform.machine()
    )
    return {
        "name": model,
        "os": platform.freedesktop_os_release().get("PRETTY_NAME", platform.system()),
        "kernel": platform.release(),
        "architechure": platform.machine(),
        "cpu": {
            "model":_get_cpu_model(),
            "cores": psutil.cpu_count(logical=False),
            "threads":psutil.cpu_count(logical=True)
        },
        "ram":{
            "total_gb": round(psutil.virtual_memory().total / 1024**3, 2)
        }
    }
def _get_cpu_model():
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith(("model name", "Hardare")):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()
##########################################################

def get_resources():
    memory = psutil.virtual_memory()
    cpu_temp = None
    try:
        temps=psutil.sensors_temperatures()
        
        for sensor in temps.values():
            if sensor:
                cpu_temp = sensor[0].current
                break
    except(AttributeError, OSError):
        pass

    return {
        "cpu": {
            "using_percent": psutil.cpu_percent(interval=0.1),
            "temperature_c": cpu_temp
        },
        "ram": {
            "using_percent": memory.percent,
            "used_gb": round(memory.used / 1024**3, 2)
        }
    }
#############################################################

PATHS={
    "system":"/",
    "hdd_sftp":"/mnt/HDD-sftp",
    "hdd_dev":"/mnt/HDD-Dev"
}
def get_storage():
    mounts = {
        os.path.realpath(p.mountpoint): p
        for p in psutil.disk_partitions(all=True)
    }

    result = {}

    for name, path in PATHS.items():
        mount = mounts.get(os.path.realpath(path))

        if mount is None:
            result[name]={
                "mounted": False
            }
            continue
        
        try:
            usage = psutil.disk_usage(path)

            result[name]={
                "mounted": True,
                "device": mount.device,
                "filesystem": mount.fstype,
                "total_gb": round(usage.total / 1024**3, 2),
                "used_gb": round(usage.used / 1024**3, 2),
                "usage_percent": usage.percent 
            }
        except OSError:
            result[name]={
                "mounted": True,
                "error": "Unable to read disk usage"
            }

    return result
#########################################################

SERVICES=[
    "ssh",
    "tailscaled"
]

def get_service():
    result={}

    for service in SERVICES:
        try:
            process = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
                timeout=3
            )
            result[service] = process.stdout.strip() or "unknown"
        except (OSError, subprocess.TimeoutExpired):
            result[service]="unknown"

    return result
##########################################################

def get_network():
    stats = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()
    counters = psutil.net_io_counters(pernic=True)

    result = {}

    for name, stat in stats.items():
        ipv4 = [
            addr.address
            for addr in addresses.get(name,[])
            if addr.family == socket.AF_INET
        ]
        traffic = counters.get(name)

        result[name] = {
            "connected": stat.isup,
            "ipv4": ipv4,
            "speed_mbps": stat.speed if stat.speed > 0 else None,
            "received_mb": round(traffic.bytes_recv / 1024**2, 2) if traffic else None,
            "sent_mb": round(traffic.bytes_sent / 1024**2, 2) if traffic else None
        }

    return result
#########################################################
#if __name__=="__main__":
#    import json
#    print(json.dumps(get_network(), indent=4))
