"""
Common database queries for the RAG pipeline.
"""

from sqlalchemy import text
from src.database.connection import get_shared_engine


def search_similar_reviews(query_embedding: list, top_k: int = 5) -> list[dict]:
    """
    Find the most similar reviews using pgvector cosine similarity.

    Args:
        query_embedding: List of floats (384 dimensions)
        top_k: Number of results to return

    Returns:
        List of review dicts with similarity scores
    """
    engine = get_shared_engine()

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                r.id,
                r.summary,
                r.score,
                r.review_text,
                r.helpfulness_numerator,
                r.helpfulness_denominator,
                p.product_id,
                1 - (r.embedding <=> CAST(:query_emb AS vector)) as similarity
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.embedding IS NOT NULL
            ORDER BY r.embedding <=> CAST(:query_emb AS vector)
            LIMIT :top_k
        """), {"query_emb": str(query_embedding), "top_k": top_k})

        columns = ["id", "summary", "score", "review_text", "helpfulness_num",
                    "helpfulness_den", "product_id", "similarity"]

        return [dict(zip(columns, row)) for row in result]


def get_review_count() -> int:
    """Get total number of reviews."""
    engine = get_shared_engine()
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar()


def get_embedded_count() -> int:
    """Get number of reviews with embeddings."""
    engine = get_shared_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT COUNT(*) FROM reviews WHERE embedding IS NOT NULL")
        ).scalar()


def get_reviews_without_embeddings(batch_size: int = 1000) -> list[tuple]:
    """Fetch reviews that need embeddings generated."""
    engine = get_shared_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, COALESCE(summary, '') || ' ' || COALESCE(review_text, '') as combined_text
            FROM reviews
            WHERE embedding IS NULL
            ORDER BY id
            LIMIT :batch_size
        """), {"batch_size": batch_size})
        return result.fetchall()


def update_embedding(review_id: int, embedding: list):
    """Update a single review's embedding."""
    engine = get_shared_engine()
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE reviews SET embedding = :emb WHERE id = :id"),
            {"emb": str(embedding), "id": review_id}
        )
        conn.commit()
