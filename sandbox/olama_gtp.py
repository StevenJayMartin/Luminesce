import json
import httpx
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TextArea
from textual.containers import Container, VerticalScroll

OLLAMA_API_URL = "http://192.168.5.241:11434/api/chat"


class OllamaChatApp(App):
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, model="llama3.2:latest", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.history = []  # Conversation history

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with VerticalScroll():
                self.chat_area = TextArea(read_only=True)
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

        # Display user message
        self.chat_area.insert(f"You: {user_text}\n")
        self.input_box.value = ""

        # Add to conversation history
        self.history.append({"role": "user", "content": user_text})

        # Get AI response
        try:
            await self.stream_ollama_response(self.history)
        except Exception as e:
            self.chat_area.insert(f"Error: {e}\n")

    async def stream_ollama_response(self, messages):
        """
        Streams the assistant's reply from Ollama and appends it to the chat area.
        """
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

                    # Extract streaming content
                    if "message" in data and "content" in data["message"]:
                        chunk = data["message"]["content"]
                        full_reply += chunk
                        self.chat_area.insert(chunk)
                        self.chat_area.refresh()  # NOT awaited

                    if data.get("done"):
                        break

                self.chat_area.insert("\n")
                self.history.append({"role": "assistant", "content": full_reply})


if __name__ == "__main__":
    OllamaChatApp().run()
