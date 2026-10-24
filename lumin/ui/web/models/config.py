import os
import json

# ------------------------------------------------------------
# Resolve directory structure robustly
# ------------------------------------------------------------

# This file lives in: lumin/ui/web/models/config.py
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))          # lumin/ui/web/models
WEB_DIR    = os.path.dirname(MODELS_DIR)                         # lumin/ui/web
UI_DIR     = os.path.dirname(WEB_DIR)                            # lumin/ui
LUMIN_DIR  = os.path.dirname(UI_DIR)                             # lumin

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

CONFIG_PATH = os.path.join(LUMIN_DIR, "config.json")
MEMORY_PATH = os.path.join(LUMIN_DIR, "embed_memory.json")
PROMPTS_DIR = os.path.join(LUMIN_DIR, "prompts")
INDEX_PATH  = os.path.join(WEB_DIR, "index.html")
STATIC_PATH = os.path.join(WEB_DIR, "static")

# ------------------------------------------------------------
# Load config.json
# ------------------------------------------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"config.json not found at: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------------------------------------------------------
# Return all resolved paths
# ------------------------------------------------------------

def get_paths():
    return {
        "config": CONFIG_PATH,
        "memory": MEMORY_PATH,
        "prompts": PROMPTS_DIR,
        "index": INDEX_PATH,
        "static": STATIC_PATH,
    }
