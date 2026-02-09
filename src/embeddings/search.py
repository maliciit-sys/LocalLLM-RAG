"""
Vector similarity search using pgvector.
"""

from src.embeddings.generator import get_embedding_generator
from src.database.queries import search_similar_reviews


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Perform semantic search: encode query → pgvector similarity search.

    Args:
        query: Natural language search query
        top_k: Number of results to return

    Returns:
        List of review dicts sorted by similarity
    """
    generator = get_embedding_generator()
    query_embedding = generator.encode_query(query)
    return search_similar_reviews(query_embedding, top_k=top_k)
