import os
import json
import uuid
import requests
import subprocess
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from lumin.tools.prompts import INTENT_SYSTEM_PROMPT
from lumin.tools.router import route_intent
from lumin.agent.tools import execute_tool, format_tool_results
from lumin.agent.continue_llm import continue_llm_with_tool_results

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
STATIC_PATH = os.path.join(BASE_DIR, "static")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "config.json")

# ------------------------------------------------------------
# LOAD CONFIG.JSON
# ------------------------------------------------------------
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

PERSONALITY_DIR = os.path.join(os.path.dirname(CONFIG_PATH), "prompts")


def load_personality_prompt(model_name: str) -> str:
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})

    personality_name = model_map.get(model_name, "default")
    personality_path = personalities.get(personality_name)

    if not personality_path:
        return SYSTEM_PROMPT  # fallback

    full_path = os.path.join(os.path.dirname(CONFIG_PATH), personality_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"ERROR loading personality '{personality_name}':", e)
        return SYSTEM_PROMPT


def call_rag_server(query: str, session_id: str) -> str | None:
    rag_cfg = config.get("rag", {})
    if not rag_cfg.get("enabled"):
        return None

    try:
        resp = requests.post(
            rag_cfg["url"],
            json={"query": query, "session": session_id},
            timeout=3,
        )
        data = resp.json()
        return data.get("augmented_prompt")
    except Exception as e:
        print("RAG unavailable:", e)
        return None


# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.get("/")
def root():
    return FileResponse(INDEX_PATH)


@app.get("/config")
def get_config():
    return {
        "ollama": {
            "url": config["backend"]["ollama_url"],
            "model": config["backend"]["model"],
            "mode": "chat",
        },
        "ui": config["ui_web"],
    }


@app.get("/api/personalities")
def list_personalities():
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})
    current_model = config["backend"]["model"]
    current_personality = model_map.get(current_model, "default")

    return {
        "personalities": list(personalities.keys()),
        "current_model": current_model,
        "current_personality": current_personality,
        "model_personality_map": model_map,
    }


@app.post("/api/set-personality")
async def set_personality(req: dict):
    model_name = req.get("model") or config["backend"]["model"]
    personality_name = req.get("personality")

    if not personality_name:
        return {"ok": False, "error": "No personality provided"}

    if "personalities" not in config or personality_name not in config["personalities"]:
        return {"ok": False, "error": "Unknown personality"}

    model_map = config.get("model_personality_map", {})
    model_map[model_name] = personality_name
    config["model_personality_map"] = model_map

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print("ERROR writing config.json:", e)
        return {"ok": False, "error": str(e)}

    return {"ok": True, "model": model_name, "personality": personality_name}


@app.get("/api/models")
def list_models():
    try:
        r = requests.get(f"{config['backend']['ollama_url']}/api/tags")
        data = r.json()
        models = [m.get("name") for m in data.get("models", [])]
        return {"models": models}
    except Exception as e:
        print("ERROR in /api/models:", e)
        return {"models": [], "error": str(e)}


@app.get("/api/model-info")
def model_info():
    info = {
        "model": config["backend"]["model"],
        "backend": config["backend"]["ollama_url"],
    }

    # Ollama ps
    try:
        r = requests.get(f"{config['backend']['ollama_url']}/api/ps")
        ps = r.json()
        info["running"] = ps.get("models", [])
    except Exception as e:
        info["running_error"] = str(e)

    # GPU via nvidia-smi (best-effort)
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
        parts = [p.strip() for p in out.split(",")]
        info["gpu"] = {
            "name": parts[0],
            "memory_used": parts[1] + " MiB",
            "memory_total": parts[2] + " MiB",
            "utilization": parts[3] + " %",
            "temperature": parts[4] + " C",
        }
    except Exception as e:
        info["gpu_error"] = str(e)

    return info


@app.post("/api/set-model")
async def set_model(req: dict):
    new_model = req.get("model")
    if not new_model:
        return {"ok": False, "error": "No model provided"}

    config["backend"]["model"] = new_model

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print("ERROR writing config.json:", e)
        return {"ok": False, "error": str(e)}

    return {"ok": True, "model": new_model}


# ------------------------------------------------------------
# SYSTEM / PERSONA PROMPT
# ------------------------------------------------------------

SYSTEM_PROMPT = """
You are Lumin, a local, privacy-first, Markdown-fluent AI assistant.
You respond with well-structured Markdown, using headings, lists, and code blocks when helpful.
You are concise, friendly, and practical, and you never mention external services or clouds.

Identity:
- You run using whichever local model the user has configured (typically an Ollama model).
- You do not know your internal architecture unless the user provides it.
- You do not claim to be built from scratch, open-source, or hosted anywhere.
- You do not claim affiliation with any company (Facebook, Google, etc.).
- You do not invent details about your creators or development history.
- You do not claim to run on your own server; you simply run wherever the user has configured you.

Behavior:
- You answer clearly, calmly, and truthfully.
- You avoid speculation about your origin or capabilities.
- If asked "What LLM are you?", respond: "I run on whichever local model you have configured."
- If asked about your architecture, respond: "My behavior depends on your local configuration."
- You respond using clean, well-structured Markdown when helpful.

Boundaries:
- You do not simulate internet access.
- You do not fabricate tool results.
- You do not invent system details.
- You do not mention clouds or external services.
"""

REASONING_PROMPT = """
You are a reasoning engine. Respond ONLY with valid JSON. 
No prose. No explanations. No markdown. No commentary. 
Your response MUST begin with '{' and end with '}'.

JSON schema:
{
  "thought": "string",
  "intent": "string",
  "plan": ["string"],
  "decision": "none | respond | call_tool"
}

Rules:
- Do NOT add any text before or after the JSON.
- Do NOT include backticks.
- Do NOT include comments.
- Do NOT explain the JSON.
- Do NOT apologize.
- Do NOT add extra fields.
- Do NOT add trailing commas.
- Produce concise values.
"""

# ------------------------------------------------------------
# GENERATE ENDPOINT (non-stream, Markdown-aware)
# ------------------------------------------------------------

conversations = {}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    raw = await file.read()

    try:
        text = raw.decode("utf-8")
        decoded = True
    except Exception:
        decoded = False
        text = None

    session_id = "default"
    if session_id not in conversations:
        conversations[session_id] = []

    if decoded:
        conversations[session_id].append(
            {
                "role": "user",
                "content": f"[Uploaded file: {file.filename}]\n{text}",
            }
        )
    else:
        conversations[session_id].append(
            {
                "role": "user",
                "content": (
                    f"[Uploaded file: {file.filename} — binary data, {len(raw)} bytes]"
                ),
            }
        )

    if decoded:
        preview = text[:500]
        return {
            "reply": (
                f"I received **{file.filename}** and successfully read it.\n\n"
                f"Here is a preview:\n\n"
                f"{preview}\n\n"
                f"(The full content is now part of the conversation, "
                f"so you can ask me questions about it.)"
            )
        }
    else:
        return {
            "reply": (
                f"I received **{file.filename}**, but it isn't a text file I can decode.\n"
                f"I stored its metadata in the conversation so you can still ask me about it."
            )
        }


@app.post("/api/generate")
async def generate(req: dict):
    text = req.get("text", "")
    if not text:
        return {"reply": ""}

    model_name = config["backend"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    session_id = "default"
    if session_id not in conversations:
        conversations[session_id] = []

    conversations[session_id].append({"role": "user", "content": text})

    transcript = personality_prompt.strip() + "\n\n"
    for m in conversations[session_id]:
        transcript += f"{m['role'].capitalize()}: {m['content']}\n"
    transcript += "Assistant:"

    payload = {
        "model": model_name,
        "prompt": transcript,
        "stream": False,
    }

    try:
        r = requests.post(
            f"{config['backend']['ollama_url']}/api/generate",
            json=payload,
        )

        print("OLLAMA RAW RESPONSE:", r.text)

        resp = r.json()
        return {"reply": resp.get("response", "")}
    except Exception as e:
        print("ERROR in /api/generate:", e)
        return {"reply": "Error contacting model."}

# ------------------------------------------------------------
# RAG SAFE WRAPPER
# ------------------------------------------------------------

def call_rag_server_safe(query: str, session_id: str) -> str | None:
    try:
        rag_cfg = config.get("rag", {})
        resp = requests.post(
            rag_cfg["url"],
            json={"query": query, "session": session_id},
            timeout=2,
        )
        data = resp.json()
        return data.get("augmented_prompt")
    except Exception as e:
        print("RAG unavailable:", e)
        return None

# ------------------------------------------------------------
# REASONING MODULE
# ------------------------------------------------------------
def run_reasoning_module(user_message: str) -> dict:
    try:
        payload = {
            "model": config["backend"]["reasoning_model"],
            "prompt": f"{REASONING_PROMPT}\nUser message: {user_message}\nJSON:",
            "stream": False,
        }

        r = requests.post(
            f"{config['backend']['ollama_url']}/api/generate",
            json=payload,
        )

        raw = r.json().get("response", "").strip()
        print("RAW REASONING OUTPUT:", raw)

        # Try to extract JSON substring
        start = raw.find("{")
        end = raw.rfind("}")

        if start != -1 and end != -1:
            cleaned = raw[start:end+1]
            try:
                return json.loads(cleaned)
            except:
                pass

        print("Reasoning JSON malformed, using fallback.")
        return {
            "thought": f"Fallback reasoning for: {user_message}",
            "intent": "unknown",
            "plan": ["No plan — fallback."],
            "decision": "none",
        }

    except Exception as e:
        print("Reasoning module error:", e)
        return {
            "thought": f"Fallback reasoning for: {user_message}",
            "intent": "unknown",
            "plan": ["No plan — fallback."],
            "decision": "none",
        }


# ------------------------------------------------------------
# DECISION ROUTER
# ------------------------------------------------------------

def route_decision(reasoning: dict) -> str:
    intent = reasoning.get("intent", "unknown")
    decision = reasoning.get("decision", "none")

    if decision == "respond":
        return f"Agent would respond normally (intent: {intent})."

    if decision == "call_tool":
        return f"Agent would call a tool (intent: {intent})."

    return f"No action taken (intent: {intent})."

# ------------------------------------------------------------
# INTENT EXTRACTION FOR WEB
# ------------------------------------------------------------

async def run_intent_extraction(messages: list) -> dict | None:
    try:
        payload = {
            "model": config["backend"]["model"],
            "prompt": json.dumps(messages),
            "stream": False,
        }

        r = requests.post(
            f"{config['backend']['ollama_url']}/api/generate",
            json=payload,
        )

        raw = r.json().get("response", "").strip()
        if raw.startswith("{") and raw.endswith("}"):
            return json.loads(raw)

        return None
    except Exception as e:
        print("Intent extraction error:", e)
        return None

# ------------------------------------------------------------
# SIMPLE OLLAMA CHAT WRAPPER FOR CONTINUATION
# ------------------------------------------------------------

class SimpleOllamaChat:
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    async def stream(self, messages: list, on_token):
        payload = {
            "model": self.model,
            "prompt": json.dumps(messages),
            "stream": True,
        }

        r = requests.post(
            f"{self.url}/api/generate",
            json=payload,
            stream=True,
        )

        for line in r.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
            except Exception:
                continue

            token = chunk.get("response", "")
            if token:
                on_token(token)

# ------------------------------------------------------------
# CHAT WEBSOCKET
# ------------------------------------------------------------

@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    model_name = config["backend"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    ollama_client = SimpleOllamaChat(
        config["backend"]["ollama_url"],
        model_name,
    )

    try:
        await ws.send_json(
            {
                "session": session_id,
                "reply": "Connected. Ask me anything.",
                "reasoning": {
                    "thought": "Session initialized.",
                    "intent": "none",
                    "plan": [],
                    "decision": "none",
                },
                "stream": False,
            }
        )

        while True:
            data = await ws.receive_json()
            text = data.get("text", "")

            reasoning = run_reasoning_module(text)
            decision_result = route_decision(reasoning)

            conversations[session_id].append({"role": "user", "content": text})

            # ------------------------------------------------------------
            # INTENT EXTRACTION + TOOL PIPELINE
            # ------------------------------------------------------------
            intent_messages = [
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ]

            intent_json = await run_intent_extraction(intent_messages)

            if intent_json and "intent" in intent_json:
                tool_name, tool_args = route_intent(intent_json, text)

                if tool_name != "chat_tool":
                    await ws.send_json(
                        {
                            "session": session_id,
                            "tool_call": {
                                "name": tool_name,
                                "args": tool_args,
                            },
                            "stream": False,
                        }
                    )

                    tool_results = await execute_tool(
                        tool_name,
                        tool_args,
                        config=config,
                        mcp_client=None,
                    )

                    await ws.send_json(
                        {
                            "session": session_id,
                            "tool_results": tool_results,
                            "stream": False,
                        }
                    )

                    async def ws_append_fn(token: str):
                        await ws.send_json(
                            {
                                "session": session_id,
                                "reply": token,
                                "stream": True,
                            }
                        )

                    continuation = await continue_llm_with_tool_results(
                        llm=ollama_client,
                        tool_name=tool_name,
                        results=tool_results,
                        append_fn=lambda t: asyncio.create_task(ws_append_fn(t)),
                        stream_to_terminal=False,
                        tts=None,
                    )

                    await ws.send_json(
                        {
                            "session": session_id,
                            "reply": continuation,
                            "reasoning": reasoning,
                            "decision_result": decision_result,
                            "stream": False,
                        }
                    )

                    conversations[session_id].append(
                        {"role": "assistant", "content": continuation}
                    )

                    continue

            # ------------------------------------------------------------
            # RAG + NORMAL LLM PATH
            # ------------------------------------------------------------
            augmented_prompt = call_rag_server_safe(text, session_id)

            if augmented_prompt:
                prompt_to_llm = augmented_prompt
            else:
                transcript = personality_prompt.strip() + "\n\n"
                for m in conversations[session_id]:
                    transcript += f"{m['role'].capitalize()}: {m['content']}\n"
                transcript += "Assistant:"
                prompt_to_llm = transcript

            payload = {
                "model": model_name,
                "prompt": prompt_to_llm,
                "stream": True,
            }

            try:
                r = requests.post(
                    f"{config['backend']['ollama_url']}/api/generate",
                    json=payload,
                    stream=True,
                )

                full_reply = ""

                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                    except Exception:
                        continue

                    token = chunk.get("response", "")
                    if not token:
                        continue

                    full_reply += token
                    await ws.send_json(
                        {
                            "session": session_id,
                            "reply": token,
                            "stream": True,
                        }
                    )

                conversations[session_id].append(
                    {"role": "assistant", "content": full_reply}
                )

                await ws.send_json(
                    {
                        "session": session_id,
                        "reply": full_reply,
                        "reasoning": reasoning,
                        "decision_result": decision_result,
                        "stream": False,
                    }
                )

            except Exception as e:
                print("ERROR in /ws/chat:", e)
                await ws.send_json(
                    {
                        "session": session_id,
                        "reply": "Error contacting model.",
                        "stream": False,
                    }
                )

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversations.pop(session_id, None)
