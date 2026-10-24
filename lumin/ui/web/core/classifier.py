import json
import requests

MEMORY_CLASSIFIER_PROMPT = """
You are a memory classifier.

Classify the user's message into:
- user_profile
- preference
- project
- observation

Respond ONLY with JSON:
{
  "type": "...",
  "key": "short_key_or_null",
  "value": "short_value_or_original_text"
}
"""

def classify_memory(config: dict, text: str) -> dict | None:
    try:
        payload = {
            "model": config["ollama"]["model"],
            "prompt": MEMORY_CLASSIFIER_PROMPT + "\nUser: " + text + "\nJSON:",
            "stream": False,
        }
        r = requests.post(f"{config['ollama']['url']}/api/generate", json=payload)
        raw = r.json().get("response", "").strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return None
        return json.loads(raw[start:end+1])
    except Exception:
        return None

