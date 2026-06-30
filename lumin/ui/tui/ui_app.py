import threading
import logging
import time
import sys
import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TextArea, Button
from textual.containers import Container, VerticalScroll

from lumin.voice.stt import SpeechRecognizer
from lumin.voice.tts import Speaker
from lumin.core.ollama_client import OllamaChat

log = logging.getLogger("lumin-ui")


class LuminApp(App):
    ENABLE_STDOUT = True
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def action_quit(self):
        self.exit()

    def __init__(self, config, tts):
        super().__init__()
        self.config = config

        self.tts = tts
        self.llm = OllamaChat(config)
        self.stt = SpeechRecognizer(
            config,
            volume_callback=self._volume_callback_safe
        )

        self.chat_area = None
        self.input_box = None

        self.listening = False
        self.always_listen = (config.get("listen_mode") == "always")
        self.tts_enabled = config["tts"].get("enabled", True)
        self.stream_to_terminal = config.get("stream_to_terminal", True)

        self.chat_history = []
        self._stop_flag = False

    def append_chat(self, text: str):
        end = len(self.chat_area.text)
        self.chat_area.cursor_position = end
        self.chat_area.insert(text)
        self.chat_area.scroll_end(animate=False)

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            with VerticalScroll():
                self.chat_area = TextArea()
                self.chat_area.disabled = True
                yield self.chat_area

            yield Button("Push to Talk", id="ptt-button")

            self.input_box = Input(placeholder="Type your message and press Enter...")
            yield self.input_box

        yield Footer()

    async def on_mount(self) -> None:
        self.append_chat("Connected to Lumin\n")

        if self.always_listen:
            threading.Thread(target=self._always_listen_loop, daemon=True).start()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ptt-button":
            self._start_stt()

    def _start_stt(self):
        threading.Thread(target=self._run_stt_cycle, daemon=True).start()

    def _volume_callback_safe(self, level: float):
        pass

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_text = message.value.strip()
        if not user_text:
            return

        self.append_chat(f"You: {user_text}\n")
        self.input_box.value = ""
        self.chat_history.append({"role": "user", "content": user_text})

        try:
            await self._stream_llm(user_text)
        except Exception as e:
            self.append_chat(f"Error: {e}\n")

    async def _stream_llm(self, text: str):
        log.debug(f"TUI: _stream_llm called with text='{text}'")

        messages = [{"role": "user", "content": text}]
        log.debug(f"TUI: messages={messages}")

        response_parts = []

        self.append_chat("Lumin: ")

        def on_token(token: str):
            log.debug(f"TUI: on_token received: '{token}'")
            response_parts.append(token)
            self.append_chat(token)

            if self.stream_to_terminal:
                sys.__stdout__.write(token)
                sys.__stdout__.flush()

        try:
            log.debug("TUI: calling llm.stream_chat via asyncio.to_thread")
            await asyncio.to_thread(self.llm.stream_chat, messages, on_token)
            log.debug("TUI: llm.stream_chat completed")

        except Exception as e:
            log.error(f"TUI: Exception in _stream_llm: {e}")
            fallback = f"\n[Sorry, I couldn't process that request: {e}]\n"
            self.append_chat(fallback)
            self.chat_history.append({"role": "assistant", "content": fallback})
            return

        if not response_parts:
            log.warning("TUI: _stream_llm completed but response_parts is empty")
            fallback = "\n[I'm not sure how to answer that, but I'm still here and listening.]\n"
            self.append_chat(fallback)
            self.chat_history.append({"role": "assistant", "content": fallback})
            return

        full_response = "".join(response_parts).strip()
        self.append_chat("\n")
        self.chat_history.append({"role": "assistant", "content": full_response})

        if self.tts_enabled and full_response:
            threading.Thread(target=self.tts.speak, args=(full_response,), daemon=True).start()

    def _always_listen_loop(self):
        while not self._stop_flag:
            time.sleep(0.1)

            if self.tts.is_busy() or self.listening:
                continue

            text = self._passive_listen_for_wake_word()
            if not text:
                continue

            if self.stt.detect_wake_word(text):
                self.tts.speak("I'm listening.")
                while self.tts.is_busy():
                    time.sleep(0.05)
                threading.Thread(target=self._run_stt_cycle, daemon=True).start()

    def _passive_listen_for_wake_word(self):
        try:
            result_type, text = self.stt.listen(max_duration=1.0)
            if result_type == "ok":
                return text
            return ""
        except Exception:
            return ""

    def _run_stt_cycle(self):
        self.listening = True

        while True:
            result_type, text = self.stt.listen()

            if result_type in ("stop", "clear"):
                self.listening = False
                return

            if result_type == "listen_again":
                continue

            text = text.strip()
            break

        self.listening = False

        if not text:
            return

        self.call_from_thread(lambda: self.append_chat(f"You: {text}\n"))
        self.chat_history.append({"role": "user", "content": text})

        self.call_from_thread(lambda: self.run_worker(self._stream_llm(text)))

    def on_exit(self):
        self._stop_flag = True
        self.tts.stop()
