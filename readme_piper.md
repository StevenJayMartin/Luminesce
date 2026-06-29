
1. Download Piper (Windows binary)
Download the official Piper Windows build:

https://sourceforge.net/projects/piper-tts.mirror/files/2023.11.14-2/piper_windows_amd64.zip/download

scan for vulnerabilities...
extract to {"yourrepodir"}/OllamaLumin/piper #- aka mkdir piper move it from downloads...

mv piper_windows_amd64/piper/* .
rm -rf piper_windows_amd64/

⭐2. Download the Ryan voice model
Download both files:

en_US-ryan-high.onnx

en_US-ryan-high.onnx.json

Place them inside your repo:

Code
lumin/voice/models/en_US-ryan-high.onnx
lumin/voice/models/en_US-ryan-high.onnx.json
This keeps your voice assets version‑controlled and portable.

⭐ 3. Add simpleaudio to your environment
Install the WAV player:

Code
pip install simpleaudio
This is the simplest, most stable cross‑platform WAV playback library.
