import json
import requests
import logging

from tools.web_search import web_search

# -----------------------------
# LOGGING SETUP
# -----------------------------
logging.basicConfig(
    filename="logs/lumin.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("client")

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
# OLLAMA CHAT CLIENT (patched + stable)
# ---------------------------------------------------------
class OllamaChat:
    def __init__(self, config):
        ollama_cfg = config["ollama"]
        tools_cfg = config["tools"]

        self.base_url = ollama_cfg["url"]
        self.model = ollama_cfg["model"]

        self.enable_tools = tools_cfg["enabled"]
        self.tools_list = tools_cfg["list"]

        log.debug(f"OllamaChat initialized: url={self.base_url}, model={self.model}")


    # -----------------------------------------------------
    # STREAM CHAT WITH TOOL SUPPORT (patched)
    # -----------------------------------------------------
    def stream_chat(self, messages, on_token):

        # 1) Initial request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        # Only send tool schema if enabled
        if self.enable_tools:
            payload["tools"] = TOOL_SPECS

        with requests.post(f"{self.base_url}/api/chat", json=payload, stream=True) as resp:
            resp.raise_for_status()

            for raw in resp.iter_lines():
                if not raw:
                    continue

                data = json.loads(raw.decode("utf-8"))

                # ---------------------------------------------------------
                # TOOL CALL DETECTED — DO NOT STREAM FIRST RESPONSE
                # ---------------------------------------------------------
                if "tool_calls" in data.get("message", {}):

                    # Tools disabled → ignore tool call entirely
                    if not self.enable_tools:
                        continue

                    tool_call = data["message"]["tool_calls"][0]
                    name = tool_call["function"]["name"]
                    args = tool_call["function"]["arguments"]

                    # Run tool (NO on_token here!)
                    result = TOOLS[name](**args)

                    # Inject tool result
                    messages.append({
                        "role": "tool",
                        "name": name,
                        "content": result,
                    })

                    # -----------------------------------------------------
                    # FOLLOW‑UP REQUEST (THIS is the one we stream)
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
                # NORMAL TOKEN STREAMING (only when no tool call)
                # ---------------------------------------------------------
                token = data.get("message", {}).get("content", "")
                if token:
                    on_token(token)


    # -----------------------------------------------------
    # SIMPLE RUN METHOD (non-streaming wrapper)
    # -----------------------------------------------------
    def run(self, prompt):
        """
        Wraps stream_chat() into a simple synchronous call
        that returns a full string. Safe for Web UI.
        Does NOT affect TUI streaming.
        """
        buffer = []

        def collect(token):
            buffer.append(token)

        messages = [{"role": "user", "content": prompt}]
        self.stream_chat(messages, collect)

        return "".join(buffer)
