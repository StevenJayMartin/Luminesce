import requests
from fastapi import APIRouter, Depends

router = APIRouter()

# Dependency providers
def get_config(config=Depends(lambda: None)):
    # The lambda is replaced by app dependency injection
    return config

def get_memory_engine(semantic_memory=Depends(lambda: None)):
    return semantic_memory

# ------------------------------------------------------------
# /api/models
# ------------------------------------------------------------
@router.get("/api/models")
def list_models(config: dict = Depends(get_config)):
    try:
        r = requests.get(f"{config['ollama']['url']}/api/tags")
        data = r.json()
        models = [m.get("name") for m in data.get("models", [])]
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}

# ------------------------------------------------------------
# /api/personalities
# ------------------------------------------------------------
@router.get("/api/personalities")
def list_personalities(config: dict = Depends(get_config)):
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})
    current_model = config["ollama"]["model"]
    current_personality = model_map.get(current_model, "default")

    personality_list = [
        {"id": name, "name": name.capitalize()}
        for name in personalities.keys()
    ]

    return {
        "personalities": personality_list,
        "current_model": current_model,
        "current_personality": current_personality,
        "model_personality_map": model_map,
    }

# ------------------------------------------------------------
# /api/model-info
# ------------------------------------------------------------
@router.get("/api/model-info")
def model_info(config: dict = Depends(get_config)):
    info = {
        "model": config["ollama"]["model"],
        "backend": config["ollama"]["url"],
    }

    try:
        r = requests.get(f"{config['ollama']['url']}/api/ps")
        ps = r.json()
        info["running"] = ps.get("models", [])
    except Exception as e:
        info["running_error"] = str(e)

    return info

# ------------------------------------------------------------
# /api/semantic-status
# ------------------------------------------------------------
@router.get("/api/semantic-status")
def semantic_status():
    return {"active": True}

# ------------------------------------------------------------
# /api/memory/{session_id}
# ------------------------------------------------------------
@router.get("/api/memory/{session_id}")
def get_memory(
    session_id: str,
    semantic_memory = Depends(get_memory_engine)
):
    return {"memory": semantic_memory.mem.get(session_id, [])}
