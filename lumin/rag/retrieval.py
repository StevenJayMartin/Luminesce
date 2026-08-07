from .vector_store import search_vectors


def build_augmented_prompt(query: str):
    """
    Build RAG prompt with retrieved context.
    """
    results = search_vectors(query, k=5)

    if not results:
        context = "(No context available.)"
    else:
        context = "\n\n".join([r["chunk"] for r in results])

    return f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}
""".strip()
