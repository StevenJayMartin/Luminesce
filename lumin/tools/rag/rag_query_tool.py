import httpx

class RagQueryTool:
    name = "rag_query"
    description = "Query the RAG subsystem for contextual retrieval."

    def __init__(self, config=None):
        # Use config.json if provided
        if config and "rag" in config and "url" in config["rag"]:
            # Full URL already includes /rag
            self.rag_url = config["rag"]["url"]
        else:
            # Fallback
            self.rag_url = "http://192.168.1.205:8001/rag"

    async def __call__(self, query: str, session: str = "default"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.rag_url,
                json={"query": query, "session": session},
                timeout=30.0
            )

        response.raise_for_status()
        return response.json()
