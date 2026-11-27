
Speech-to-Text (STT)
Overview
Luminesce supports microphone input through a browser-based Speech-to-Text (STT) pipeline using Vosk.

The implementation is intentionally simple:

Microphone
    ↓
Browser MediaRecorder
    ↓
audio/webm
    ↓
POST /api/transcribe
    ↓
ffmpeg
    ↓
16 kHz mono WAV
    ↓
Vosk
    ↓
Transcript
    ↓
Chat Input
The transcript is inserted into the chat input box where it can be reviewed, edited, or sent to the active model.

Components
Backend
lumin/ui/web/core/stt.py
Responsibilities:

Load the Vosk model
Convert WebM audio to WAV
Run speech recognition
Return transcript text
API Endpoint
POST /api/transcribe
Form field:

file
Example response:

{
    "success": true,
    "text": "what models are available"
}
Frontend
static/js/stt.js
Responsibilities:

Request microphone access
Record audio
Upload audio to /api/transcribe
Insert transcript into the chat input
UI
Current UI control:

Record
Workflow:

Record
    ↓
Speak
    ↓
Stop
    ↓
Transcript appears in input box
Dependencies
Python
Required:

vosk
python-multipart
System Packages
Required:

sudo apt install ffmpeg
Vosk Model
Current model:

lumin/models/vosk-model-small-en-us-0.15
Expected contents:

am/
conf/
graph/
ivector/
README
Browser Requirements
Microphone access requires a secure browser context.

For LAN development, Microsoft Edge can be configured to treat the Luminesce origin as secure:

edge://flags
Enable:

Insecure origins treated as secure
Example origin:

http://192.168.4.29:8000
This is intended only for local development and testing.

A future HTTPS deployment should eliminate the need for this workaround.

Testing
Backend API test:

curl -F "file=@recording.webm" \
http://localhost:8000/api/transcribe
Example result:

{
    "success": true,
    "text": "hello copilot running chat g t p"
}
Status
Implemented:

Vosk-based STT
Browser recording
Audio upload
Transcript generation
Transcript insertion into chat input
Planned:

Improved microphone controls
Modernized chat input UI
HTTPS deployment
Optional auto-send after transcription