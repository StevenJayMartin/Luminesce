import os
import json
import wave
import subprocess

from flask import Flask, render_template, request, jsonify
from vosk import Model, KaldiRecognizer

app = Flask(__name__)

MODEL_PATH = "models/vosk-model-small-en-us-0.15"
UPLOAD_DIR = "recordings"

os.makedirs(UPLOAD_DIR, exist_ok=True)

print("Loading Vosk model...")
model = Model(MODEL_PATH)
print("Model ready.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():

    audio_file = request.files["audio"]

    webm_path = os.path.join(
        UPLOAD_DIR,
        "recording.webm"
    )

    wav_path = os.path.join(
        UPLOAD_DIR,
        "recording.wav"
    )

    audio_file.save(webm_path)

    print(audio_file.content_type)

    subprocess.run(
        [
            r"C:\HOME_Scripts\ffmpeg\bin\ffmpeg.exe",
            "-y",
            "-i", webm_path,
            "-ar", "16000",
            "-ac", "1",
            wav_path
        ],
        check=True
    )

    wf = wave.open(wav_path, "rb")

    rec = KaldiRecognizer(
        model,
        wf.getframerate()
    )

    while True:
        data = wf.readframes(4000)

        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            pass

    wf.close()

    result = json.loads(
        rec.FinalResult()
    )

    text = result.get("text", "")

    return jsonify({
        "transcript": text
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )