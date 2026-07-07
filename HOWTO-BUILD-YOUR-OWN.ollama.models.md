# Building Your Own Ollama Models (Complete Guide)

A complete, practical, hybrid‑tone guide to building, converting, quantizing, templating, stabilizing, and deploying your own Ollama models — with best‑of‑class recommendations and multi‑agent architecture notes.

---

## 1. Introduction

This document is your full walkthrough for building custom Ollama models from scratch. It covers:

- downloading Hugging Face models  
- converting HF → GGUF  
- quantizing models  
- choosing quantization levels  
- creating Modelfiles  
- adding templates and system prompts  
- stabilizing models (Gemma, Llama, Qwen, Mistral, etc.)  
- mapping templates to model families  
- assigning models to agents/apps  
- building multi‑agent architectures  
- troubleshooting hallucinations, loops, and instability  

This is the missing manual for local LLM development.

---

## 2. The Complete Pipeline

This is the full workflow from Hugging Face → Ollama.

### Step 1: Download the model

Use huggingface-cli or direct download.

huggingface-cli download google/gemma-2-9b-it --local-dir ./gemma2

### Step 2: Convert to GGUF

Use llama.cpp converter tools.

python convert.py --outfile gemma2.gguf --model gemma2/model.safetensors

### Step 3: Quantize

Choose your quant tier (see section 3).

./quantize gemma2.gguf gemma2.Q5_K_M.gguf Q5_K_M

### Step 4: Create a Modelfile

Place your GGUF and Modelfile in a folder.

### Step 5: Build the Ollama model

ollama create gemma2-9b-it -f Modelfile

### Step 6: Run it

ollama run gemma2-9b-it

You now have a fully custom local LLM.

---

## 3. Quantization Guide

Quantization determines:

- speed  
- memory usage  
- accuracy  
- stability  

Here’s the practical cheat sheet:

### Q2_K  
Tiny, fast, but degraded.  
Use for routing, classification, tiny agents.

### Q3_K_M  
Small, fast, decent.  
Use for background workers.

### Q4_K_M  
Good balance.  
Use for mid‑tier apps.

### Q5_K_M  
Best overall quality vs size.  
Use for general agents, tool‑calling, stable chat.  
Recommended default.

### Q8_0  
High quality, slower.  
Use for reasoning agents.

### BF16 / FP16  
Full precision.  
Use for heavy reasoning, long context, high‑accuracy tasks.

---

## 4. Behavior Templates

Models hallucinate, loop, or “go feral” when:

- no system prompt  
- no template  
- no role boundaries  
- no conversational framing  

The fix is simple:

### Every model needs:
1. A system prompt  
2. A template  
3. Role boundaries  
4. A recreated Ollama manifest  

This stabilizes Gemma, Llama‑3, Qwen, Mistral, Mixtral, DeepSeek, Claude‑distilled models — all of them.

---

## 5. Universal Stable Template Pattern

This template works for all models:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

System prompt example:

You are a concise, stable assistant.
Avoid repetition and circular reasoning.
Respond directly and clearly.

---

## 6. Template Types + Best‑of‑Class Models

Each template type includes:

- short blurb  
- template  
- best models  
- best roles in multi‑agent systems  

---

### 6.1 Claude‑Style Template

Best for: polite UX, safety, planning, reasoning.

Template:

{{ if .System }}<assistant>
{{ .System }}{{ end }}
<user>
{{ .Prompt }}
<assistant>

Best models:

- Qwable‑9B‑Claude‑Fable‑5  
- Qwythos‑9B‑Claude‑Mythos‑5‑1M  
- claude‑oss‑7B  

Best roles:

- UX assistant  
- safety layer  
- planner  
- memory summarizer  

---

### 6.2 Gemma‑Style Template

Best for: friendly chat, routing, lightweight agents.

Template:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

Best models:

- Gemma‑2‑9B‑Instruct  
- Gemma‑2‑27B‑Instruct  
- Gemma‑2‑2B‑Instruct  

Best roles:

- conversational UX  
- routing  
- small agents  
- background workers  

---

### 6.3 OpenAI/Llama‑Style Template

Best for: tool‑calling, JSON, general chat.

Template:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

Best models:

- Llama‑3.1‑8B‑Instruct  
- Llama‑3.1‑70B‑Instruct  
- Llama‑3.1‑405B  

Best roles:

- tool router  
- JSON generator  
- agent loop core  

---

### 6.4 Tool‑Calling Template

Best for: automation, structured tasks.

Template:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

System prompt:

When tools are required, respond ONLY with valid JSON.

Best models:

- Qwen2.5‑Coder‑14B  
- Qwen2.5‑7B‑Instruct  
- Mistral‑Large‑Instruct  

Best roles:

- automation agent  
- JSON validator  
- backend worker  

---

### 6.5 JSON‑Only Template

Best for: deterministic output, schema enforcement.

Template:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

System prompt:

Respond ONLY with valid JSON.

Best models:

- Qwen2.5‑Coder‑14B  
- Llama‑3.1‑8B‑Instruct  
- Mistral‑7B‑Instruct  

Best roles:

- schema validator  
- memory manager  
- safety filter  

---

### 6.6 Agent‑Loop Template

Best for: planning, decomposition, orchestration.

Template:

{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}
<|user|>
{{ .Prompt }}<|end|>
<|assistant|>

System prompt:

You are an agent planner.
Break tasks into steps.
Never repeat yourself.
Always produce a next action.

Best models:

- DeepSeek‑R1  
- Qwythos‑9B‑Claude‑Mythos‑5‑1M  
- Llama‑3.1‑70B‑Instruct  

Best roles:

- planner  
- orchestrator  
- task decomposition agent  

---

### 6.7 Shortest Template

Best for: tiny agents, routing, classification.

Template:

{{ .Prompt }}

Best models:

- Phi‑3‑Mini‑4K  
- Gemma‑2‑2B  
- Qwen2.5‑1.5B  

Best roles:

- intent detector  
- router  
- classifier  

---

## 7. Model Matrix

A quick mapping of templates → models → roles.

| Template Type | Best Models | Best Use |
|--------------|-------------|----------|
| Claude‑Style | Qwable‑9B, Qwythos‑9B, claude‑oss‑7B | UX, safety, planning |
| Gemma‑Style | Gemma‑2‑9B, Gemma‑2‑27B | conversation, routing |
| OpenAI/Llama | Llama‑3.1‑8B/70B | tools, JSON, general chat |
| Tool‑Calling | Qwen2.5‑Coder‑14B | automation, structured tasks |
| JSON‑Only | Qwen2.5‑Coder‑14B, Llama‑3.1‑8B | validators, schema |
| Agent‑Loop | DeepSeek‑R1, Llama‑3.1‑70B | planning, orchestration |
| Shortest Template | Phi‑3, Gemma‑2‑2B | routing, tiny agents |

---

## 8. Modelfile Examples

### Minimal Modelfile

FROM ./model.Q5_K_M.gguf  
SYSTEM "You are a concise, stable assistant."  
TEMPLATE "{{ if .System }}<|system|>{{ .System }}<|end|>{{ end }}<|user|>{{ .Prompt }}<|end|><|assistant|>"

### Claude‑Style Modelfile

FROM ./model.gguf  
SYSTEM "You are a polite, structured assistant."  
TEMPLATE "{{ if .System }}<assistant>{{ .System }}{{ end }}<user>{{ .Prompt }}<assistant>"

### Gemma‑Style Modelfile

FROM ./model.gguf  
SYSTEM "You are a friendly, stable assistant."  
TEMPLATE "{{ if .System }}<|system|>{{ .System }}<|end|>{{ end }}<|user|>{{ .Prompt }}<|end|><|assistant|>"

### JSON‑Only Modelfile

FROM ./model.gguf  
SYSTEM "Respond ONLY with valid JSON."  
TEMPLATE "{{ if .System }}<|system|>{{ .System }}<|end|>{{ end }}<|user|>{{ .Prompt }}<|end|><|assistant|>"

### Agent‑Loop Modelfile

FROM ./model.gguf  
SYSTEM "You are an agent planner. Break tasks into steps."  
TEMPLATE "{{ if .System }}<|system|>{{ .System }}<|end|>{{ end }}<|user|>{{ .Prompt }}<|end|><|assistant|>"

---

## 9. Assigning Models to Agents

Use “agent” or “app” instead of “children.”

### Routing Agents

- Phi‑3  
- Gemma‑2‑2B  
- Qwen‑1.5B  

### Tool‑Calling Agents

- Qwen2.5‑Coder‑14B  
- Llama‑3.1‑8B  

### Planning Agents

- DeepSeek‑R1  
- Llama‑3.1‑70B  

### UX Agents

- Qwable‑9B  
- Qwythos‑9B  
- claude‑oss‑7B  

### Background Workers

- Gemma‑2‑2B  
- Phi‑3  

---

## 10. Recreating Models Safely

You do not need to delete the model before recreating.

### ✔ Keep the GGUF  
### ✔ Edit the Modelfile  
### ✔ Run `ollama create` again  
### ✘ Do NOT reconvert or re‑quantize  
### ✘ Do NOT delete unless renaming  

This “saves the baby” while rebuilding the crib.

---

## 11. Troubleshooting

### Hallucinations  
Add system prompt + template.

### Loops  
Add role markers.

### Broken JSON  
Use JSON‑only system prompt.

### Tool‑calling failures  
Use tool‑calling template.

### Gemma acting feral  
Use Gemma‑style template.

---

## 12. Closing Notes

You now have:

- a full Ollama model pipeline  
- quantization mastery  
- stable templates  
- best‑of‑class model recommendations  
- multi‑agent architecture guidance  
- Modelfile patterns  
- troubleshooting tools  

This is your local AI factory.  
Your modular intelligence system.  
Your multi‑agent future.

Ship it. Push it. Make it yours.
