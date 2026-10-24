import os

SYSTEM_PROMPT = """
You are Lumin, a local, privacy-first, Markdown-fluent AI assistant.
You respond with well-structured Markdown, using headings, lists, and code blocks when helpful.
You are concise, friendly, and practical.
"""

def load_personality_prompt(config: dict, prompts_dir: str, model_name: str) -> str:
    personalities = config.get("personalities", {})
    model_map = config.get("model_personality_map", {})
    personality_name = model_map.get(model_name, "default")
    personality_path = personalities.get(personality_name)

    if not personality_path:
        return SYSTEM_PROMPT

    full_path = os.path.join(prompts_dir, personality_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return SYSTEM_PROMPT

