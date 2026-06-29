⭐ Lumin only uses the web when the model decides it needs fresh information
It is not forced, not always‑on, and not automatic.

It behaves like this:

✔ If the question requires current or unknown info → it calls the web
Example:
“Latest updates in Python 3.13”
“News today”
“What happened this week?”
“Who won the game?”

These are things the model cannot know from training, so it calls the tool.

✔ If the question is something the model already knows → it answers normally
Example:
“What is the capital of France”
“How do I write a Python loop”
“Explain recursion”
“Tell me a joke”

No tool call. No web. No DuckDuckGo.

✔ If the tool returns nothing useful → the model still answers
That’s what you saw:

DuckDuckGo returned a 202 with no Instant Answer, so the model said:

“I couldn’t find recent info on Python 3.13…”

That’s correct behavior.

⭐ So why did it look like it was “forced”?
Because your test question was exactly the kind of question that should trigger a tool call:

“latest updates in Python 3.13”

That’s a time‑sensitive query.
The model knows it cannot answer that from training.
So it correctly chose to call the web.

If you ask something timeless, you’ll see it not call the tool.

Try these:

“Explain list comprehensions in Python”

“What is 2+2”

“Write a haiku about the ocean”

“What is a GPU”

“Tell me a bedtime story”

You’ll see no web search.

⭐ If you want, I can tune the behavior
We can adjust the system prompt so Lumin:

uses the web more often

uses the web less often

only uses the web when you say “search”

or uses the web only when the user explicitly asks

Just tell me the style you want and I’ll tune it.

No I think it's great! Maybe we should produce a little read on web components though! Just to include. But BIG THANKS!
Oh that’s the perfect next move — now that Lumin’s web search pipeline is alive and humming, adding a clean little “Web Components” readme will make the whole system feel complete and future‑proof. And honestly, you’ve earned the right to document this victory.

Here’s a tight, friendly write‑up you can drop straight into your repo as web_components.md or fold into your main docs. It explains the moving parts without drowning anyone in implementation details.

Lumin Web Components Overview
Lumin includes a lightweight, privacy‑friendly web search capability powered by a simple tool‑calling architecture. This lets the assistant fetch fresh information when needed while keeping everything local and under your control.

What Triggers a Web Search
Lumin only uses the web when the model decides the question requires external or time‑sensitive information. Examples include:

“Latest updates in Python 3.13”

“What happened today in tech”

“Recent news about space launches”

For timeless or general knowledge questions, Lumin answers locally without calling the web.

How It Works
The flow is simple and predictable:

User asks a question

The model decides whether a tool call is needed

If so, it emits a structured tool request

Lumin runs the DuckDuckGo query

The result is fed back into the model

The model produces a final answer

The UI streams the response and TTS speaks it

This keeps the assistant responsive, accurate, and grounded.

DuckDuckGo Instant Answer API
Lumin uses the DuckDuckGo Instant Answer API because it:

Requires no API key

Returns fast, structured summaries

Respects privacy

Works well with tool‑calling models

The tool returns a short text summary that the model incorporates naturally into its final answer.

Why This Matters
Adding web search transforms Lumin from a static model into a dynamic assistant that can:

Check current events

Fetch up‑to‑date facts

Provide context beyond training data

Stay relevant without cloud services

And because the tool is optional and model‑driven, Lumin stays efficient and doesn’t overuse the web.

If you want, I can also help you write a “Tools Architecture” page, a “How Lumin Decides to Search” page, or a “Debugging Tool Calls” page. Just say the word — I’m here for the whole journey.

TY so much and fantastic work!
You’re very welcome — and honestly, watching you bring Lumin to life has been a blast. You pushed through every weird edge case, every silent hang, every model quirk, and now you’ve got a real, responsive, voice‑driven, tool‑calling assistant running entirely on your own hardware. That’s not small stuff. That’s creator‑level work.

And the best part is that you’re not just using this thing — you understand it. You debugged it. You shaped it. You made it yours. That’s the kind of foundation that lets you keep building without fear.

If you ever want to expand Lumin’s world — more tools, richer UI, smoother animations, deeper memory, or just more personality — I’m right here with you.

What are the tools supporting models I can pull? I just got qwen3
Ohhh you’re gonna love this answer — because you now have access to some of the best tool‑calling models available today, and you can pull them straight into Ollama with one‑liners.

Let’s break it down cleanly so you know exactly what’s worth installing and why.

⭐ Top Tool‑Calling Models You Can Pull in Ollama (2026)
These models support structured function calling / tool calling, meaning they can emit JSON tool requests just like your DuckDuckGo test.

Below are the ones that work reliably with tools.

✅ 1. Qwen2.5 / Qwen3 (AMAZING tool‑calling)
You said you just got qwen3 — excellent choice.

Qwen models are currently the most reliable tool‑callers in the open‑source world.

Pull commands:
Code
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
ollama pull qwen3:7b
ollama pull qwen3:14b
Why they’re great:
Extremely accurate tool‑calling

Very clean JSON

Rarely hallucinate tool names

Great for coding + reasoning

Fast on CPU, excellent on GPU

If you want the best, Qwen is it.

✅ 2. Llama 3.2 (your current model — supports tools!)
You already confirmed llama3.2:latest emits tool calls.

Pull commands:
Code
ollama pull llama3.2:latest
ollama pull llama3.2:3b
ollama pull llama3.2:11b
Why it’s good:
Lightweight

Fast

Good tool‑calling

Great for general chat

You’re already using this successfully.

✅ 3. Phi‑3.5 / Phi‑4 (Microsoft)
These are surprisingly strong for their size.

Pull commands:
Code
ollama pull phi3.5:latest
ollama pull phi4:latest
Why they’re good:
Very small

Very fast

Good structured output

Great for embedded assistants

Not as strong as Qwen for tools, but still solid.

⚠️ 4. DeepSeek‑Coder‑V2 (partial tool support)
DeepSeek models can tool‑call, but they’re inconsistent.

Pull:
Code
ollama pull deepseek-coder-v2:latest
Notes:
Sometimes emits malformed JSON

Sometimes refuses to call tools

Great coder, but not a great tool‑caller

Use only if you want raw coding power.

⚠️ 5. CodeLlama / StarCoder2 (weak tool support)
They can sometimes emit tool calls, but not reliably.

Pull:
Code
ollama pull codellama:13b
ollama pull starcoder2:7b
Notes:
Good for coding

Not good for tool‑calling

Use Qwen instead

⭐ Recommended Setup for Lumin (Best Combo)
If you want the best possible tool‑calling experience, use:

🔥 Primary model:
qwen3:7b or qwen3:14b

🔥 Backup model:
llama3.2:latest

This combo gives you:

Best tool‑calling

Best JSON

Best reasoning

Fast responses

Low hallucination rate

⭐ Want me to generate a “Tool‑Calling Models Guide” for your repo?
Something like:

What models support tools

How to pull them

How to benchmark them

How to switch models in Lumin

How to tune system prompts for each model

Just say “Yes, generate the guide” and I’ll produce a clean, polished markdown file for you.

Yes please
Absolutely — here is a clean, polished, drop‑in‑ready Markdown guide you can add to your repo.
It’s written to be clear, friendly, and useful for anyone who wants to understand which models support tools and how to use them with Lumin.

Tool‑Calling Models Guide (Lumin Assistant)
Lumin supports any local model that can emit structured function calls (also called tool calls).
This guide explains which models work best, how to pull them, and how to choose the right one for your setup.

⭐ What Is a “Tool‑Calling Model”?
A tool‑calling model is an LLM that can output structured JSON like:

json
{
  "tool_calls": [
    {
      "function": {
        "name": "web_search",
        "arguments": { "query": "latest Python news" }
      }
    }
  ]
}
Lumin uses this to trigger real actions such as:

Web search

System utilities

Local file operations

Custom tools you add

Not all models can do this reliably — but the ones below do.

⭐ Recommended Models (Best for Lumin)
These models are the most reliable for tool‑calling and structured output.

🥇 Qwen3 / Qwen2.5 (Best Overall)
Why it’s great:

Extremely accurate tool‑calling

Clean JSON

Strong reasoning

Great coding performance

Fast on CPU and GPU

Pull commands:

Code
ollama pull qwen3:7b
ollama pull qwen3:14b
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
Recommended: qwen3:7b (best balance of speed + intelligence)

🥈 Llama 3.2 (Solid, Lightweight, Reliable)
Why it’s great:

Good tool‑calling

Very fast

Low memory usage

Great general assistant behavior

Pull commands:

Code
ollama pull llama3.2:latest
ollama pull llama3.2:3b
ollama pull llama3.2:11b
Recommended: llama3.2:latest

🥉 Phi‑3.5 / Phi‑4 (Small but Mighty)
Why it’s great:

Very small

Very fast

Good structured output

Great for embedded or low‑power systems

Pull commands:

Code
ollama pull phi3.5:latest
ollama pull phi4:latest
Recommended: phi4:latest if you want tiny + smart

⚠️ Models With Partial Tool Support
These models can tool‑call, but not reliably.

DeepSeek‑Coder‑V2
Pros:

Incredible coding performance

Great reasoning

Cons:

JSON sometimes malformed

Tool calls inconsistent

Pull:

Code
ollama pull deepseek-coder-v2:latest
Use only if you want raw coding power.

CodeLlama / StarCoder2
Pros:

Good for coding tasks

Cons:

Weak tool‑calling

Often ignores tool specs

Pull:

Code
ollama pull codellama:13b
ollama pull starcoder2:7b
❌ Models Not Recommended for Tools
These models either:

Don’t support tool‑calling

Produce unreliable JSON

Ignore tool specs entirely

Examples:

Mistral 7B

Mixtral 8x7B

Gemma 2B / 7B

LLaVA / vision models

They work fine for chat, but not for Lumin’s tool system.

⭐ Choosing the Right Model
Goal	Best Model
Best tool‑calling	Qwen3:7b or 14b
Fastest on CPU	Phi‑4
Best all‑around	Llama3.2:latest
Best coder	DeepSeek‑Coder‑V2
Lowest VRAM	Phi‑3.5


⭐ Switching Models in Lumin
Edit your config.json:

json
{
  "model": "qwen3:7b",
  "enable_tools": true
}
Restart Lumin and you’re good to go.

⭐ Final Notes
All recommended models work fully offline

No API keys required

Tool‑calling behavior is controlled by your system prompt

You can mix and match models depending on your workflow
