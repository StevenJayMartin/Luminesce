import json
import requests

REASONING_PROMPT = """
You are a reasoning engine. Respond ONLY with valid JSON.
{
  "thought": "string",
  "intent": "string",
  "plan": ["string"],
  "decision": "none | respond | call_tool"
}
"""

def tolerant_json_extract(raw: str) -> dict | None:
    raw = raw.replace("```json", "").replace("```", "").strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return None
    raw = raw[start:end+1]
    try:
        return json.loads(raw)
    except Exception:
        return None

def sanitize_reasoning(parsed: dict) -> dict:
    decision = parsed.get("decision", "none")
    if decision not in ["none", "respond", "call_tool"]:
        decision = "respond"
    return {
        "thought": parsed.get("thought", ""),
        "intent": parsed.get("intent", "none"),
        "plan": parsed.get("plan", []),
        "decision": decision,
    }

def run_reasoning_module(config: dict, user_message: str) -> dict:
    try:
        payload = {
            "model": config["reasoning"]["model"],
            "prompt": f"{REASONING_PROMPT}\nUser message: {user_message}\nJSON:",
            "stream": False,
        }
        r = requests.post(f"{config['ollama']['url']}/api/generate", json=payload)
        raw = r.json().get("response", "").strip()
        parsed = tolerant_json_extract(raw)
        if parsed:
            return sanitize_reasoning(parsed)
    except Exception:
        pass
    return {
        "thought": f"Fallback reasoning for: {user_message}",
        "intent": "unknown",
        "plan": [],
        "decision": "respond",
    }

