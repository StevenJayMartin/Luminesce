# lumin/tools/chat_tool.py

def chat_tool(message: str = "", config=None):
    """
    Conversational small-talk tool.
    Handles greetings, introductions, jokes, casual questions,
    and general chit-chat. Returns the user's message so the
    continuation prompt can generate a natural reply.
    """
    if not message:
        return {"response": "Hello! How can I help you today?"}

    return {"response": message}
