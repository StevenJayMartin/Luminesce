```
luminesce/
    __init__.py

    core/
        __init__.py
        intent.py
        entities.py
        state.py
        memory.py
        reasoning.py

    llm/
        __init__.py
        pipeline.py
        prompts.py

    ui/
        __init__.py
        web/
            __init__.py
            app.py
            websocket.py
            static/
            templates/

    api/
        __init__.py
        routes.py

    personality/
        __init__.py
        style.py
        behavior.py
        identity.py

    util/
        __init__.py
        logger.py
        config.py
        helpers.py
```
⭐ What each part does (and why it matters)
1. luminesce/core/ — The Cognitive Foundation
This is where Luminesce’s mind lives.

✔ intent.py
Classifies what the user is trying to do.

✔ entities.py
Extracts names, tasks, topics, references.

✔ state.py
Tracks the current conversation state.

✔ memory.py
Short‑term + long‑term memory.

✔ reasoning.py
Planning, multi‑step thinking, chain‑of‑thought.

This folder is the brainstem of Luminesce.

2. luminesce/llm/ — The Model Pipeline
This is where you interface with Ollama or any future model.

✔ pipeline.py
Handles message formatting, streaming, and model calls.

✔ prompts.py
Holds system prompts, personality prompts, and cognitive prompts.

This keeps your LLM logic clean and separate from your cognitive logic.

3. luminesce/ui/ — The Interface Layer
This is where your browser vs phone modes will live.

✔ web/app.py
Your FastAPI app.

✔ web/websocket.py
Your WebSocket message handler.

✔ web/static/
Your HTML/CSS/JS.

✔ web/templates/
Optional Jinja templates.

This is where Luminesce’s body lives.

4. luminesce/api/ — REST Endpoints
This is where you expose:

/talk

/stream

/settings

/memory

/intent

This keeps your API clean and separate from your UI.

5. luminesce/personality/ — The Soul
This is where Luminesce becomes someone, not something.

✔ style.py
Tone, pacing, warmth, humor.

✔ behavior.py
Conversational rules, emotional intelligence.

✔ identity.py
Name, role, mission, presence.

This is the layer that makes Luminesce feel like a colleague.

6. luminesce/util/ — Utilities
Everything that doesn’t belong in the cognitive or UI layers.

✔ logger.py
Unified logging.

✔ config.py
Settings, outputDestination, environment.

✔ helpers.py
Small reusable functions.

⭐ Why this architecture works
Because it separates Luminesce into layers of intelligence:

🧠 Mind → core/
🗣️ Voice → personality/
🧩 Reasoning → core/reasoning.py
🧬 Memory → core/memory.py
🖥️ Body → ui/web/
🔌 Interface → api/
⚙️ Engine → llm/
🛠️ Tools → util/
This is how real AI assistants are built.

It’s clean.
It’s scalable.
It’s future‑proof.
It’s beautiful.