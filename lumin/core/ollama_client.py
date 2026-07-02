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
        self.mode = ollama_cfg.get("mode", "chat")   # "chat" or "generate"

        log.debug(f"OllamaChat initialized: url={self.base_url}, model={self.model}, mode={self.mode}")

    # -----------------------------------------------------
    # STREAM CHAT MODE (TUI)
    # -----------------------------------------------------
    def _stream_chat(self, messages, on_token):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        url = f"{self.base_url}/api/chat"
        log.debug(f"OllamaChat: CHAT mode → {url}, payload={payload}")

        with requests.post(url, json=payload, stream=True) as resp:
            log.debug(f"OllamaChat: CHAT response status={resp.status_code}")
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                log.debug(f"OllamaChat: CHAT raw line='{line}'")

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except Exception as e:
                    log.error(f"OllamaChat: CHAT JSON parse error: {e}, line='{line}'")
                    continue

                # tool-call interrupt
                if "tool_call" in data:
                    log.debug(f"OllamaChat: CHAT TOOL_CALL detected: {data['tool_call']}")
                    return {"tool_call": data["tool_call"]}

                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]
                    log.debug(f"OllamaChat: CHAT token='{token}'")
                    on_token(token)

                if data.get("done"):
                    log.debug("OllamaChat: CHAT done flag received")
                    break

        return None

    # -----------------------------------------------------
    # STREAM GENERATE MODE (WEB UI)
    # -----------------------------------------------------
    def _stream_generate(self, messages, on_token):
        transcript = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            transcript += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
        transcript += "Assistant:"

        payload = {
            "model": self.model,
            "prompt": transcript,
            "stream": True
        }

        url = f"{self.base_url}/api/generate"
        log.debug(f"OllamaChat: GENERATE mode → {url}, payload={payload}")

        with requests.post(url, json=payload, stream=True) as resp:
            log.debug(f"OllamaChat: GENERATE response status={resp.status_code}")
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                log.debug(f"OllamaChat: GENERATE raw line='{line}'")

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except Exception as e:
                    log.error(f"OllamaChat: GENERATE JSON parse error: {e}, line='{line}'")
                    continue

                token = data.get("response", "")
                if token:
                    log.debug(f"OllamaChat: GENERATE token='{token}'")
                    on_token(token)

    # -----------------------------------------------------
    # PUBLIC STREAM METHOD
    # -----------------------------------------------------
    def stream_chat(self, messages, on_token):
        log.debug(f"OllamaChat.stream_chat called, mode={self.mode}, messages={messages}")

        if self.mode == "chat":
            result = self._stream_chat(messages, on_token)
            if isinstance(result, dict) and "tool_call" in result:
                return result
            return None
        else:
            self._stream_generate(messages, on_token)
            return None
