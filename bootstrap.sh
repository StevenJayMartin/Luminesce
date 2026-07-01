#!/usr/bin/env bash
set -e

# system prep
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl ffmpeg unzip

# clone
git clone https://github.com/StevenJayMartin/Luminesce
cd Luminesce

# python env
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# backend deps
pip install fastapi uvicorn websockets pydantic numpy soundfile vosk

# ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:8b

# vosk model
mkdir -p models/vosk
curl -L -o models/vosk/model.zip \
  https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip models/vosk/model.zip -d models/vosk/

# piper binary
mkdir -p tts/piper
curl -L -o tts/piper/piper \
  https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64
chmod +x tts/piper/piper

# piper voice model
mkdir -p tts/piper/models
curl -L -o tts/piper/models/ryan.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx

# fastapi server
uvicorn lumin.server:app --host 0.0.0.0 --port 8000 &
sleep 2

# tui
python -m lumin.tui &

# web front-end
xdg-open http://localhost:8000 || true

# test STT
python - <<EOF
from vosk import Model, KaldiRecognizer
import wave, json
wf = wave.open("test.wav","rb")
rec = KaldiRecognizer(Model("models/vosk"), wf.getframerate())
while True:
    data = wf.readframes(4000)
    if len(data)==0: break
    if rec.AcceptWaveform(data):
        print(rec.Result())
print(rec.FinalResult())
EOF

# test TTS
./tts/piper/piper \
  --model tts/piper/models/ryan.onnx \
  --output_file out.wav \
  <<< "Luminesce online."

ffplay -nodisp -autoexit out.wav || true

