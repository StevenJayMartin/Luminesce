import json
import httpx
import pyttsx3
import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TextArea
from textual.containers import Container, VerticalScroll

OLLAMA_API_URL = "http://192.168.1.184:11434/api/chat"


class OllamaChatApp(App):
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, model="llama3.2:latest", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.history = []

    def speak(self, text: str):
        """Speak the AI's response aloud using a fresh engine each time."""
        def _run():
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()

        threading.Thread(target=_run, daemon=True).start()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with VerticalScroll():
                self.chat_area = TextArea()
                yield self.chat_area
            self.input_box = Input(placeholder="Type your message and press Enter...")
            yield self.input_box
        yield Footer()

    async def on_mount(self) -> None:
        self.chat_area.insert("Connected to Ollama server on port 11434\n")

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_text = message.value.strip()
        if not user_text:
            return

        self.chat_area.insert(f"You: {user_text}\n")
        self.input_box.value = ""
        self.history.append({"role": "user", "content": user_text})

        try:
            await self.stream_ollama_response(self.history)
        except Exception as e:
            self.chat_area.insert(f"Error: {e}\n")

    async def stream_ollama_response(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", OLLAMA_API_URL, json=payload) as resp:
                resp.raise_for_status()

                self.chat_area.insert("AI: ")
                full_reply = ""

                async for line in resp.aiter_lines():
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if "message" in data and "content" in data["message"]:
                        chunk = data["message"]["content"]
                        full_reply += chunk
                        self.chat_area.insert(chunk)
                        self.chat_area.refresh()

                    if data.get("done"):
                        break

                self.chat_area.insert("\n")
                self.history.append({"role": "assistant", "content": full_reply})

                # Speak the full reply
                if full_reply.strip():
                    self.speak(full_reply)


if __name__ == "__main__":
    OllamaChatApp().run()
