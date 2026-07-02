import requests
import json
import logging

log = logging.getLogger("ollama-client")

class OllamaChat:
    def __init__(self, config):
        self.url = config["ollama"].get("url", "http://localhost:11434")
        self.model = config["ollama"].get("model", "llama3.2:latest")
        self.mode = config["ollama"].get("mode", "chat")

    def stream_chat(self, messages, on_token):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        with requests.post(f"{self.url}/api/chat", json=payload, stream=True) as r:
            r.raise_for_status()

            final_json = None

            for line in r.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))
                except Exception:
                    continue

                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]
                    on_token(token)

                if "tool_call" in data:
                    final_json = data

            return final_json
