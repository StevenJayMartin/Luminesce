import faulthandler
faulthandler.enable(all_threads=True)

import os
os.environ["VOSK_LOG_LEVEL"] = "-1"

import json
import threading
import queue
import time
import logging
import asyncio

import numpy as np
import scipy.signal
import httpx
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TextArea
from textual.containers import Container, VerticalScroll
from textual.widget import Widget
from textual.reactive import reactive

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("lumin")

# -----------------------------
# CONFIG
# -----------------------------
OLLAMA_API_URL = "http://192.168.5.241:11434/api/chat"
VOSK_MODEL_PATH = r"C:\HOME_Scripts\ollama_ui\vosk-model-en-us-0.22-lgraph"

# Your working microphone device
MIC_DEVICE_INDEX = 1  # MME mic


# -----------------------------
# THINKING SPINNER WIDGET
# -----------------------------
class ThinkingSpinner(Widget):
    spinning = reactive(False)
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    index = 0

    def on_mount(self):
        self.set_interval(0.1, self.update_spinner)

    def update_spinner(self):
        if self.spinning:
            self.index = (self.index + 1) % len(self.frames)
            self.refresh()

    def render(self):
        if not self.spinning:
            return ""
        return f"Lumin is thinking… {self.frames[self.index]}"


# -----------------------------
# MAIN APP
# -----------------------------
class OllamaChatApp(App):
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+m", "mic_input", "Speak (push-to-talk)")
    ]

    def __init__(self, model="llama3.2:latest", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.history = []

        log.debug("Loading Vosk model...")
        self.vosk_model = Model(VOSK_MODEL_PATH)
        log.debug("Vosk model loaded.")

    # -------------------------
    # TTS
    # -------------------------
    def speak(self, text: str):
        def _run():
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                log.exception("TTS error: %s", e)

        threading.Thread(target=_run, daemon=True).start()

    # -------------------------
    # LISTEN WITH RESAMPLING (DEVICE 1, MME)
    # -------------------------
    def listen(self, max_duration: float = 15.0) -> str:
        log.debug("Entering listen()")

        # Detect native sample rate for device 1
        device_info = sd.query_devices(MIC_DEVICE_INDEX, 'input')
        native_rate = int(device_info['default_samplerate'])
        log.debug(f"Native mic sample rate (device {MIC_DEVICE_INDEX}): {native_rate}")

        TARGET_RATE = 16000
        recognizer = KaldiRecognizer(self.vosk_model, TARGET_RATE)

        # Warm-up frame
        recognizer.AcceptWaveform(b"\x00" * 4000)

        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time_, status):
            try:
                if status:
                    log.debug("STT audio status: %s", status)

                # Convert to NumPy array
                if not isinstance(indata, np.ndarray):
                    data = np.frombuffer(indata, dtype=np.int16)
                else:
                    data = indata

                # Force mono
                if data.ndim == 2:
                    data = data.mean(axis=1).astype(np.int16)

                # Resample to 16k
                data = scipy.signal.resample_poly(data, TARGET_RATE, native_rate).astype(np.int16)

                # Ensure contiguous bytes
                audio_queue.put(data.tobytes())

            except Exception as e:
                log.exception("STT audio callback error: %s", e)

        silence_threshold = 100
        silence_duration = 3.0
        last_spoke_time = time.time()
        start_time = time.time()
        collected_text = ""

        try:
            log.debug(f"Opening InputStream at native rate {native_rate} on device {MIC_DEVICE_INDEX}")
            stream = sd.InputStream(
                samplerate=native_rate,
                blocksize=4000,
                dtype="int16",
                channels=1,  # mono for MME device 1
                device=MIC_DEVICE_INDEX,
                callback=audio_callback
            )
            stream.start()
        except Exception as e:
            log.exception("Failed to open mic: %s", e)
            return ""

        try:
            while True:
                if time.time() - start_time > max_duration:
                    log.debug("listen() timed out")
                    return collected_text.strip()

                try:
                    data = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    if time.time() - last_spoke_time > silence_duration:
                        return collected_text.strip()
                    continue

                samples = np.frombuffer(data, dtype=np.int16)
                if samples.size == 0:
                    continue

                volume = int(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
                log.debug(f"Volume: {volume}")

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        collected_text += " " + text
                        last_spoke_time = time.time()
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if partial:
                        last_spoke_time = time.time()

                if volume < silence_threshold:
                    if time.time() - last_spoke_time > silence_duration:
                        return collected_text.strip()

        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    # -------------------------
    # UI
    # -------------------------
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with VerticalScroll():
                self.chat_area = TextArea(read_only=True)
                yield self.chat_area
                self.spinner = ThinkingSpinner()
                yield self.spinner
            self.input_box = Input(
                placeholder="Type or press Ctrl+M to speak..."
            )
            yield self.input_box
        yield Footer()

    async def on_mount(self) -> None:
        self.chat_area.insert(
            "Connected to Ollama on 11434\n"
            "Push-to-talk: press Ctrl+M\n"
        )

    # -------------------------
    # Push-to-talk action
    # -------------------------
    async def action_mic_input(self):
        self.chat_area.insert("🎤 Listening...\n")
        await asyncio.sleep(0)   # <-- UI refresh fix
        self.refresh()

        spoken_text = await asyncio.to_thread(self.listen)

        self.chat_area.insert(f"You (mic): {spoken_text}\n")
        if spoken_text.strip():
            self.history.append({"role": "user", "content": spoken_text})
            await self.stream_ollama_response(self.history)
        else:
            self.chat_area.insert("No speech detected.\n")

    # -------------------------
    # Text input
    # -------------------------
    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_text = message.value.strip()
        if not user_text:
            return

        self.chat_area.insert(f"You: {user_text}\n")
        self.input_box.value = ""
        self.history.append({"role": "user", "content": user_text})

        await self.stream_ollama_response(self.history)

    # -------------------------
    # Streaming Ollama
    # -------------------------
    async def stream_ollama_response(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        self.spinner.spinning = True

        try:
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
                        except:
                            continue

                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            full_reply += chunk
                            self.chat_area.insert(chunk)

                        if data.get("done"):
                            break

                    self.chat_area.insert(f"\n\nAI (full): {full_reply}\n")
                    self.history.append({"role": "assistant", "content": full_reply})
                    self.speak(full_reply)

        finally:
            self.spinner.spinning = False


if __name__ == "__main__":
    OllamaChatApp().run()
