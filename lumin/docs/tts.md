
Text-to-Speech (TTS)
Overview
Luminesce supports speech playback using a local ONNX-based TTS engine.

The implementation is intentionally lightweight:

Assistant Response
        ↓
Speak Button
        ↓
POST /api/tts
        ↓
ONNX TTS Engine
        ↓
WAV Audio
        ↓
Browser Playback
Speech playback is optional and user-controlled.

The assistant never automatically speaks responses.

Components
Backend
lumin/voice/tts_onnx.py
Responsibilities:

Load ONNX voice models
Generate WAV audio
Return audio to the web interface
API Endpoint
POST /api/tts
Request:

{
    "text": "Hello world"
}
Response:

audio/wav
Frontend
static/js/speech.js
Responsibilities:

Queue speech requests
Split long responses into chunks
Request audio from /api/tts
Play audio in sequence
Stop playback when requested
UI
Assistant messages contain a speaker button:

🔊
Workflow:

Assistant Message
        ↓
Click 🔊
        ↓
speech.js
        ↓
/api/tts
        ↓
Audio Playback
Components in app.py
Initialization:

tts_engine = OnnxTTS(
    "lumin/models/onnx"
)
Endpoint:

@app.post("/api/tts")
Speech generation:

wav = tts_engine.synthesize(text)
Voice Models
Current location:

lumin/models/onnx
Expected contents:

ONNX model files
voice configuration files
Queue-Based Playback
The browser uses a simple queue system.

Text
 ↓
Split into chunks
 ↓
Queue
 ↓
Generate audio
 ↓
Play
 ↓
Next chunk
Advantages:

Prevents overlapping speech
Handles long responses
Allows interruption
Keeps browser memory usage low
Controls
Speak text:

window.speakText(text);
Stop playback:

window.stopSpeech();
UI Button:

Stop Speech
Design Principles
TTS is treated as an output enhancement.

The primary interface remains:

Text
 ↓
LLM
 ↓
Text
Speech is optional:

Text
 ↓
TTS
 ↓
Audio
The chat experience remains fully usable if audio playback is disabled.

Status
Implemented:

ONNX TTS engine
Browser audio playback
Message speaker buttons
Queue-based speech playback
Stop speech control
Planned:

Voice selection
Adjustable speaking rate
Adjustable volume
Streaming audio generation
Per-session voice preferences

TTS Model Notes
The current ONNX voice model was one of the more difficult parts of the TTS stack to locate and integrate.

Source:

https://huggingface.co/MiaoMint/MeloTTS-ONNX/tree/main/onnx_exports

The model was selected because it produced usable ONNX exports compatible with the Luminesce ONNX TTS pipeline.

Current implementation:

tts_engine = OnnxTTS(
    "lumin/models/onnx"
)
Model files are stored under:

lumin/models/onnx
Historical Notes
Several TTS backends were evaluated during development:

Piper
Sherpa-ONNX
ONNX exported voice models
Obtaining a compatible ONNX voice model proved significantly more challenging than implementing the TTS API itself.

For future maintenance:

Keep a copy of the original model source URL.
Keep local backups of downloaded model files.
Avoid assuming upstream model locations will remain available indefinitely.
