# lumin/tools/rag/rag_query_tool.py

import httpx

class RagQueryTool:
    """
    Query the RAG subsystem for answers using previously ingested documents.
    Use this tool when the user wants information retrieved from stored or indexed content.
    """
    name = "rag_query"
    description = "Query the RAG subsystem for contextual retrieval."

    def __init__(self, rag_url="http://localhost:8001"):
        self.rag_url = rag_url

    async def __call__(self, query: str, session: str = "default"):
        """
        Execute a RAG query by calling the RAG FastAPI server.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.rag_url}/rag",
                json={"query": query, "session": session},
                timeout=30.0
            )

        response.raise_for_status()
        return response.json()

