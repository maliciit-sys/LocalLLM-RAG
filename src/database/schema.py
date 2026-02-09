"""
Database schema definitions for the LocalLLM-RAG project.
Creates and manages PostgreSQL tables with pgvector support.
"""

from sqlalchemy import text
from src.database.connection import get_shared_engine


def create_tables():
    """Create all database tables with pgvector extension."""
    engine = get_shared_engine()

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        conn.execute(text("DROP TABLE IF EXISTS reviews CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))

        conn.execute(text("""
            CREATE TABLE products (
                product_id VARCHAR(20) PRIMARY KEY,
                review_count INTEGER DEFAULT 0,
                avg_score NUMERIC(3,2) DEFAULT 0
            );
        """))

        conn.execute(text("""
            CREATE TABLE users (
                user_id VARCHAR(50) PRIMARY KEY,
                profile_name VARCHAR(255)
            );
        """))

        conn.execute(text("""
            CREATE TABLE reviews (
                id SERIAL PRIMARY KEY,
                original_id INTEGER,
                product_id VARCHAR(20) REFERENCES products(product_id),
                user_id VARCHAR(50) REFERENCES users(user_id),
                helpfulness_numerator INTEGER,
                helpfulness_denominator INTEGER,
                score INTEGER,
                review_time BIGINT,
                summary TEXT,
                review_text TEXT,
                embedding vector(384)
            );
        """))

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_score ON reviews(score);"))

        conn.commit()

    print("✅ Database schema created successfully!")


def create_vector_index():
    """Create HNSW index for fast vector similarity search."""
    engine = get_shared_engine()

    with engine.connect() as conn:
        conn.execute(text("DROP INDEX IF EXISTS idx_reviews_embedding;"))
        conn.execute(text("""
            CREATE INDEX idx_reviews_embedding
            ON reviews
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))
        conn.commit()

    print("✅ HNSW vector index created!")


def get_stats() -> dict:
    """Get database statistics."""
    engine = get_shared_engine()

    with engine.connect() as conn:
        stats = {}
        for table in ["products", "users", "reviews"]:
            stats[table] = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        stats["embedded"] = conn.execute(
            text("SELECT COUNT(*) FROM reviews WHERE embedding IS NOT NULL")
        ).scalar()

    return stats


if __name__ == "__main__":
    create_tables()
    print(get_stats())
