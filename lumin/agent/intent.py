# lumin/agent/intent.py

import json

def extract_intent_from_streamed_json(json_buffer: str):
    """
    Extracts intent JSON from a streamed LLM response.
    """
    try:
        parsed = json.loads(json_buffer)
        if isinstance(parsed, dict) and "intent" in parsed:
            return parsed
    except Exception:
        pass
    return None


def route_intent(intent_json: dict, user_message: str):
    """
    Wraps the existing TUI route_intent logic.
    """
    from lumin.tools.router import route_intent as _route
    return _route(intent_json, user_message)

