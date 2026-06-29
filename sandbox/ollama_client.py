import json
import requests

from tools.web_search import web_search


# ---------------------------------------------------------
# TOOL REGISTRY
# ---------------------------------------------------------
TOOLS = {
    "web_search": web_search,
}

# ---------------------------------------------------------
# TOOL SPECS (simple + llama3.2‑friendly)
# ---------------------------------------------------------
TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]


# ---------------------------------------------------------
# OLLAMA CHAT CLIENT (minimal + stable)
# ---------------------------------------------------------
class OllamaChat:
    def __init__(self, config):
        self.base_url = config.get("ollama_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.2:latest")
        self.enable_tools = config.get("enable_tools", True)

    # -----------------------------------------------------
    # STREAM CHAT WITH TOOL SUPPORT
    # -----------------------------------------------------
    def stream_chat(self, messages, on_token):

        # 1) Initial request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        if self.enable_tools:
            payload["tools"] = TOOL_SPECS

        with requests.post(f"{self.base_url}/api/chat", json=payload, stream=True) as resp:
            resp.raise_for_status()

            for raw in resp.iter_lines():
                if not raw:
                    continue

                data = json.loads(raw.decode("utf-8"))

                # ---------------------------------------------------------
                # TOOL CALL DETECTED
                # ---------------------------------------------------------
                if "tool_calls" in data.get("message", {}):
                    tool_call = data["message"]["tool_calls"][0]
                    name = tool_call["function"]["name"]
                    args = tool_call["function"]["arguments"]

                    # UI feedback
                    on_token("\nLumin: 🌐 Searching the web…\n")

                    # Run tool
                    result = TOOLS[name](**args)

                    # Inject tool result
                    messages.append({
                        "role": "tool",
                        "name": name,
                        "content": result,
                    })

                    # -----------------------------------------------------
                    # FOLLOW‑UP REQUEST (VERY IMPORTANT)
                    # -----------------------------------------------------
                    follow_payload = {
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                    }

                    if self.enable_tools:
                        follow_payload["tools"] = TOOL_SPECS

                    with requests.post(f"{self.base_url}/api/chat", json=follow_payload, stream=True) as follow_resp:
                        follow_resp.raise_for_status()

                        for follow_raw in follow_resp.iter_lines():
                            if not follow_raw:
                                continue

                            follow_data = json.loads(follow_raw.decode("utf-8"))
                            token = follow_data.get("message", {}).get("content", "")
                            if token:
                                on_token(token)

                    return  # IMPORTANT: exit after follow‑up

                # ---------------------------------------------------------
                # NORMAL TOKEN STREAMING
                # ---------------------------------------------------------
                token = data.get("message", {}).get("content", "")
                if token:
                    on_token(token)
