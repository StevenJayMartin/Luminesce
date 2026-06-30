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


    def stream_chat(self, messages, on_token=None):
        log.debug(f"OllamaChat.stream_chat called, messages={messages}, on_token={on_token}")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        url = f"{self.base_url}/api/chat"
        log.debug(f"OllamaChat: Streaming to {url} with payload={payload}")

        with requests.post(url, json=payload, stream=True) as resp:
            log.debug(f"OllamaChat: response status={resp.status_code}")
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                log.debug(f"OllamaChat: raw line='{line}'")

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except Exception as e:
                    log.error(f"OllamaChat: JSON parse error: {e}, line='{line}'")
                    continue

                # Chat API format
                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]
                    log.debug(f"OllamaChat: token='{token}'")

                    if on_token:
                        on_token(token)

                if data.get("done"):
                    log.debug("OllamaChat: done flag received")
                    break
