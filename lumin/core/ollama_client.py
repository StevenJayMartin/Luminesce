import requests
import json
import logging

log = logging.getLogger("ollama-client")

class OllamaChat:
    def __init__(self, config):
        self.url = config["ollama"].get("url", "http://localhost:11434")
        self.model = config["ollama"].get("model", "llama3.2:latest")
        self.mode = config["ollama"].get("mode", "chat")  # chat or generate

    def stream_chat(self, messages, on_token):
        """
        Chat mode: uses /api/chat
        Supports tool_call JSON.
        """

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

                # normal token
                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]
                    on_token(token)

                # tool call
                if "tool_call" in data:
                    final_json = data

            return final_json

    def stream_generate(self, prompt, on_token):
        """
        Generate mode: uses /api/generate
        Does NOT support tool_call JSON.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        with requests.post(f"{self.url}/api/generate", json=payload, stream=True) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))
                except Exception:
                    continue

                if "response" in data:
                    token = data["response"]
                    on_token(token)

            return None

    def stream(self, messages, on_token):
        """
        Unified entry point used by the TUI.
        Switches between chat and generate.
        """

        if self.mode == "generate":
            # convert messages → prompt
            prompt = "\n".join(m["content"] for m in messages)
            return self.stream_generate(prompt, on_token)

        else:
            return self.stream_chat(messages, on_token)
