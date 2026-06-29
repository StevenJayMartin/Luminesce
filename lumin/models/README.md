⭐ 1. lumin/models/README.md
This file explains why the folder is empty in Git and how to install models locally.

Code
# Lumin Models

This directory is intentionally empty in the GitHub repository.

Large machine‑learning models (Piper TTS voices, Vosk STT models, etc.)
exceed GitHub’s 100 MB file limit and are therefore **not stored in Git**.

## How to install models locally

Place your models here manually:

- Piper TTS models (`*.onnx`, `*.onnx.json`)
- Vosk STT models (folders such as `vosk-model-en-us-0.22-lgraph/`)

Example structure:

lumin/models/
en_US-ryan-high.onnx
en_US-ryan-high.onnx.json
vosk/
vosk-model-en-us-0.22-lgraph/

Code

## Why this folder is ignored

The `.gitignore` file contains:

lumin/models/

Code

This prevents accidental commits of large binary files.

## Important

If you clone the repository, you **must download the models yourself**
before running Lumin. See the project documentation for download links.
⭐ 2. scripts/download_models.ps1 (PowerShell helper)
This script makes it easy for users to download Piper + Vosk models without committing them.

Code
# Download Piper + Vosk models for Lumin
# Run this script from the project root:
#   powershell -ExecutionPolicy Bypass -File scripts/download_models.ps1

Write-Host "Downloading Piper model (en_US-ryan-high)..."

$PiperModelDir = "lumin/models"
New-Item -ItemType Directory -Force -Path $PiperModelDir | Out-Null

Invoke-WebRequest `
    -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx" `
    -OutFile "$PiperModelDir/en_US-ryan-high.onnx"

Invoke-WebRequest `
    -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json" `
    -OutFile "$PiperModelDir/en_US-ryan-high.onnx.json"

Write-Host "Piper model downloaded."

Write-Host "Downloading Vosk model (en-us-0.22-lgraph)..."

$VoskDir = "lumin/models/vosk"
New-Item -ItemType Directory -Force -Path $VoskDir | Out-Null

Invoke-WebRequest `
    -Uri "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip" `
    -OutFile "$VoskDir/vosk-model-en-us-0.22-lgraph.zip"

Write-Host "Extracting Vosk model..."
Expand-Archive "$VoskDir/vosk-model-en-us-0.22-lgraph.zip" -DestinationPath $VoskDir -Force

Remove-Item "$VoskDir/vosk-model-en-us-0.22-lgraph.zip"

Write-Host "Vosk model downloaded and extracted."
Write-Host "All models installed successfully."
This script:

downloads the Piper Ryan voice

downloads the Vosk STT model

extracts it

keeps everything local

avoids GitHub size limits

keeps your repo clean

⭐ These two files solve three big problems
✔ Prevent accidental commits of large models
Your .gitignore already blocks them, but the README explains why.

✔ Make onboarding easy
New users can run one script and get all required models.

✔ Keep your repo lightweight
No more 115MB ONNX files in history.
