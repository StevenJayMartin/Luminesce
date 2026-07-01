import queue
import time
import logging
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer

log = logging.getLogger("stt")

# ---------------------------------------------------------
# Pure NumPy resampler (replaces SciPy)
# ---------------------------------------------------------
def np_resample(data, target_len):
    old_len = len(data)
    if old_len == target_len:
        return data

    # Linear interpolation resampling
    return np.interp(
        np.linspace(0, old_len, target_len, endpoint=False),
        np.arange(old_len),
        data
    ).astype(np.int16)


class SpeechRecognizer:
    def __init__(self, config, volume_callback=None):
        self.config = config
        voice_cfg = config["voice"]

        # Voice settings
        self.mic_device = voice_cfg["mic_device"]
        self.silence_threshold = voice_cfg["silence_threshold"]
        self.silence_duration = voice_cfg["silence_duration"]
        self.listen_mode = voice_cfg["listen_mode"]

        # Wake/control words
        self.wake_words = [w.lower() for w in voice_cfg["wake_words"]]
        self.stop_words = [w.lower() for w in voice_cfg["stop_words"]]
        self.clear_words = [w.lower() for w in voice_cfg["clear_words"]]
        self.listen_again_words = [w.lower() for w in voice_cfg["listen_again_words"]]

        # Volume callback
        self.volume_callback = volume_callback

        # Device capabilities
        dev_info = sd.query_devices(self.mic_device)
        self.samplerate = dev_info["default_samplerate"]
        self.channels = dev_info["max_input_channels"]

        # Load Vosk model
        model_path = voice_cfg["vosk_model_path"]
        log.debug(f"Loading Vosk model from: {model_path}")
        self.model = Model(model_path)

        # Vosk recognizer uses 16 kHz
        self.rec_samplerate = 16000
        log.debug("KaldiRecognizer samplerate set to 16000")

        log.debug("SpeechRecognizer initialized.")

    # ---------------------------------------------------------
    # Wake-word detection
    # ---------------------------------------------------------
    def detect_wake_word(self, text: str):
        text = text.lower().strip()
        return any(w in text for w in self.wake_words)

    # ---------------------------------------------------------
    # Control word detection
    # ---------------------------------------------------------
    def _detect_control(self, text: str):
        t = text.lower().strip()

        if any(w in t for w in self.stop_words):
            return "stop"
        if any(w in t for w in self.clear_words):
            return "clear"
        if any(w in t for w in self.listen_again_words):
            return "listen_again"

        return None

    # ---------------------------------------------------------
    # Main STT listen loop
    # ---------------------------------------------------------
    def listen(self, max_duration=None):
        log.debug("Starting STT listen()")

        recognizer = KaldiRecognizer(self.model, self.rec_samplerate)
        audio_q = queue.Queue()

        last_voice_time = time.time()
        start_time = time.time()

        # -----------------------------------------------------
        # Audio callback
        # -----------------------------------------------------
        def callback(indata, frames, time_info, status):
            try:
                if status:
                    log.warning(f"Audio status: {status}")

                # Collapse to mono
                if indata.ndim == 2:
                    mono = indata.mean(axis=1)
                else:
                    mono = indata

                # Convert float32 → int16
                audio = (mono * 32767).astype(np.int16)

                # Volume meter
                max_amp = float(np.abs(audio).max())
                if self.volume_callback:
                    try:
                        level = min(1.0, max_amp / 32768.0)
                        self.volume_callback(level)
                    except Exception as e:
                        log.error(f"Volume callback error: {e}")

                # RESAMPLE to 16 kHz for Vosk
                if self.samplerate != 16000:
                    target_len = int(len(audio) * 16000 / self.samplerate)
                    audio = np_resample(audio, target_len)

                audio_q.put(audio)

            except Exception as e:
                log.error(f"Audio callback error: {e}")

        # -----------------------------------------------------
        # InputStream
        # -----------------------------------------------------
        with sd.InputStream(
            device=self.mic_device,
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            blocksize=0,
            callback=callback,
        ):
            collected_text = ""

            while True:
                try:
                    audio = audio_q.get(timeout=0.1)
                except queue.Empty:
                    audio = None

                if audio is not None:
                    if recognizer.AcceptWaveform(audio.tobytes()):
                        result = recognizer.Result()
                        text = self._extract_text(result)
                        log.debug(f"Final recognized: {text}")
                        if text:
                            collected_text += " " + text
                            last_voice_time = time.time()
                    else:
                        partial = recognizer.PartialResult()
                        ptext = self._extract_partial(partial)
                        log.debug(f"Partial: {ptext}")
                        if ptext:
                            last_voice_time = time.time()

                # Silence detection
                if time.time() - last_voice_time > self.silence_duration:
                    log.debug("Silence detected, ending listen()")
                    break

                # Max duration cutoff
                if max_duration and (time.time() - start_time > max_duration):
                    log.debug("Max duration reached, ending listen()")
                    break

        collected_text = collected_text.strip()
        if not collected_text:
            log.debug("No speech detected.")
            return ("text", "")

        control = self._detect_control(collected_text)
        if control:
            log.debug(f"Control word detected: {control}")
            return (control, collected_text)

        return ("text", collected_text)

    # ---------------------------------------------------------
    # Helpers to extract Vosk JSON text
    # ---------------------------------------------------------
    def _extract_text(self, result_json):
        try:
            import json
            data = json.loads(result_json)
            return data.get("text", "")
        except Exception:
            return ""

    def _extract_partial(self, partial_json):
        try:
            import json
            data = json.loads(partial_json)
            return data.get("partial", "")
        except Exception:
            return ""
