import json
import requests
import logging

logging.basicConfig(
    filename="logs/lumin.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("client")


class OllamaChat:
    def __init__(self, config):
        ollama_cfg = config["ollama"]

        self.base_url = ollama_cfg["url"]
        self.model = ollama_cfg["model"]

        log.debug(f"OllamaChat initialized: url={self.base_url}, model={self.model}")


    def run(self, messages):
        transcript = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                transcript += f"User: {content}\n"
            else:
                transcript += f"Assistant: {content}\n"

        transcript += "Assistant:"

        payload = {
            "model": self.model,
            "prompt": transcript,
            "stream": False
        }

        log.debug(f"Sending to Ollama /api/generate: {payload}")

        resp = requests.post(f"{self.base_url}/api/generate", json=payload)
        resp.raise_for_status()

        data = resp.json()
        return data.get("response", "")
