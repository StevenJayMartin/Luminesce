🔥 Lumin + Ollama Performance Tuning Guide
This guide helps you squeeze maximum speed, responsiveness, and stability out of your local AI assistant — whether you’re running Qwen3, Llama 3.2, Phi‑4, or DeepSeek.

It covers:

Model performance tuning

Ollama configuration

GPU optimization

Memory & VRAM tuning

Streaming responsiveness

Tool‑calling optimization

Network & remote‑host tuning

TTS/STT performance

UI responsiveness

Let’s make Lumin fast.

⭐ 1. Choose the Right Model Size
Best balance of speed + intelligence
qwen3:7b

llama3.2:latest

Fastest on CPU
phi4:latest

Best for GPU rigs
qwen3:14b

llama3.2:11b

Avoid for speed
DeepSeek‑Coder‑V2 (amazing coder, slow general chat)

Mixtral models (too heavy for most setups)

⭐ 2. Enable GPU Acceleration (Critical)
Check if Ollama sees your GPU:

Code
ollama list
ollama run llama3.2 "test"
If GPU is active, you’ll see:

Code
using CUDA / ROCm / Metal
If not:

Linux (NVIDIA)
Install CUDA toolkit + drivers:

Code
sudo apt install nvidia-cuda-toolkit
Restart Ollama:

Code
sudo systemctl restart ollama
AMD
Install ROCm:

Code
sudo apt install rocm-dev
⭐ 3. Tune Ollama’s GPU Layers
You can force more layers onto GPU:

Code
ollama run qwen3:7b --gpu-layers 999
Or set globally in ~/.ollama/config.yaml:

yaml
gpu-layers: 999
More GPU layers = faster inference
Too many = crash → reduce until stable.

⭐ 4. Use Quantized Models for Speed
Quantization massively boosts speed with minimal quality loss.

Best formats:
Q4_K_M → fastest, still smart

Q5_K_M → great balance

Q8_0 → highest quality, slower

Pull quantized versions:

Code
ollama pull qwen3:7b-q4_K_M
⭐ 5. Tune Context Window
Large context = slower inference.

In config.json:

json
"context": 4096
Recommended:

4096 for speed

8192 for long conversations

16384+ only if you need it

⭐ 6. Optimize Streaming Responsiveness
Lumin streams tokens — so we want fast token generation.

In your Ollama client:
Use stream: true

Process tokens as soon as they arrive

Avoid blocking UI callbacks

Avoid heavy logging inside the token loop

In Python:
Use iter_lines() (you already do this correctly).

⭐ 7. Speed Up Tool‑Calling
Tool calls add latency — but we can minimize it.

1. Keep tool results short
Models slow down when fed huge tool outputs.

2. Use fast APIs
DuckDuckGo is good — but SearXNG is faster.

3. Cache results
Cache recent queries for 30–60 seconds.

4. Avoid multiple tool calls per turn
Your current client already stops after one — perfect.

⭐ 8. Tune Remote Ollama Hosts (Your 192.168.5.241 Setup)
You’re running Ollama on a LAN host — great idea.

To optimize:

1. Use HTTP keep‑alive
Ollama already supports this.

2. Use wired Ethernet if possible
Wi‑Fi adds jitter.

3. Increase MTU if your router supports it
Jumbo frames = smoother streaming.

4. Reduce network logging
Debug logs slow down token loops.

⭐ 9. Optimize TTS Performance
Your TTS is already fast — but you can make it snappier:

Pre‑warm the TTS engine on startup

Use a lightweight voice

Avoid long SSML

Stream TTS in parallel with token streaming

⭐ 10. Optimize STT (Vosk)
Vosk is CPU‑bound.

To speed it up:

Use the small model (you already do)

Reduce sample rate to 16 kHz (you already do)

Run STT in a separate thread

Disable STT when not listening

⭐ 11. UI Performance (Textual)
Textual is fast, but:

Avoid updating the UI every token

Batch updates every 20–40 ms

Use async tasks for TTS

Avoid heavy logging in the UI thread

⭐ 12. System‑Level Tuning
Linux
Enable hugepages

Disable CPU frequency scaling

Use performance governor:

Code
sudo cpupower frequency-set -g performance
Windows
Set power mode to “Best Performance”

Disable background apps

Ensure GPU is in “High Performance” mode

⭐ 13. Recommended Config for Maximum Speed
Here’s a killer setup:

json
{
  "model": "qwen3:7b-q4_K_M",
  "enable_tools": true,
  "context": 4096,
  "temperature": 0.4,
  "max_tokens": 2048
}
This gives you:

Fastest inference

Great tool‑calling

Low VRAM usage

Stable long conversations

⭐ 14. Recommended Config for Maximum Intelligence
json
{
  "model": "qwen3:14b-q5_K_M",
  "enable_tools": true,
  "context": 8192,
  "temperature": 0.6,
  "max_tokens": 4096
}
This gives you:

Best reasoning

Best tool‑calling

Still fast on GPU
