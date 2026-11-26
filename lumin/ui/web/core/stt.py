import json
import wave
import tempfile
import subprocess

from vosk import Model, KaldiRecognizer


class SpeechToText:

    def __init__(
        self,
        model_path="models/vosk-model-small-en-us-0.15"
    ):
        print("Loading Vosk model...")
        self.model = Model(model_path)
        print("Vosk ready.")

    def transcribe(self, input_path):

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as tmp:
            wav_path = tmp.name

        try:

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    input_path,
                    "-ar", "16000",
                    "-ac", "1",
                    wav_path
                ],
                check=True,
                capture_output=True
            )

            wf = wave.open(wav_path, "rb")

            rec = KaldiRecognizer(
                self.model,
                wf.getframerate()
            )

            while True:

                data = wf.readframes(4000)

                if len(data) == 0:
                    break

                rec.AcceptWaveform(data)

            wf.close()

            result = json.loads(
                rec.FinalResult()
            )

            return result.get(
                "text",
                ""
            )

        finally:
            try:
                import os
                os.remove(wav_path)
            except Exception:
                pass