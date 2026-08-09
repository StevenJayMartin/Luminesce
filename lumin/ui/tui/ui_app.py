# lumin/ui/tui/ui_app.py

import asyncio
import threading
import time
import json
import sys
import logging
import os

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Input, Button
from textual.containers import Container, VerticalScroll

from lumin.core.ollama_client import OllamaChat
from lumin.voice.stt import SpeechRecognizer
from lumin.tools.registry import get as get_tool, list_tools
from lumin.tools.router import route_intent
from lumin.tools.prompts import INTENT_SYSTEM_PROMPT, TOOL_PROMPTS, DEFAULT_TOOL_PROMPT
from lumin.mcp.registry import MCP_TOOLS
from lumin.mcp.client import MCPClient

log = logging.getLogger("lumin-ui")


# -----------------------------
# Persistence paths
# -----------------------------
STATE_DIR = "lumin/state"
CHAT_HISTORY_FILE = os.path.join(STATE_DIR, "chat.json")


def render_tool_call_block(tool_name, args_dict):
    args_str = ", ".join(f'{k}="{v}"' for k, v in args_dict.items())
    return f"\n🔧 Tool Call:\n• {tool_name}({args_str})\n\n"


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
        
        # -----------------------------
        # MCP Client Initialization
        # -----------------------------
        mcp_cfg = config.get("mcp", {})
        server_cmd = mcp_cfg.get("server_cmd")
        cwd = mcp_cfg.get("cwd")

        # Force correct type
        if isinstance(server_cmd, str):
            # Try to parse JSON list if it was stringified
            try:
                server_cmd = json.loads(server_cmd)
            except Exception:
                # Fallback: split string
                server_cmd = server_cmd.split()    
        
        if server_cmd:
            from lumin.mcp.client import mcp_client
            self.mcp_client = mcp_client
        else:
            self.mcp_client = None

        self.chat_area = None
        self.input_box = None

        voice_cfg = config.get("voice", {})
        ui_cfg = config.get("ui", {})
        tools_cfg = config.get("tools", {})

        self.listening = False
        self.always_listen = (voice_cfg.get("listen_mode") == "always")
        self.tts_enabled = config.get("tts", {}).get("enabled", True)
        self.stream_to_terminal = ui_cfg.get("stream_to_terminal", True)
        self.tools_enabled = tools_cfg.get("enabled", True)

        self.chat_history = []
        self._stop_flag = False

        os.makedirs(STATE_DIR, exist_ok=True)

    # -----------------------------
    # Persistence helpers
    # -----------------------------
    def _load_chat_history(self):
        try:
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.chat_history = json.load(f)
                log.info("Chat history loaded.")
            else:
                self.chat_history = []
        except Exception as e:
            log.error(f"Failed to load chat history: {e}")
            self.chat_history = []

    def _render_chat_history(self):
        for msg in self.chat_history:
            role = "You" if msg["role"] == "user" else "Lumin"
            self.append_chat(f"{role}: {msg['content']}\n")

    def _save_chat_history(self):
        try:
            with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, indent=2)
            log.info("Chat history saved.")
        except Exception as e:
            log.error(f"Failed to save chat history: {e}")

    # -----------------------------
    # UI / TUI setup
    # -----------------------------
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

        self._load_chat_history()
        self._render_chat_history()

        if self.always_listen:
            threading.Thread(
                target=self._always_listen_loop, daemon=True
            ).start()

        # -----------------------------
        # Start MCP Client
        # -----------------------------
        if self.mcp_client:
            try:
                await self.mcp_client.start()
                self.append_chat("🔌 MCP Connected\n")
            except Exception as e:
                self.append_chat(f"⚠️ MCP Failed to start: {e}\n")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ptt-button":
            self._start_stt()

    def _start_stt(self):
        threading.Thread(
            target=self._run_stt_cycle, daemon=True
        ).start()

    def _volume_callback_safe(self, level: float):
        pass

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_text = message.value.strip()
        if not user_text:
            return

        self.append_chat(f"You: {user_text}\n")
        self.input_box.value = ""
        self.chat_history.append({"role": "user", "content": user_text})
        
        # -----------------------------------------
        # RAW JSON-RPC MCP COMMAND
        # -----------------------------------------
        if user_text.startswith("mcp_rpc "):
            try:
                payload = user_text[len("mcp_rpc "):].strip()
                req = json.loads(payload)

                # IMPORTANT: send_jsonrpc_raw is sync, do NOT await it
                result = self.mcp_client.send_jsonrpc_raw(req)

                self.append_chat(f"🔧 MCP JSON-RPC:\n{json.dumps(result, indent=2)}\n\n")
            except Exception as e:
                self.append_chat(f"Error parsing JSON-RPC: {e}\n")
            return

        if user_text.startswith("ingest "):
            url = user_text.split(" ", 1)[1].strip()
            results = await self._execute_tool("rag_ingest", {"url": url})
            self.append_chat(f"🔧 RAG Ingest:\n{json.dumps(results, indent=2)}\n\n")
            return

        try:
            await self._stream_llm(user_text)
        except Exception as e:
            self.append_chat(f"Error: {e}\n")

    # -----------------------------
    # Tool execution
    # -----------------------------
    async def _execute_tool(self, name, args):

        # ⭐ SPECIAL CASE: MCP tools
        if name == "mcp_tool":
            tool = get_tool(name)
            return tool(args["command"])
  
        if name == "list_tools":
            # Local tools
            local = list_tools()

            # MCP tools
            mcp = [
                {"name": n, "description": meta.get("description", "")}
                for n, meta in MCP_TOOLS.items()
            ]

            # Unified list
            return {"tools": local + mcp}
   
        tool = get_tool(name)
        if not tool:
            return {"error": f"Unknown tool '{name}'"}

        if name == "weather_api" and not args.get("location"):
            return {"error": "Missing 'location' for weather_api"}

        if name == "web_search" and not args.get("query"):
            return {"error": "Missing 'query' for web_search"}

        if name == "wikipedia_search" and not args.get("topic"):
            return {"error": "Missing 'topic' for wikipedia_search"}

        if name == "rag_ingest" and not args.get("url"):
            return {"error": "Missing 'url' for rag_ingest"}

        try:
            # Async tools (rag_query, rag_ingest)
            if asyncio.iscoroutinefunction(tool.__call__):
                return await tool(**args)

            # Sync tools
            return tool(config=self.config, **args)

        except Exception as e:
            return {"error": str(e)}


    def _format_tool_results(self, tool_name, results):

        if tool_name == "weather_api":
            if "error" in results:
                return f"🌦 Weather Error: {results['error']}\n\n"
            return (
                "🌦 Weather Raw Data:\n"
                f"{json.dumps(results, indent=2)}\n\n"
            )

        if tool_name == "wikipedia_search":
            if "error" in results:
                return f"📘 Wikipedia Error: {results['error']}\n\n"
            return (
                "📘 Wikipedia Summary:\n"
                f"• Title: {results.get('title', '')}\n"
                f"• Description: {results.get('description', '')}\n"
                f"• Extract: {results.get('extract', '')}\n"
                f"• URL: {results.get('url', '')}\n\n"
            )

        if tool_name == "web_search":
            if isinstance(results, str):
                return f"🔎 Web Search:\n{results}\n\n"
            return f"🔎 Web Search:\n{results}\n\n"

        if tool_name == "list_tools":
            tools = results.get("tools", [])
            if not tools:
                return "🧰 Available Tools:\n• [no tools registered]\n\n"
            lines = ["🧰 Available Tools:"]
            for t in tools:
                name = t.get("name", "")
                desc = t.get("description", "")
                lines.append(f"• {name} — {desc}")
            return "\n".join(lines) + "\n\n"

        if tool_name == "chat_tool":
            return f"💬 Small Talk:\n{results.get('response', '')}\n\n"

        return f"[Tool '{tool_name}' returned: {results}]\n\n"

    # -----------------------------
    # Continuation prompt
    # -----------------------------
    async def _continue_llm_with_tool_results(self, tool_name, results):
        tool_prompt = TOOL_PROMPTS.get(tool_name, DEFAULT_TOOL_PROMPT)

        messages = [
            {"role": "system", "content": tool_prompt},
            {
                "role": "user",
                "content": (
                    f"Tool '{tool_name}' returned the following data:\n"
                    f"{json.dumps(results, indent=2)}\n\n"
                    "Please answer the user's question using this information."
                ),
            },
        ]

        self.append_chat("Lumin: ")

        response_parts = []

        def on_token(token: str):
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

    # -----------------------------
    # Intent extraction + tool routing
    # -----------------------------
    async def _stream_llm(self, text: str):
        log.debug(f"TUI: _stream_llm called with text='{text}'")

        messages = [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

        response_parts = []
        json_buffer = ""
        json_mode = False
        intent_json = None

        self.append_chat("Lumin: ")

        def on_token(token: str):
            nonlocal json_buffer, json_mode, intent_json

            log.debug(f"TUI: on_token received: '{token}'")
            stripped = token.strip()

            if stripped in ("```", "json"):
                return

            if (
                "edge_all_open_tabs" in token
                or "WebsiteContent_" in token
                or "User's Edge browser tabs metadata" in token
                or "The edge_all_open_tabs metadata provides" in token
            ):
                return

            if stripped.startswith("{") and not json_mode:
                json_mode = True
                json_buffer = stripped

                response_parts.append(token)
                self.append_chat(token)
                return

            if json_mode:
                json_buffer += stripped

                response_parts.append(token)
                self.append_chat(token)

                if stripped.endswith("}"):
                    try:
                        parsed = json.loads(json_buffer)
                        if isinstance(parsed, dict) and "intent" in parsed:
                            intent_json = parsed
                            json_mode = False
                            raise StopIteration
                    except Exception:
                        pass
                return

            response_parts.append(token)
            self.append_chat(token)

            if self.stream_to_terminal:
                sys.__stdout__.write(token)
                sys.__stdout__.flush()

        try:
            await asyncio.to_thread(self.llm.stream, messages, on_token)
        except StopIteration:
            pass
        except Exception as e:
            fallback = f"\n[Sorry, I couldn't process that request: {e}]\n"
            self.append_chat(fallback)
            self.chat_history.append(
                {"role": "assistant", "content": fallback}
            )
            return
        
        user_message = self.chat_history[-1]["content"]

        if self.tools_enabled and intent_json:
            try:
                    
                tool_name, tool_args = route_intent(intent_json, user_message)

                block = render_tool_call_block(tool_name, tool_args)
                self.append_chat(block)

                # -----------------------------
                # MCP TOOL EXECUTION
                # -----------------------------
                if tool_name in MCP_TOOLS:
                    try:
                        tool_results = await self.mcp_client.execute(tool_name, tool_args)
                    except Exception as e:
                        tool_results = {"error": f"MCP execution failed: {e}"}

                    results_block = self._format_tool_results(tool_name, tool_results)
                    self.append_chat(results_block)

                    await self._continue_llm_with_tool_results(tool_name, tool_results)
                    return

                # -----------------------------
                # LOCAL TOOL EXECUTION (existing)
                # -----------------------------
                tool_results = await self._execute_tool(tool_name, tool_args)

                results_block = self._format_tool_results(tool_name, tool_results)
                self.append_chat(results_block)

                await self._continue_llm_with_tool_results(tool_name, tool_results)
                return

            except Exception as e:
                log.error(f"Router failed: {e}")

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

    # -----------------------------
    # Wake-word + STT loop
    # -----------------------------
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

    # -----------------------------
    # Exit handler
    # -----------------------------
    def on_exit(self):
        self._stop_flag = True
        self._save_chat_history()
        self.tts.stop()
        # -----------------------------
        # Stop MCP Client
        # -----------------------------
        if self.mcp_client:
            try:
                self.mcp_client.stop()
            except Exception:
                pass
