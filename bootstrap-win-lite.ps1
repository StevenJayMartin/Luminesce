# requires PowerShell 5+ and admin privileges

# system prep
winget install -e --id Python.Python.3.12
winget install -e --id Git.Git
winget install -e --id Gyan.FFmpeg
winget install -e --id Microsoft.VisualStudio.2022.BuildTools

# clone
git clone https://github.com/StevenJayMartin/Luminesce
cd Luminesce

# python env
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip

# backend deps
pip install fastapi uvicorn websockets pydantic numpy soundfile vosk

# vosk model
New-Item -ItemType Directory -Force -Path models\vosk
Invoke-WebRequest `
  -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" `
  -OutFile "models\vosk\model.zip"
Expand-Archive models\vosk\model.zip models\vosk -Force

# piper windows binary
New-Item -ItemType Directory -Force -Path tts\piper
Invoke-WebRequest `
  -Uri "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_x86_64.exe" `
  -OutFile "tts\piper\piper.exe"

# piper voice model
New-Item -ItemType Directory -Force -Path tts\piper\models
Invoke-WebRequest `
  -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx" `
  -OutFile "tts\piper\models\ryan.onnx"

# fastapi server
Start-Process powershell -ArgumentList "uvicorn lumin.server:app --host 0.0.0.0 --port 8000"

# tui
Start-Process powershell -ArgumentList "python -m lumin.tui"

# open web ui
Start-Process "http://localhost:8000"

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
.\tts\piper\piper.exe `
  --model tts\piper\models\ryan.onnx `
  --output_file out.wav `
  "Luminesce online."

ffplay -nodisp -autoexit out.wav

