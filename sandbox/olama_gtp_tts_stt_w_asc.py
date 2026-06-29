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
import argparse

import numpy as np
import scipy.signal
import httpx
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container
from textual.widget import Widget
from textual.reactive import reactive

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    filename="lumin.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("lumin")


# -----------------------------
# CONFIG + ARGPARSE
# -----------------------------
def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Lumin — Local Light Bulb Assistant")
    parser.add_argument("-c", "--config", default="config.json", help="Path to config file")
    parser.add_argument("-m", "--model", help="Override model name")
    parser.add_argument("--ollama", help="Override Ollama URL")
    parser.add_argument("--mic", type=int, help="Override microphone device index")
    parser.add_argument("--mode", choices=["tui"], default="tui", help="Run mode (currently only 'tui')")
    return parser.parse_args()


# -----------------------------
# DSP HELPERS (LIGHT NOISE HANDLING)
# -----------------------------
def rms_volume(samples: np.ndarray) -> float:
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))


def highpass_filter(data: np.ndarray, cutoff=100, fs=16000, order=4) -> np.ndarray:
    from scipy.signal import butter, lfilter
    b, a = butter(order, cutoff / (0.5 * fs), btype="high")
    return lfilter(b, a, data)


# -----------------------------
# ASCII LIGHT BULB WIDGET
# -----------------------------
class LuminBulb(Widget):
    mode = reactive("idle")  # idle, listening, thinking, speaking
    mouth_state = reactive(0)
    flicker_state = reactive(0)

    idle = [
        "       .-.       ",
        "     .'   `.     ",
        "    /  ( )  \\    ",
        "    |   ^   |    ",
        "    |  '-'  |    ",
        "    \\       /    ",
        "     `.___.'     ",
        "       | |       ",
        "       | |       ",
        "       |_|       ",
    ]

    listening = [
        "       .-.       ",
        "     .'   `.     ",
        "    /  O O  \\    ",
        "    |   ^   |    ",
        "    |  '-'  |    ",
        "    \\ LIST /     ",
        "     `.___.'     ",
        "       | |       ",
        "       | |       ",
        "       |_|       ",
    ]

    thinking_frames = [
        [
            "       .-.       ",
            "     .'   `.     ",
            "    /  - -  \\    ",
            "    |   ~   |    ",
            "    |  '-'  |    ",
            "    \\ THINK /     ",
            "     `.___.'     ",
            "       | |       ",
            "       | |       ",
            "       |_|       ",
        ],
        [
            "       .-.       ",
            "     .'   `.     ",
            "    /  - -  \\    ",
            "    |   o   |    ",
            "    |  '-'  |    ",
            "    \\ THINK /     ",
            "     `.___.'     ",
            "       | |       ",
            "       | |       ",
            "       |_|       ",
        ],
    ]

    speaking_mouths = [
        "    |  '-'  |    ",
        "    |  ___  |    ",
        "    |  '-'  |    ",
        "    |  ___  |    ",
    ]

    def on_mount(self):
        self.set_interval(0.25, self.animate)

    def animate(self):
        if self.mode == "speaking":
            self.mouth_state = (self.mouth_state + 1) % len(self.speaking_mouths)
            self.refresh()

        if self.mode == "thinking":
            self.flicker_state = (self.flicker_state + 1) % len(self.thinking_frames)
            self.refresh()

    def render(self):
        if self.mode == "idle":
            return "\n".join(self.idle)

        if self.mode == "listening":
            return "\n".join(self.listening)

        if self.mode == "thinking":
            return "\n".join(self.thinking_frames[self.flicker_state])

        if self.mode == "speaking":
            face = self.idle.copy()
            face[4] = self.speaking_mouths[self.mouth_state]
            return "\n".join(face)

        return "\n".join(self.idle)


# -----------------------------
# MAIN APP
# -----------------------------
class OllamaChatApp(App):
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+m", "mic_input", "Speak (push-to-talk)")
    ]

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.model = config["model"]
        self.history = []

        log.debug("Loading Vosk model...")
        self.vosk_model = Model(config["vosk_model_path"])
        log.debug("Vosk model loaded.")

    # -------------------------
    # TTS
    # -------------------------
    def speak(self, text: str):
        def _run():
            try:
                self.bulb.mode = "speaking"
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                log.exception("TTS error: %s", e)
            finally:
                self.bulb.mode = "idle"

        threading.Thread(target=_run, daemon=True).start()

    # -------------------------
    # LISTEN (simplified, stable)
    # -------------------------
    def listen(self, max_duration: float = 15.0) -> str:
        log.debug("Entering listen()")

        mic_index = self.config["mic_device"]
        device_info = sd.query_devices(mic_index, "input")
        native_rate = int(device_info["default_samplerate"])
        TARGET_RATE = 16000

        recognizer = KaldiRecognizer(self.vosk_model, TARGET_RATE)
        recognizer.AcceptWaveform(b"\x00" * 4000)

        audio_queue = queue.Queue()

        # Silence config (fixed threshold)
        silence_threshold = self.config.get("silence_threshold", 1200)
        silence_duration = self.config.get("silence_duration", 0.7)

        def audio_callback(indata, frames, time_, status):
            try:
                if not isinstance(indata, np.ndarray):
                    data = np.frombuffer(indata, dtype=np.int16)
                else:
                    data = indata

                if data.ndim == 2:
                    data = data.mean(axis=1).astype(np.int16)

                # Resample to TARGET_RATE
                data = scipy.signal.resample_poly(data, TARGET_RATE, native_rate).astype(np.int16)

                # Optional light high-pass to remove rumble
                float_data = data.astype(np.float32)
                float_data = highpass_filter(float_data, cutoff=100, fs=TARGET_RATE)
                clean_int16 = np.clip(float_data, -32768, 32767).astype(np.int16)

                audio_queue.put(clean_int16.tobytes())
            except Exception as e:
                log.exception("STT audio callback error: %s", e)

        start_time = time.time()
        last_spoke_time = time.time()
        collected_text = ""

        try:
            stream = sd.InputStream(
                samplerate=native_rate,
                blocksize=4000,
                dtype="int16",
                channels=1,
                device=mic_index,
                callback=audio_callback,
            )
            stream.start()
        except Exception as e:
            log.exception("Failed to open mic: %s", e)
            return ""

        try:
            while True:
                if time.time() - start_time > max_duration:
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

                volume = rms_volume(samples)
                log.debug(f"Volume: {volume:.2f}")

                # Feed recognizer
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        collected_text += " " + text
                        last_spoke_time = time.time()
                        log.debug(f"Recognized: {text}")
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if partial:
                        last_spoke_time = time.time()
                        log.debug(f"Partial: {partial}")

                # Silence detection
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
            self.bulb = LuminBulb()
            yield self.bulb
        yield Footer()

    async def on_mount(self) -> None:
        self.bulb.mode = "idle"

    # -------------------------
    # Push-to-talk
    # -------------------------
    async def action_mic_input(self):
        self.bulb.mode = "listening"
        await asyncio.sleep(0)

        spoken_text = await asyncio.to_thread(self.listen)

        if spoken_text.strip():
            self.history.append({"role": "user", "content": spoken_text})
            self.bulb.mode = "thinking"
            await self.stream_ollama_response(self.history)
        else:
            self.bulb.mode = "idle"

    # -------------------------
    # Streaming Ollama
    # -------------------------
    async def stream_ollama_response(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        ollama_url = self.config["ollama_url"] + "/api/chat"

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", ollama_url, json=payload) as resp:
                    resp.raise_for_status()

                    full_reply = ""

                    async for line in resp.aiter_lines():
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                        except:
                            continue

                        if "message" in data and "content" in data["message"]:
                            full_reply += data["message"]["content"]

                        if data.get("done"):
                            break

                    self.history.append({"role": "assistant", "content": full_reply})
                    self.speak(full_reply)

        finally:
            self.bulb.mode = "idle"


# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    args = parse_args()
    config = load_config(args.config)

    if args.model:
        config["model"] = args.model
    if args.ollama:
        config["ollama_url"] = args.ollama
    if args.mic is not None:
        config["mic_device"] = args.mic

    if args.mode == "tui":
        app = OllamaChatApp(config)
        app.run()
