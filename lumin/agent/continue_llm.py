# lumin/agent/continue_llm.py

import json
from lumin.tools.prompts import TOOL_PROMPTS, DEFAULT_TOOL_PROMPT


async def continue_llm_with_tool_results(llm, tool_name, results, append_fn, stream_to_terminal, tts):
    tool_prompt = TOOL_PROMPTS.get(tool_name, DEFAULT_TOOL_PROMPT)

    messages = [
        {"role": "system", "content": tool_prompt},
        {
            "role": "user",
            "content": (
                f"Tool '{tool_name}' returned:\n"
                f"{json.dumps(results, indent=2)}\n\n"
                "Please answer the user's question using this information."
            ),
        },
    ]

    append_fn("Lumin: ")

    response_parts = []

    def on_token(token: str):
        response_parts.append(token)
        append_fn(token)

        if stream_to_terminal:
            import sys
            sys.__stdout__.write(token)
            sys.__stdout__.flush()

    try:
        await llm.stream(messages, on_token)
    except StopIteration:
        pass

    full_response = "".join(response_parts).strip()
    append_fn("\n")

    if tts and full_response:
        import threading
        threading.Thread(target=tts.speak, args=(full_response,), daemon=True).start()

    return full_response
