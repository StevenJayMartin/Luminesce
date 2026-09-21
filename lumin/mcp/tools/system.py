import platform
import psutil
import datetime

# ------------------------------------------------------------
# System operations
# ------------------------------------------------------------

def tool_sys_info(params):
    return {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "python": platform.python_version(),
        "timestamp": datetime.datetime.now().isoformat()
    }

def tool_cpu_load(params):
    return {"cpu_percent": psutil.cpu_percent(interval=1)}

def tool_disk_usage(params):
    usage = psutil.disk_usage("/")
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent
    }

# ------------------------------------------------------------
# MCP entrypoint
# ------------------------------------------------------------

def run(params):
    command = params.get("command")

    if command == "info":
        return tool_sys_info(params)

    if command == "cpu":
        return tool_cpu_load(params)

    if command == "disk":
        return tool_disk_usage(params)

    return {"error": f"Unknown system command '{command}'"}

# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

TOOL_META = {
    "tool_sys_info": {
        "description": "Returns OS and system metadata",
        "params": {},
        "returns": "System info dictionary",
        "category": "system",
        "examples": []
    },
    "tool_cpu_load": {
        "description": "Returns CPU load percentage",
        "params": {},
        "returns": "CPU usage percent",
        "category": "system",
        "examples": []
    },
    "tool_disk_usage": {
        "description": "Returns disk usage stats",
        "params": {},
        "returns": "Disk usage dictionary",
        "category": "system",
        "examples": []
    }
}
