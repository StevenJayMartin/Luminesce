📄 INSTALL_PIPER.md
Piper Text‑to‑Speech Installation Guide for Luminesce (Windows)
This document explains how to install and configure Piper TTS for use inside the Luminesce project. Piper provides high‑quality, offline speech synthesis and integrates directly with Luminesce’s TTS class.

⭐ 1. Download Piper (Windows Build)
Download the official Piper Windows release from GitHub:

Piper Releases: https://github.com/rhasspy/piper/releases (github.com in Bing)

Download the file named similar to:

Code
piper_windows_amd64.zip
Extract the archive. You should get:

Code
piper.exe
voices/
models/
⭐ 2. Add Piper to the Luminesce Repository
Copy the entire extracted Piper directory into your Luminesce project:

Code
C:/HOME_Scripts/Luminesce/piper/
Your project structure should now include:

Code
Luminesce/
    piper/
        piper.exe
        voices/
        models/
    lumin/
    README.md
    ...
This ensures Luminesce can locate Piper.exe and its voice models.

⭐ 3. Choose a Voice Model
Inside:

Code
Luminesce/piper/models/
select a .onnx model to use. For example:

Code
en_US-ryan-high.onnx
You may download additional voices from the Piper releases page.

⭐ 4. Configure Luminesce to Use Piper
Wherever you instantiate the TTS class, set the correct paths:

python
tts = TTS(
    piper_path="C:/HOME_Scripts/Luminesce/piper/piper.exe",
    model_path="C:/HOME_Scripts/Luminesce/piper/models/en_US-ryan-high.onnx"
)
Or use os.path.join for portability:

python
BASE = "C:/HOME_Scripts/Luminesce"

tts = TTS(
    piper_path=os.path.join(BASE, "piper", "piper.exe"),
    model_path=os.path.join(BASE, "piper", "models", "en_US-ryan-high.onnx")
)
Luminesce requires absolute paths for Piper.exe and the model.

⭐ 5. Verify Installation
Open PowerShell and run:

powershell
Test-Path "C:/HOME_Scripts/Luminesce/piper/piper.exe"
Expected output:

Code
True
Then verify the model:

powershell
Test-Path "C:/HOME_Scripts/Luminesce/piper/models/en_US-ryan-high.onnx"
Expected output:

Code
True
If either returns False, check your folder placement.

⭐ 6. Optional: Test Piper Manually
From PowerShell:

powershell
cd C:/HOME_Scripts/Luminesce/piper
.\piper.exe -m models/en_US-ryan-high.onnx -f test.wav
Type some text when prompted.
If test.wav appears, Piper is working correctly.

⭐ 7. Run Luminesce
Start your application normally:

Code
python main.py
Send a message that triggers TTS.
You should see logs similar to:

Code
[DEBUG] tts: Piper TTS speaking: ...
And hear audio output.

⭐ 8. Troubleshooting
❌ WinError 2 — “The system cannot find the file specified”
Cause: Piper.exe path is incorrect or Piper folder missing.
Fix: Ensure piper.exe exists at:

Code
C:/HOME_Scripts/Luminesce/piper/piper.exe
❌ No audio plays
Cause: WAV file not generated or winsound blocked.
Fix: Verify Piper.exe runs manually.

❌ Piper crashes or produces distorted audio
Cause: Model too large for system.
Fix: Try a medium or low‑quality .onnx model.

⭐ 9. Notes
Piper runs entirely offline.

Models vary in size and quality.

You may add multiple voices and switch between them in your config.

Luminesce deletes temporary WAV files automatically after playback.
