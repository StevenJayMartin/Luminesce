from .embeddings import embed
from .vector_store import search_vectors


def build_augmented_prompt(query: str) -> str:
    """
    Embed the query, retrieve relevant docs, and build an augmented prompt.
    """
    qvec = embed(query)
    context_chunks = search_vectors(qvec, k=3)
    context = "\n\n".join(context_chunks) if context_chunks else "(No context available.)"

    prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}
"""
    return prompt.strip()

