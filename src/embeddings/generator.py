"""
Embedding generation and management.
Handles model loading, batch generation, and storage.
"""

import torch
import time
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from src.database.connection import get_shared_engine
from src.utils.config import config


class EmbeddingGenerator:
    """Manages embedding model and generation."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_name = config.embedding.model_name
        self.dimension = config.embedding.dimension
        self.batch_size = config.embedding.batch_size

    def load_model(self):
        """Load the sentence transformer model."""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"✅ Model loaded on {self.device} (dim={self.dimension})")
        return self.model

    def encode(self, texts: list[str], normalize: bool = True) -> list:
        """Encode texts into embeddings."""
        model = self.load_model()
        return model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        )

    def encode_query(self, query: str) -> list:
        """Encode a single query and return as list."""
        embedding = self.encode([query], normalize=True)[0]
        return embedding.tolist()

    def generate_all_embeddings(self):
        """Generate embeddings for all reviews missing them."""
        model = self.load_model()
        engine = get_shared_engine()

        # Fetch all reviews without embeddings
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, COALESCE(summary, '') || ' ' || COALESCE(review_text, '') as combined_text
                FROM reviews
                WHERE embedding IS NULL
                ORDER BY id
            """))
            rows = result.fetchall()

        total = len(rows)
        if total == 0:
            print("✅ All reviews already have embeddings!")
            return

        ids = [row[0] for row in rows]
        texts = [row[1] for row in rows]

        print(f"Generating embeddings for {total:,} reviews...")
        start_time = time.time()
        processed = 0

        for i in range(0, total, self.batch_size):
            batch_ids = ids[i:i + self.batch_size]
            batch_texts = texts[i:i + self.batch_size]

            embeddings = model.encode(
                batch_texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
            )

            with engine.connect() as conn:
                for review_id, embedding in zip(batch_ids, embeddings):
                    conn.execute(
                        text("UPDATE reviews SET embedding = :emb WHERE id = :id"),
                        {"emb": str(embedding.tolist()), "id": review_id}
                    )
                conn.commit()

            processed += len(batch_ids)
            elapsed = time.time() - start_time
            rate = processed / elapsed
            remaining = (total - processed) / rate if rate > 0 else 0

            if (i // self.batch_size) % 10 == 0 or processed == total:
                print(f"  {processed:,}/{total:,} ({processed/total*100:.1f}%) | "
                      f"{rate:.0f} reviews/sec | ETA: {remaining/60:.1f}min")

        total_time = time.time() - start_time
        print(f"\n✅ Done! {total:,} embeddings in {total_time/60:.1f}min ({total/total_time:.0f}/sec)")


# Singleton instance
_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the singleton EmbeddingGenerator."""
    global _generator
    if _generator is None:
        _generator = EmbeddingGenerator()
    return _generator
