import asyncio
import threading
import time
import json
import sys
import logging
import requests

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Input, Button
from textual.containers import Container, VerticalScroll

from lumin.core.ollama_client import OllamaChat
from lumin.voice.stt import SpeechRecognizer

log = logging.getLogger("lumin-ui")

SYSTEM_PROMPT = """
You are Lumin, a local assistant.

- When you need external information, you may call tools.
- When you call a tool, you must emit a JSON object with a top-level "tool_call" key.
- Never wrap JSON in markdown.
- Only output the JSON object when calling a tool.
- After the tool result is returned, integrate it into a natural language answer.
"""

# ---------------------------------------------------------
# Helper: Render collapsed tool-call block
# ---------------------------------------------------------
def render_tool_call_block(tool_name, args_dict):
    args_str = ", ".join(f'{k}="{v}"' for k, v in args_dict.items())
    return f"\n🔧 Tool Call:\n• {tool_name}({args_str})\n\n"


# ---------------------------------------------------------
# Main TUI App
# ---------------------------------------------------------
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
            volume_callback=self._volume_callback_safe,
        )

        self.chat_area = None
        self.input_box = None

        voice_cfg = config.get("voice", {})
        ui_cfg = config.get("ui", {})
        tools_cfg = config.get("tools", {})

        self.listening = False
        self.always_listen = (voice_cfg.get("listen_mode") == "always")
        self.tts_enabled = config.get("tts", {}).get("enabled", True)
        self.stream_to_terminal = ui_cfg.get("stream_to_terminal", True)
        self.tools_enabled = tools_cfg.get("enabled", False)

        self.chat_history = []
        self._stop_flag = False

    # ---------------------------------------------------------
    # UI Helpers
    # ---------------------------------------------------------
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

            self.input_box = Input(
                placeholder="Type your message and press Enter..."
            )
            yield self.input_box

        yield Footer()

    async def on_mount(self) -> None:
        self.append_chat("Connected to Lumin\n")

        if self.always_listen:
            threading.Thread(
                target=self._always_listen_loop, daemon=True
            ).start()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ptt-button":
            self._start_stt()

    def _start_stt(self):
        threading.Thread(
            target=self._run_stt_cycle, daemon=True
        ).start()

    def _volume_callback_safe(self, level: float):
        pass

    # ---------------------------------------------------------
    # Input Submission
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # DuckDuckGo Tool
    # ---------------------------------------------------------
    async def _call_duckduckgo(self, query: str):
        try:
            resp = requests.post(
                "http://localhost:8000/tools/duckduckgo_search",
                json={"query": query},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            log.error(f"TUI: DuckDuckGo call failed: {e}")
            return []

    def _format_duck_results_block(self, results):
        if not results:
            return "🔎 DuckDuckGo Search Results:\n• [no results]\n"

        lines = ["🔎 DuckDuckGo Search Results:"]
        for r in results:
            title = r.get("title", "").strip()
            snippet = r.get("snippet", "").strip()
            lines.append(f"• {title} — {snippet}")
        return "\n".join(lines) + "\n"

    # ---------------------------------------------------------
    # Continuation Step
    # ---------------------------------------------------------
    async def _continue_llm_with_results(self, results):
        block = self._format_duck_results_block(results)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Here are search results:\n{block}\n"
                    "Please answer based on these."
                ),
            },
        ]

        self.append_chat("Lumin: ")

        response_parts = []

        def on_token(token: str):
            # Filter hallucinated metadata
            if (
                "edge_all_open_tabs" in token
                or "WebsiteContent_" in token
                or "User's Edge browser tabs metadata" in token
                or "The edge_all_open_tabs metadata provides" in token
            ):
                log.debug(f"[Filtered Edge Metadata] {token}")
                return

            response_parts.append(token)
            self.append_chat(token)

            if self.stream_to_terminal:
                sys.__stdout__.write(token)
                sys.__stdout__.flush()

        await asyncio.to_thread(self.llm.stream, messages, on_token)

        full_response = "".join(response_parts).strip()
        self.append_chat("\n")
        self.chat_history.append(
            {"role": "assistant", "content": full_response}
        )

        if self.tts_enabled and full_response:
            threading.Thread(
                target=self.tts.speak,
                args=(full_response,),
                daemon=True,
            ).start()

    # ---------------------------------------------------------
    # Main LLM Streaming
    # ---------------------------------------------------------
    async def _stream_llm(self, text: str):
        log.debug(f"TUI: _stream_llm called with text='{text}'")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

        response_parts = []

        self.append_chat("Lumin: ")

        def on_token(token: str):
            log.debug(f"TUI: on_token received: '{token}'")

            # Filter hallucinated metadata
            if (
                "edge_all_open_tabs" in token
                or "WebsiteContent_" in token
                or "User's Edge browser tabs metadata" in token
                or "The edge_all_open_tabs metadata provides" in token
            ):
                log.debug(f"[Filtered Edge Metadata] {token}")
                return

            response_parts.append(token)
            self.append_chat(token)

            if self.stream_to_terminal:
                sys.__stdout__.write(token)
                sys.__stdout__.flush()

        try:
            # OllamaChat.stream returns a final JSON dict when a tool_call occurs,
            # otherwise None. All normal text goes through on_token().
            tc_json = await asyncio.to_thread(
                self.llm.stream, messages, on_token
            )

        except Exception as e:
            log.error(f"TUI: Exception in _stream_llm: {e}")
            fallback = (
                f"\n[Sorry, I couldn't process that request: {e}]\n"
            )
            self.append_chat(fallback)
            self.chat_history.append(
                {"role": "assistant", "content": fallback}
            )
            return

        # ---------------------------------------------------------
        # Handle tool_call JSON (only if tools are enabled)
        # ---------------------------------------------------------
        if self.tools_enabled and tc_json and "tool_call" in tc_json:
            try:
                tool_call = tc_json["tool_call"]
                name = tool_call.get("name", "")
                args = tool_call.get("arguments", {})

                # Show collapsed block
                block = render_tool_call_block(name, args)
                self.append_chat(block)

                # Execute tool
                query = args.get("query", text)
                duck_results = await self._call_duckduckgo(query)

                # Show results
                results_block = self._format_duck_results_block(
                    duck_results
                )
                self.append_chat(results_block)

                # Continue LLM
                await self._continue_llm_with_results(duck_results)
                return

            except Exception as e:
                log.error(f"Failed to handle tool_call JSON: {e}")

        # ---------------------------------------------------------
        # Normal assistant response
        # ---------------------------------------------------------
        if not response_parts:
            fallback = (
                "\n[I'm not sure how to answer that, but I'm still here "
                "and listening.]\n"
            )
            self.append_chat(fallback)
            self.chat_history.append(
                {"role": "assistant", "content": fallback}
            )
            return

        full_response = "".join(response_parts).strip()
        self.append_chat("\n")
        self.chat_history.append(
            {"role": "assistant", "content": full_response}
        )

        if self.tts_enabled and full_response:
            threading.Thread(
                target=self.tts.speak,
                args=(full_response,),
                daemon=True,
            ).start()

    # ---------------------------------------------------------
    # Wake Word Loop
    # ---------------------------------------------------------
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
                threading.Thread(
                    target=self._run_stt_cycle, daemon=True
                ).start()

    def _passive_listen_for_wake_word(self):
        try:
            result_type, text = self.stt.listen(max_duration=1.0)
            if result_type == "ok":
                return text
            return ""
        except Exception:
            return ""

    # ---------------------------------------------------------
    # STT Cycle
    # ---------------------------------------------------------
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

        self.call_from_thread(
            lambda: self.append_chat(f"You: {text}\n")
        )
        self.chat_history.append({"role": "user", "content": text})

        self.call_from_thread(
            lambda: self.run_worker(self._stream_llm(text))
        )

    # ---------------------------------------------------------
    # Exit
    # ---------------------------------------------------------
    def on_exit(self):
        self._stop_flag = True
        self.tts.stop()
