"""
Configuration loader for the project.
Reads from .env file and provides typed access to settings.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    user: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
    name: str = ""

    def __post_init__(self):
        self.user = os.getenv("DB_USER", "llmuser")
        self.password = os.getenv("DB_PASS", "")
        self.host = os.getenv("DB_HOST", "127.0.0.1")
        self.port = os.getenv("DB_PORT", "5432")
        self.name = os.getenv("DB_NAME", "llmdb")


@dataclass
class OllamaConfig:
    host: str = ""
    model: str = ""

    def __post_init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")


@dataclass
class EmbeddingConfig:
    model_name: str = ""
    dimension: int = 384
    batch_size: int = 512

    def __post_init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        self.batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "512"))


@dataclass
class RAGConfig:
    top_k: int = 5
    similarity_threshold: float = 0.3

    def __post_init__(self):
        self.top_k = int(os.getenv("RAG_TOP_K", "5"))
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.3"))


@dataclass
class AppConfig:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)


# Global config instance
config = AppConfig()
