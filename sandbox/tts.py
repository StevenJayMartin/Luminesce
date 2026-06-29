import threading
import queue
import logging
import pyttsx3
import time

log = logging.getLogger("tts")


class Speaker:
    """
    Threaded TTS engine with:
    - Non-blocking speech
    - Internal queue
    - Busy flag (for wake-word logic)
    """

    def __init__(self):
        self.engine = pyttsx3.init()
        self.queue = queue.Queue()
        self.busy = False
        self._stop_flag = False

        # Start worker thread
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

        log.debug("Speaker initialized.")

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------
    def speak(self, text: str):
        """Queue text to be spoken."""
        if not text:
            return
        self.queue.put(text)

    def is_busy(self) -> bool:
        """Returns True if TTS is currently speaking."""
        return self.busy

    def stop(self):
        """Stops the TTS engine and worker thread."""
        self._stop_flag = True
        try:
            self.engine.stop()
        except Exception:
            pass

    # -----------------------------------------------------
    # Worker thread
    # -----------------------------------------------------
    def _run(self):
        while not self._stop_flag:
            try:
                text = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                self.busy = True
                log.debug(f"TTS speaking: {text}")

                self.engine.say(text)
                self.engine.runAndWait()

            except Exception as e:
                log.exception("TTS error: %s", e)

            finally:
                self.busy = False
                time.sleep(0.05)  # small cooldown
