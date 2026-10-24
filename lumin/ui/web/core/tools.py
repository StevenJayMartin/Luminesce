import json
import uuid
import requests
from lumin.tools.registry import get as get_tool

async def execute_tool(name: str, args: dict, config: dict):
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

async def continue_llm_with_tool_results(config: dict, tool_name: str, results: dict):
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
        r = requests.post(f"{config['ollama']['url']}/api/generate", json=payload)
        return r.json().get("response", "")
    except Exception:
        return "Error contacting model."

