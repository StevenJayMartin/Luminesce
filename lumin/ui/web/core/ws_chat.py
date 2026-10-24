import json
import uuid
import requests
from fastapi import WebSocket, WebSocketDisconnect
from .personality import load_personality_prompt
from .classifier import classify_memory
from .reasoning import run_reasoning_module
from .semantic_memory import LuminSemanticMemory
from lumin.ui.web.models.state import conversations

async def chat_ws(
    ws: WebSocket,
    config: dict,
    paths: dict,
    semantic_memory: LuminSemanticMemory,
):
    await ws.accept()

    session_id = str(uuid.uuid4())
    conversations[session_id] = []
    semantic_memory.init_session(session_id)

    model_name = config["ollama"]["model"]
    personality_prompt = load_personality_prompt(config, paths["prompts"], model_name)

    await ws.send_json({
        "session": session_id,
        "reply": "Connected. Ask me anything.",
        "reasoning": {"thought": "Session initialized.", "intent": "none", "plan": [], "decision": "none"},
        "stream": False,
    })

    try:
        while True:
            data = await ws.receive_json()
            text = data.get("text", "").strip()
            if not text:
                continue

            classified = classify_memory(config, text)
            if classified:
                semantic_memory.add(
                    session_id,
                    type=classified.get("type", "observation"),
                    key=classified.get("key"),
                    value=classified.get("value") or text,
                    text=text,
                )
            else:
                semantic_memory.add(
                    session_id,
                    type="observation",
                    key=None,
                    value=text,
                    text=text,
                )

            if "what is my name" in text.lower():
                conversations[session_id].append({"role": "user", "content": text})
                recalled = semantic_memory.recall(
                    session_id,
                    query="user name",
                    type="user_profile",
                    key="name",
                    top_k=1,
                )
                if recalled:
                    reply = f"Your name is {recalled[0]['value']}."
                else:
                    reply = "I’m not confident I know your name yet."
                conversations[session_id].append({"role": "assistant", "content": reply})
                await ws.send_json({
                    "session": session_id,
                    "reply": reply,
                    "reasoning": {"thought": "Name recall", "intent": "recall_name", "plan": [], "decision": "respond"},
                    "stream": False,
                })
                continue

            conversations[session_id].append({"role": "user", "content": text})
            memory_context = semantic_memory.build_context(session_id)

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
                        "stream": True,
                    })

                conversations[session_id].append({"role": "assistant", "content": full_reply})
                await ws.send_json({
                    "session": session_id,
                    "reply": "",
                    "reasoning": None,
                    "stream": False,
                })

            except Exception:
                await ws.send_json({
                    "session": session_id,
                    "reply": "Error contacting model.",
                    "stream": False,
                })

    except WebSocketDisconnect:
        pass
    finally:
        conversations.pop(session_id, None)

