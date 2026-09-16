from lumin.tools.registry import get

def run_agent(reasoning: dict, user_message: str, config=None):
    intent = reasoning.get("intent", "")
    tool = get(intent)

    if not tool:
        return {"tool_result": None}

    try:
        # Some tools expect (query), some expect (query, config)
        if config:
            result = tool(user_message, config)
        else:
            result = tool(user_message)

        return {"tool_result": result}
    except Exception as e:
        return {"tool_result": {"error": str(e)}}

