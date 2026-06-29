import subprocess
import uuid
import os
import logging
import winsound
import threading

log = logging.getLogger("tts")
log.setLevel(logging.INFO)

class TTS:
    def __init__(self, piper_path: str, model_path: str):
        self.piper_path = piper_path
        self.model_path = model_path

    # ----------------------------------------------------
    # PUBLIC: Non-blocking TTS entry point (async via thread)
    # ----------------------------------------------------
    def speak(self, text: str):
        if not text.strip():
            return

        # Run TTS in a background thread
        threading.Thread(
            target=self._speak_sync,
            args=(text,),
            daemon=True
        ).start()

    # ----------------------------------------------------
    # INTERNAL: Actual synchronous TTS logic
    # ----------------------------------------------------
    def _speak_sync(self, text: str):
        log.debug(f"Piper TTS speaking: {text[:60]}...")

        wav_path = f"tts_{uuid.uuid4()}.wav"

        try:
            # Capture Piper logs to a file instead of polluting UI
            with open("logs/piper_raw.log", "a", encoding="utf-8") as f:
                f.write("\n--- Piper TTS Invocation ---\n")
                subprocess.run(
                    [
                        self.piper_path,
                        "-m", self.model_path,
                        "-f", wav_path
                    ],
                    input=text.encode("utf-8"),
                    check=True,
                    stdout=f,      # capture stdout
                    stderr=f       # capture stderr
                )

            # Play audio natively on Windows
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)

        except Exception as e:
            log.error(f"Piper TTS failed: {e}")

        finally:
            try:
                os.remove(wav_path)
            except Exception:
                pass

    # ----------------------------------------------------
    # Compatibility methods for UI
    # ----------------------------------------------------
    def is_busy(self):
        return False

    def stop(self):
        pass
