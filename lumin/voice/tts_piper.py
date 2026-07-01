import subprocess
import uuid
import os
import logging
import winsound
import threading
import time

log = logging.getLogger("tts")
log.setLevel(logging.INFO)

class TTS:
    def __init__(self, piper_path: str, model_path: str):
        self.piper_path = piper_path
        self.model_path = model_path

    def speak(self, text: str):
        if not text.strip():
            return

        threading.Thread(
            target=self._speak_sync,
            args=(text,),
            daemon=True
        ).start()

    def _speak_sync(self, text: str):
        log.debug(f"Piper TTS speaking: {text[:60]}...")

        # ⭐ FIX: Write WAV inside the Piper folder
        wav_path = os.path.join(
            os.path.dirname(self.piper_path),
            f"tts_{uuid.uuid4()}.wav"
        )

        try:
            with open("logs/piper_raw.log", "a", encoding="utf-8") as f:
                f.write("\n--- Piper TTS Invocation ---\n")

                subprocess.run(
                    [
                        self.piper_path,
                        "-m", self.model_path,
                        "--stdin",
                        "-f", wav_path
                    ],
                    input=text.encode("utf-8"),
                    check=True,
                    stdout=f,
                    stderr=f,
                    cwd=os.path.dirname(self.piper_path)
                )

            # Wait for WAV to finish writing
            last_size = -1
            while True:
                try:
                    size = os.path.getsize(wav_path)
                    if size == last_size:
                        break
                    last_size = size
                    time.sleep(0.05)
                except FileNotFoundError:
                    time.sleep(0.01)

            # ⭐ Play the WAV from the correct folder
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)

        except Exception as e:
            log.error(f"Piper TTS failed: {e}")

        finally:
            try:
                os.remove(wav_path)
            except Exception:
                pass

    def is_busy(self):
        return False

    def stop(self):
        pass
