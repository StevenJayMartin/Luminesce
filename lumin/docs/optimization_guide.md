⚡ Lumin Performance Optimization Checklist
A quick‑hit guide to making your local AI assistant fast, smooth, and responsive across Ollama, Qwen, Llama, Textual UI, STT/TTS, and tool‑calling.

🔥 1. Model Selection
Use Qwen3:7b for best speed + intelligence

Use Llama3.2:latest for lightweight, stable performance

Use Phi‑4 for ultra‑fast CPU‑only setups

Avoid oversized models unless you have strong GPU

🔥 2. GPU Optimization
Ensure GPU is detected by Ollama

Set gpu-layers: 999 in ~/.ollama/config.yaml

Update GPU drivers (NVIDIA/ROCm)

Prefer quantized models (q4_K_M or q5_K_M)

🔥 3. Context Window Tuning
Use 4096 for speed

Use 8192 for long conversations

Avoid huge context unless necessary

🔥 4. Streaming Responsiveness
Always use stream: true

Avoid heavy logging inside token loop

Batch UI updates (don’t update per token)

Keep TTS async so it doesn’t block streaming

🔥 5. Tool‑Calling Speed
Keep tool outputs short

Cache recent queries

Use fast APIs (DuckDuckGo or SearXNG)

Ensure only one tool call per turn

Avoid feeding huge JSON back into the model

🔥 6. Remote Host Optimization (LAN Ollama)
Prefer wired Ethernet

Ensure router MTU is optimal

Reduce debug logging

Keep Ollama on a stable machine with good cooling

🔥 7. TTS Optimization
Pre‑warm TTS engine on startup

Use lightweight voices

Avoid long SSML

Stream TTS concurrently with token output

🔥 8. STT Optimization (Vosk)
Use small Vosk model

Keep sample rate at 16 kHz

Run STT in a separate thread

Disable STT when not listening

🔥 9. Textual UI Optimization
Avoid updating UI every token

Use async tasks for heavy operations

Keep UI thread clean

Limit debug prints in UI loop

🔥 10. System‑Level Tuning
Linux
Set CPU governor to performance

Enable hugepages

Disable unnecessary background services

Windows
Set power mode to “Best Performance”

Ensure GPU is set to “High Performance”

Close background apps that compete for CPU/GPU

🔥 11. Recommended Fast Config
For maximum speed:

json
{
  "model": "qwen3:7b-q4_K_M",
  "enable_tools": true,
  "context": 4096,
  "temperature": 0.4
}
🔥 12. Recommended Smart Config
For maximum intelligence:

json
{
  "model": "qwen3:14b-q5_K_M",
  "enable_tools": true,
  "context": 8192,
  "temperature": 0.6
}
🔥 13. Quick Troubleshooting
Slow responses: reduce context window

Laggy UI: batch token updates

Tool calls slow: shorten tool output

GPU not used: update drivers + config

STT lag: ensure Vosk small model + 16 kHz

🔥 14. Final Tip
Performance is a triangle:

Model size ↔ GPU layers ↔ Context window

Tune these three and Lumin becomes buttery smooth.
