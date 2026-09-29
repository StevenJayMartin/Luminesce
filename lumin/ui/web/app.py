import os
import json
import uuid
import requests
import subprocess

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from lumin.tools.router import route_intent
from lumin.tools.registry import get as get_tool

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
            "url": config["ollama"]["url"],
            "model": config["ollama"]["model"],
            "mode": config["ollama"].get("mode", "chat")
        },
        #- sjm 092626"ui": config["ui"]
        "ui": config.get("ui", {}).get("web", {})
    }

@app.get("/api/personalities")
def list_personalities():
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})
    current_model = config["ollama"]["model"]
    current_personality = model_map.get(current_model, "default")

    personality_list = [
        {"id": name, "name": name.capitalize()}
        for name in personalities.keys()
    ]

    return {
        "personalities": personality_list,
        "current_model": current_model,
        "current_personality": current_personality,
        "model_personality_map": model_map
    }

@app.post("/api/set-personality")
async def set_personality(req: dict):
    model_name = req.get("model") or config["ollama"]["model"]
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
        r = requests.get(f"{config['ollama']['url']}/api/tags")
        data = r.json()
        models = [m.get("name") for m in data.get("models", [])]
        return {"models": models}
    except Exception as e:
        print("ERROR in /api/models:", e)
        return {"models": [], "error": str(e)}
    
@app.get("/api/model-info")
def model_info():
    info = {
        "model": config["ollama"]["model"],
        "backend": config["ollama"]["url"],
    }

    # Ollama ps
    try:
        r = requests.get(f"{config['ollama']['url']}/api/ps")
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

    # update in-memory config
    config["ollama"]["model"] = new_model

    # write back to config.json
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

Decision rules:
- If the user asks for weather, set "decision": "call_tool" and "intent": "get_weather".
- If the user asks for information requiring external lookup (weather, facts, search queries), set "decision": "call_tool".
- If the user asks for anything requiring a tool, ALWAYS choose "call_tool".
- Only choose "respond" for purely conversational or opinion questions.

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

from fastapi import UploadFile, File


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read raw bytes
    raw = await file.read()

    # Try to decode as UTF‑8 text
    try:
        text = raw.decode("utf-8")
        decoded = True
    except:
        decoded = False
        text = None

    # Determine active session
    # If your chat system uses a session ID, retrieve it here.
    # If not, fall back to a single global session.
    session_id = "default"
    if session_id not in conversations:
        conversations[session_id] = []

    # Store file content in conversation history
    if decoded:
        conversations[session_id].append({
            "role": "user",
            "content": f"[Uploaded file: {file.filename}]\n{text}"
        })
    else:
        conversations[session_id].append({
            "role": "user",
            "content": (
                f"[Uploaded file: {file.filename} — binary data, {len(raw)} bytes]"
            )
        })

    # Build assistant reply
    if decoded:
        preview = text[:500]  # prevent flooding the chat
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

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    #- prompt = f"{personality_prompt.strip()}\n\nUser: {text}\nAssistant:"
    session_id = "default"
    if session_id not in conversations:
        conversations[session_id] = []

    # Store the new user message
    conversations[session_id].append({"role": "user", "content": text})

    # Build transcript
    transcript = personality_prompt.strip() + "\n\n"
    for m in conversations[session_id]:
        transcript += f"{m['role'].capitalize()}: {m['content']}\n"
    transcript += "Assistant:"

    prompt = transcript

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload
        )

        print("OLLAMA RAW RESPONSE:", r.text)

        resp = r.json()
        return {"reply": resp.get("response", "")}

    except Exception as e:
        print("ERROR in /api/generate:", e)
        return {"reply": "Error contacting model."}

# ------------------------------------------------------------
# CHAT WEBSOCKET (streaming, Markdown-aware)
# ------------------------------------------------------------

conversations = {}

def call_rag_server_safe(query: str, session_id: str) -> str | None:
    """
    Safe RAG call — returns None if RAG server is offline or errors.
    """
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

import re

def tolerant_json_extract(raw: str) -> dict:
    """
    Extracts and repairs malformed JSON from LLM output.
    Handles:
    - missing closing brace
    - missing commas between fields
    - trailing commas
    - extra text before/after JSON
    - markdown fences
    - comments
    """

    # Strip markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Extract the first {...} block
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1:
        return None
    if end == -1:
        # Missing closing brace → add one
        raw = raw[start:] + "}"
    else:
        raw = raw[start:end+1]

    # Remove comments
    raw = re.sub(r"//.*", "", raw)
    raw = re.sub(r"#.*", "", raw)

    # Fix missing commas between fields:
    # "value"\n  "next_key":
    raw = re.sub(r'"\s*\n\s*"(?=[a-zA-Z0-9_]+")', '",\n"', raw)

    # Fix missing commas after arrays
    raw = re.sub(r']\s*\n\s*"(?=[a-zA-Z0-9_]+")', '],\n"', raw)

    # Fix trailing commas before closing brace
    raw = re.sub(r',\s*}', '}', raw)

    try:
        return json.loads(raw)
    except Exception:
        return None

def sanitize_reasoning(parsed: dict) -> dict:
    # Ensure required keys exist
    thought = parsed.get("thought", "").strip()
    intent = parsed.get("intent", "").strip()
    plan = parsed.get("plan", [])
    decision = parsed.get("decision", "none")

    # Fix empty intent
    if intent == "":
        intent = "none"

    # Fix malformed plan
    if not isinstance(plan, list):
        plan = []

    # Fix invalid decision
    if decision not in ["none", "respond", "call_tool"]:
        decision = "none"

    # --- NEW: memory-related messages should be conversational ---
    memory_words = ["remember", "recall", "memory"]
    if any(w in thought.lower() for w in memory_words):
        decision = "respond"
        intent = "conversation"

    return {
        "thought": thought,
        "intent": intent,
        "plan": plan,
        "decision": decision
    }


def run_reasoning_module(user_message: str) -> dict:
    try:
        payload = {
            "model": config["reasoning"]["model"],
            "prompt": f"{REASONING_PROMPT}\nUser message: {user_message}\nJSON:",
            "stream": False
        }

        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload
        )

        raw = r.json().get("response", "").strip()

        print("RAW REASONING OUTPUT:", raw)

        # Extract JSON substring
        parsed = tolerant_json_extract(raw)
        if parsed is not None:
            parsed = sanitize_reasoning(parsed)

            # --- NEW: conversational override based on user message ---
            conversation_keywords = [
                "how are", "hello", "hi", "hey", "good morning", "good evening",
                "what's up", "how is your day", "how are we"
            ]

            if any(k in user_message.lower() for k in conversation_keywords):
                parsed["decision"] = "respond"
                parsed["intent"] = "conversation"

            # --- NEW: global fallback override ---
            # If the reasoning module can't classify the message,
            # treat it as normal conversation instead of "no context".
            if parsed["decision"] == "none":
                parsed["decision"] = "respond"
                parsed["intent"] = "conversation"

            return parsed
           
    except Exception as e:
        print("Reasoning module error:", e)
        return {
            "thought": f"Fallback reasoning for: {user_message}",
            "intent": "unknown",
            "plan": ["No plan — fallback."],
            "decision": "none"
        }

# ------------------------------------------------------------
# DECISION ROUTER (Non-action version)
# ------------------------------------------------------------

def route_decision(reasoning: dict, user_message: str):
    decision = reasoning.get("decision", "none")
    intent = reasoning.get("intent", "conversation")

    # If the agent should respond normally, do nothing.
    if decision == "respond":
        return "respond"

    # If the agent should call a tool, signal that.
    if decision == "call_tool":
        return "call_tool"

    # Fallback: treat as normal conversation
    return "respond"

async def execute_tool(name, args):
    import inspect
    tool = get_tool(name)
    if not tool:
        return {"error": f"Unknown tool '{name}'"}

    try:
        
        if inspect.iscoroutinefunction(tool.__call__):
            return await tool(**args)
        return tool(config=config, **args)
        
    except Exception as e:
        return {"error": str(e)}

async def continue_llm_with_tool_results(tool_name, results):
       
    import uuid

    prefix = f"### TOOL_EXECUTION_{uuid.uuid4()} ###\n"
    prompt = (
        prefix +
        f"Tool '{tool_name}' returned:\n"
        f"{json.dumps(results, indent=2)}\n\n"
        "Answer the user's question using this information."
    )
    
    payload = {
        "model": config["ollama"]["model"],
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload
        )
        return r.json().get("response", "")
    except Exception:
        return "Error contacting model."

@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    try:
        
        await ws.send_json({
            "session": session_id,
            "reply": "Connected. Ask me anything.",
            "reasoning": {"thought": "Session initialized.", "intent": "none", "plan": [], "decision": "none"},
            "stream": False
        })

        while True:
            data = await ws.receive_json()
            text = data.get("text", "")
            reasoning = run_reasoning_module(text)
            decision_result = route_decision(reasoning, text)          

            response_sent = False   # <-- ADD THIS

            if reasoning.get("decision") == "call_tool":
                intent_json = reasoning
                tool_name, tool_args = route_intent(intent_json, text)

                results = await execute_tool(tool_name, tool_args)
                reply = await continue_llm_with_tool_results(tool_name, results)

                await ws.send_json({
                    "session": session_id,
                    "reply": reply,
                    "reasoning": reasoning,
                    "decision_result": decision_result,
                    "stream": False
                })

                response_sent = True   # <-- ADD THIS
                continue

            # Store user message
            conversations[session_id].append({"role": "user", "content": text})

            # ------------------------------------------------------------
            # TRY RAG AUGMENTATION
            # ------------------------------------------------------------
            augmented_prompt = call_rag_server_safe(text, session_id)

            if augmented_prompt:
                # Use RAG prompt
                prompt_to_llm = augmented_prompt
            else:
                # Fall back to your existing transcript behavior
                transcript = personality_prompt.strip() + "\n\n"
                for m in conversations[session_id]:
                    transcript += f"{m['role'].capitalize()}: {m['content']}\n"
                transcript += "Assistant:"
                prompt_to_llm = transcript

            payload = {
                "model": model_name,
                "prompt": prompt_to_llm,
                "stream": True
            }

            try:
                r = requests.post(
                    f"{config['ollama']['url']}/api/generate",
                    json=payload,
                    stream=True
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
                    await ws.send_json({
                        "session": session_id,
                        "reply": token,
                        "stream": True
                    })
                    response_sent = True   # no dup responses
                    
                conversations[session_id].append({
                    "role": "assistant",
                    "content": full_reply
                })

                if not response_sent:
                    await ws.send_json({
                        "session": session_id,
                        "reply": full_reply,
                        "reasoning": reasoning,
                        "decision_result": decision_result,
                        "stream": False
                    })

            except Exception as e:
                print("ERROR in /ws/chat:", e)
                await ws.send_json({
                    "session": session_id,
                    "reply": "Error contacting model.",
                    "stream": False
                })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversations.pop(session_id, None)
