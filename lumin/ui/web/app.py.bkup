import os
import json
import uuid
import requests
import subprocess
import re
import time
import math

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from lumin.tools.router import route_intent
from lumin.tools.registry import get as get_tool

# ------------------------------------------------------------
# PATHS / LIMITS
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
STATIC_PATH = os.path.join(BASE_DIR, "static")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "config.json")

MEMORY_TTL_SECONDS = 30 * 24 * 3600  # 30 days
MEMORY_MAX_ITEMS = 200

# ------------------------------------------------------------
# LOAD CONFIG.JSON
# ------------------------------------------------------------

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

PERSONALITY_DIR = os.path.join(os.path.dirname(CONFIG_PATH), "prompts")

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

MEMORY_CLASSIFIER_PROMPT = """
You are a memory classifier for a local AI assistant.

Classify the user's message into one of:
- "user_profile"  (identity facts: name, location, role)
- "preference"    (likes, dislikes, habits)
- "project"       (information about ongoing work or creative projects)
- "observation"   (general conversation, greetings, questions, small talk)

Respond ONLY with JSON:
{
  "type": "user_profile | preference | project | observation",
  "key": "short_key_or_null",
  "value": "short_value_or_original_text"
}
"""

# ------------------------------------------------------------
# PERSONALITIES / RAG
# ------------------------------------------------------------

def load_personality_prompt(model_name: str) -> str:
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})

    personality_name = model_map.get(model_name, "default")
    personality_path = personalities.get(personality_name)

    if not personality_path:
        return SYSTEM_PROMPT

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
# SEMANTIC MEMORY (embeddings only)
# ------------------------------------------------------------

EMBED_MEMORY_FILE = os.path.join(os.path.dirname(CONFIG_PATH), "embed_memory.json")


def load_embed_memory():
    try:
        with open(EMBED_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_embed_memory(mem):
    try:
        with open(EMBED_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2)
    except Exception as e:
        print("Error saving embed memory:", e)


def prune_embed_memory(mem):
    now = int(time.time())
    for sid, items in mem.items():
        items = [it for it in items if now - it.get("ts", now) <= MEMORY_TTL_SECONDS]
        if len(items) > MEMORY_MAX_ITEMS:
            items = items[-MEMORY_MAX_ITEMS:]
        mem[sid] = items
    return mem


embed_memory = load_embed_memory()  # { session_id: [ { "text": str, "embedding": [float], "ts": int } ] }

PROJECT_MEMORY_FILE = "project_memory.json"

def load_project_memory():
    if not os.path.exists(PROJECT_MEMORY_FILE):
        return {"projects": {}, "current_project": None}
    with open(PROJECT_MEMORY_FILE, "r") as f:
        return json.load(f)

def save_project_memory(pm):
    with open(PROJECT_MEMORY_FILE, "w") as f:
        json.dump(pm, f, indent=2)


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
            "mode": config["ollama"].get("mode", "chat"),
        },
        "ui": config.get("ui", {}).get("web", {}),
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
        "model_personality_map": model_map,
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

    try:
        r = requests.get(f"{config['ollama']['url']}/api/ps")
        ps = r.json()
        info["running"] = ps.get("models", [])
    except Exception as e:
        info["running_error"] = str(e)

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

    config["ollama"]["model"] = new_model

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print("ERROR writing config.json:", e)
        return {"ok": False, "error": str(e)}

    return {"ok": True, "model": new_model}

@app.get("/api/memory")
def get_memory():
    """
    Return all semantic memory for all sessions.
    The UI can decide how to display it.
    """
    try:
        return {"memory": embed_memory}
    except Exception as e:
        return {"memory": {}, "error": str(e)}

@app.get("/api/semantic-status")
def semantic_status():
    return semantic_memory_status()

@app.get("/api/memory/{session_id}")
def get_memory_for_session(session_id: str):
    mem = embed_memory.get(session_id)
    if not mem:
        return {"memory": [], "error": "Unknown session or no semantic memory"}
    return {"memory": mem}

@app.get("/api/project-memory")
def get_project_memory():
    return load_project_memory()

@app.post("/api/set-project")
def set_project(payload: dict):
    name = payload.get("name")
    if not name:
        return {"ok": False, "error": "Missing project name"}

    pm = load_project_memory()
    pm["current_project"] = name
    pm["projects"].setdefault(name, {
        "topics": [],
        "characters": [],
        "lore": [],
        "notes": []
    })
    save_project_memory(pm)
    return {"ok": True, "project": pm["projects"][name]}

@app.post("/api/project-note")
def add_project_note(payload: dict):
    text = payload.get("text")
    if not text:
        return {"ok": False, "error": "Missing text"}

    pm = load_project_memory()
    name = pm.get("current_project")
    if not name:
        return {"ok": False, "error": "No current project set"}

    proj = pm["projects"].setdefault(name, {
        "topics": [],
        "characters": [],
        "lore": [],
        "notes": []
    })
    proj["notes"].append(text)
    save_project_memory(pm)
    return {"ok": True}

# ------------------------------------------------------------
# UPLOAD + GENERATE (non-stream)
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

    model_name = config["ollama"]["model"]
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
            f"{config['ollama']['url']}/api/generate",
            json=payload,
        )

        resp = r.json()
        return {"reply": resp.get("response", "")}
    except Exception as e:
        print("ERROR in /api/generate:", e)
        return {"reply": "Error contacting model."}

# ------------------------------------------------------------
# REASONING / TOOLS
# ------------------------------------------------------------

def tolerant_json_extract(raw: str) -> dict | None:
    raw = raw.replace("```json", "").replace("```", "").strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1:
        return None
    if end == -1:
        raw = raw[start:] + "}"
    else:
        raw = raw[start : end + 1]

    raw = re.sub(r"//.*", "", raw)
    raw = re.sub(r"#.*", "", raw)
    raw = re.sub(r'"\s*\n\s*"(?=[a-zA-Z0-9_]+")', '",\n"', raw)
    raw = re.sub(r']\s*\n\s*"(?=[a-zA-Z0-9_]+")', '],\n"', raw)
    raw = re.sub(r",\s*}", "}", raw)

    try:
        return json.loads(raw)
    except Exception:
        return None

def sanitize_reasoning(parsed: dict, user_message: str) -> dict:
    thought = parsed.get("thought", "").strip()
    intent = parsed.get("intent", "").strip() or "none"
    plan = parsed.get("plan", [])
    decision = parsed.get("decision", "none")

    if not isinstance(plan, list):
        plan = []

    if decision == "call_tool":
        tool_keywords = ["search", "lookup", "find", "tool", "calculate", "run"]
        if not any(k in user_message.lower() for k in tool_keywords):
            decision = "respond"
            intent = "conversation"

    if decision not in ["none", "respond", "call_tool"]:
        decision = "none"

    memory_words = ["remember", "recall", "memory"]
    if any(w in thought.lower() for w in memory_words):
        decision = "respond"
        intent = "conversation"

    return {
        "thought": thought,
        "intent": intent,
        "plan": plan,
        "decision": decision,
    }

def run_reasoning_module(user_message: str) -> dict:
    try:
        payload = {
            "model": config["reasoning"]["model"],
            "prompt": f"{REASONING_PROMPT}\nUser message: {user_message}\nJSON:",
            "stream": False,
        }

        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload,
        )

        raw = r.json().get("response", "").strip()
        parsed = tolerant_json_extract(raw)
        if parsed is not None:
            parsed = sanitize_reasoning(parsed, user_message)

            conversation_keywords = [
                "how are",
                "hello",
                "hi",
                "hey",
                "good morning",
                "good evening",
                "what's up",
                "how is your day",
                "how are we",
            ]

            if any(k in user_message.lower() for k in conversation_keywords):
                parsed["decision"] = "respond"
                parsed["intent"] = "conversation"

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
        "decision": "none",
    }

def classify_memory(text: str) -> dict | None:
    try:
        payload = {
            "model": config["ollama"]["model"],
            "prompt": MEMORY_CLASSIFIER_PROMPT + "\nUser: " + text + "\nJSON:",
            "stream": False,
        }
        r = requests.post(f"{config['ollama']['url']}/api/generate", json=payload)
        raw = r.json().get("response", "").strip()
        parsed = tolerant_json_extract(raw)
        return parsed
    except Exception as e:
        print("Memory classifier error:", e)
        return None


def route_decision(reasoning: dict, user_message: str):
    decision = reasoning.get("decision", "none")
    if decision == "respond":
        return "respond"
    if decision == "call_tool":
        return "call_tool"
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
    prefix = f"### TOOL_EXECUTION_{uuid.uuid4()} ###\n"
    prompt = (
        prefix
        + f"Tool '{tool_name}' returned:\n"
        + f"{json.dumps(results, indent=2)}\n\n"
        + "Answer the user's question using this information."
    )
    payload = {
        "model": config["ollama"]["model"],
        "prompt": prompt,
        "stream": False,
    }
    try:
        r = requests.post(
            f"{config['ollama']['url']}/api/generate",
            json=payload,
        )
        return r.json().get("response", "")
    except Exception:
        return "Error contacting model."

# ------------------------------------------------------------
# MEMORY MANAGER - EMBEDDINGS HELPERS
# ------------------------------------------------------------

class MemoryManager:
    def __init__(self, embed_mem: dict):
        self.embed_mem = embed_mem

    def init_session(self, session_id: str):
        if session_id not in self.embed_mem:
            self.embed_mem[session_id] = []

    def add_item(
        self,
        session_id: str,
        *,
        type: str,
        key: str | None,
        value: str,
        text: str,
        importance: float = 0.5,
    ):
        emb = get_embedding(value)
        if emb is None:
            return

        item = {
            "id": str(uuid.uuid4()),
            "type": type,
            "key": key,
            "value": value,
            "text": text,
            "embedding": emb,
            "importance": importance,
            "ts": int(time.time()),
        }

        self.embed_mem.setdefault(session_id, []).append(item)
        self.embed_mem = prune_embed_memory(self.embed_mem)
        save_embed_memory(self.embed_mem)

    def recall(
        self,
        session_id: str,
        query: str,
        *,
        type: str | None = None,
        key: str | None = None,
        top_k: int = 5,
    ):
        emb_q = get_embedding(query)
        if emb_q is None:
            return []

        items = self.embed_mem.get(session_id, [])
        scored = []
        for item in items:
            if type and item.get("type") != type:
                continue
            if key and item.get("key") != key:
                continue

            emb = item.get("embedding")
            if not emb:
                continue

            score = cosine(emb_q, emb) * (1.0 + item.get("importance", 0.0))
            scored.append((score, item))

        scored.sort(reverse=True)
        return [it for _, it in scored[:top_k]]


memory_manager = MemoryManager(embed_memory)

def get_embedding(text: str) -> list | None:
    try:
        payload = {
            "model": config["ollama"].get("embedding_model", config["ollama"]["model"]),
            "prompt": text,
            "stream": False,
        }
        r = requests.post(
            f"{config['ollama']['url']}/api/embeddings",
            json=payload,
        )
        return r.json().get("embedding")
    except Exception as e:
        print("Embedding error:", e)
        return None

def semantic_memory_status():
    model = config["ollama"].get("embedding_model")
    if not model:
        return {
            "active": False,
            "reason": "No embedding model configured",
            "model": None,
            "stored_items": 0,
        }

    # Try a tiny test embedding
    test_emb = get_embedding("test")
    if test_emb is None:
        return {
            "active": False,
            "reason": "Embedding model returned null",
            "model": model,
            "stored_items": 0,
        }

    stored_items = sum(len(v) for v in embed_memory.values())
    return {
        "active": True,
        "reason": None,
        "model": model,
        "stored_items": stored_items,
    }

def cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) + 1e-8
    )

def build_memory_context(session_id: str) -> str:
    items = memory_manager.recall(
        session_id,
        query="user info",
        top_k=10,
    )

    if not items:
        return ""

    lines = ["Memory:"]
    for item in items:
        t = item.get("type")
        k = item.get("key")
        v = item.get("value")
        if t == "user_profile" and k:
            lines.append(f"- {k}: {v}")
        elif t == "preference" and k:
            lines.append(f"- prefers {k}: {v}")
        elif t == "project" and k:
            lines.append(f"- project {k}: {v}")
        else:
            lines.append(f"- {item.get('text')}")

    return "\n".join(lines) + "\n\n"


# ------------------------------------------------------------
# CHAT WEBSOCKET (streaming, semantic memory only)
# ------------------------------------------------------------
@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    global embed_memory
    await ws.accept()

    session_id = str(uuid.uuid4())
    conversations[session_id] = []

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(model_name)

    def sanitize_reply(text: str) -> str:
        fallback_phrases = [
            "provide the context",
            "didn’t provide any context",
            "no context",
            "clarify the question",
        ]
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            if any(p in line.lower() for p in fallback_phrases):
                continue
            cleaned.append(line)
        return "\n".join(cleaned).strip()

    try:
        await ws.send_json({
            "session": session_id,
            "reply": "Connected. Ask me anything.",
            "reasoning": {
                "thought": "Session initialized.",
                "intent": "none",
                "plan": [],
                "decision": "none",
            },
            "decision_result": None,
            "stream": False,
        })

        while True:
            data = await ws.receive_json()
            text = data.get("text", "").strip()
            if not text:
                continue

            # ------------------------------------------------------------
            # STRUCTURED MEMORY WRITE (minimal)
            # ------------------------------------------------------------
            memory_manager.init_session(session_id)

            classified = classify_memory(text)
            if classified:
                m_type = classified.get("type", "observation")
                m_key = classified.get("key")
                m_value = classified.get("value") or text

                importance_map = {
                    "user_profile": 0.9,
                    "preference": 0.7,
                    "project": 0.7,
                    "observation": 0.2,
                }
                importance = importance_map.get(m_type, 0.2)

                memory_manager.add_item(
                    session_id,
                    type=m_type,
                    key=m_key,
                    value=m_value,
                    text=text,
                    importance=importance,
                )
            else:
                memory_manager.add_item(
                    session_id,
                    type="observation",
                    key=None,
                    value=text,
                    text=text,
                    importance=0.1,
                )

            # ------------------------------------------------------------
            # NAME RECALL (minimal)
            # ------------------------------------------------------------
            if "what is my name" in text.lower():
                conversations[session_id].append({"role": "user", "content": text})

                recalled = memory_manager.recall(
                    session_id,
                    query="user name",
                    type="user_profile",
                    key="name",
                    top_k=1,
                )

                if recalled:
                    name_value = recalled[0].get("value", "").strip()
                    reply = f"Your name is {name_value}."
                else:
                    reply = (
                        "I’m not confident I know your name yet. "
                        "You can tell me by saying: 'My name is ...'."
                    )

                conversations[session_id].append({"role": "assistant", "content": reply})

                await ws.send_json({
                    "session": session_id,
                    "reply": reply,
                    "reasoning": {
                        "thought": "Recalled name from structured memory",
                        "intent": "recall_name_structured",
                        "plan": [],
                        "decision": "memory_read",
                    },
                    "decision_result": None,
                    "stream": False,
                })
                continue

            # ------------------------------------------------------------
            # NORMAL CHAT PATH WITH MEMORY CONTEXT
            # ------------------------------------------------------------
            conversations[session_id].append({"role": "user", "content": text})

            memory_context = build_memory_context(session_id)

            transcript = (
                personality_prompt.strip()
                + "\n\n"
                + memory_context
                + "Conversation:\n"
            )
            for m in conversations[session_id][-8:]:
                transcript += f"{m['role'].capitalize()}: {m['content']}\n"
            transcript += "Assistant:"

            payload = {
                "model": model_name,
                "prompt": transcript,
                "stream": True,
            }

            try:
                r = requests.post(
                    f"{config['ollama']['url']}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=300,
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
                        "reasoning": None,
                        "decision_result": None,
                        "stream": True,
                    })

                clean_reply = sanitize_reply(full_reply)
                conversations[session_id].append({"role": "assistant", "content": clean_reply})

                await ws.send_json({
                    "session": session_id,
                    "reply": "",
                    "reasoning": None,
                    "decision_result": None,
                    "stream": False,
                })

            except Exception as e:
                print("ERROR in /ws/chat:", e)
                await ws.send_json({
                    "session": session_id,
                    "reply": "Error contacting model.",
                    "reasoning": None,
                    "decision_result": None,
                    "stream": False,
                })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversations.pop(session_id, None)
