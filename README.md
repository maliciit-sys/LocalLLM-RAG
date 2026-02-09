# 🧠 LocalLLM-RAG

A self-hosted LLM system that answers queries exclusively from your own database — not the web. Built with a Retrieval-Augmented Generation (RAG) pipeline using PostgreSQL + pgvector, sentence-transformers, and Ollama.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)
![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5_14B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  User Query  │────▶│  Embedding   │────▶│  pgvector Similarity │
│              │     │  Model (GPU) │     │  Search (PostgreSQL) │
└─────────────┘     └──────────────┘     └──────────┬──────────┘
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │  Top-K Relevant     │
                                          │  Documents/Reviews  │
                                          └──────────┬──────────┘
                                                     │
                                                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Response    │◀────│  Ollama LLM  │◀────│  Prompt + Context   │
│              │     │  (Qwen 2.5)  │     │                     │
└─────────────┘     └──────────────┘     └─────────────────────┘
```

## 📊 Evaluation Results

| Metric | Score |
|--------|-------|
| **Retrieval Keyword Precision** | 100.0% |
| **Avg Similarity Score** | 0.7773 |
| **Retrieval Time** | 7.0ms |
| **Faithfulness** | 4.40/5 |
| **Relevance** | 4.80/5 |
| **Completeness** | 3.40/5 |
| **Hallucination Rate** | 20% |
| **Product Diversity** | 100.0% |
| **Avg End-to-End Latency** | 4.03s |
| **Tokens/sec** | 11.0 |

## 🔧 Tech Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| LLM                | Qwen 2.5 14B via Ollama             |
| Embedding Model    | all-MiniLM-L6-v2 (384 dims)        |
| Vector Database    | PostgreSQL 14 + pgvector (HNSW)     |
| Backend            | Python 3.10 + SQLAlchemy            |
| Web UI             | Gradio                              |
| GPU                | NVIDIA RTX 5070 Ti (12GB VRAM)      |
| Dataset            | Amazon Fine Food Reviews (568K)     |

## 📁 Project Structure

```
LocalLLM-RAG/
├── src/
│   ├── database/              # PostgreSQL connection, schema, queries
│   │   ├── connection.py      # DB engine & session management
│   │   ├── schema.py          # Table definitions & vector index
│   │   └── queries.py         # SQL queries for retrieval
│   ├── embeddings/            # Embedding generation & search
│   │   ├── generator.py       # Batch embedding with sentence-transformers
│   │   └── search.py          # Vector similarity search
│   ├── llm/                   # LLM interaction layer
│   │   ├── ollama_client.py   # Ollama API wrapper (streaming + sync)
│   │   └── prompts.py         # Prompt templates for RAG & evaluation
│   ├── rag/                   # RAG pipeline orchestration
│   │   └── pipeline.py        # End-to-end retrieve → generate pipeline
│   ├── api/                   # Web interface
│   │   └── app.py             # Gradio chat UI with sources panel
│   └── utils/                 # Shared utilities
│       └── config.py          # Configuration loader from .env
├── config/                    # Configuration files
├── notebooks/                 # Jupyter notebooks (step-by-step)
│   ├── 00_Creating_PostgreSQL_DB.ipynb
│   ├── 01_embedding.ipynb
│   ├── 02_rag_pipeline.ipynb
│   └── 03_evaluation.ipynb
├── scripts/
│   ├── run_pipeline.py        # CLI entry point
│   └── start.sh               # Quick launch script
├── data/
│   ├── raw/                   # Original Kaggle dataset
│   └── processed/             # Cleaned data
├── tests/                     # Test suite
├── docs/                      # Documentation
├── .env.example               # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04+
- NVIDIA GPU with 12GB+ VRAM (CUDA support)
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Ollama

### 1. Clone & Setup

```bash
git clone https://github.com/maliciit-sys/LocalLLM-RAG.git
cd LocalLLM-RAG
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
# Fill in your database credentials and model preferences
```

### 3. Setup PostgreSQL + pgvector

```bash
sudo apt install postgresql postgresql-contrib -y
cd /tmp && git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector && make && sudo make install

sudo -u postgres psql -c "CREATE USER llmuser WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE llmdb OWNER llmuser;"
sudo -u postgres psql -d llmdb -c "CREATE EXTENSION vector;"
```

### 4. Download Dataset

Download [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) from Kaggle and place `Reviews.csv` in `data/raw/`.

### 5. Load Data & Generate Embeddings

Run the notebooks in order:
1. `notebooks/00_Creating_PostgreSQL_DB.ipynb` — Load CSV into PostgreSQL
2. `notebooks/01_embedding.ipynb` — Generate vector embeddings on GPU

### 6. Install LLM

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:14b
```

### 7. Launch

```bash
# Web UI
python scripts/run_pipeline.py --serve

# Terminal chat
python scripts/run_pipeline.py --chat

# Single query
python scripts/run_pipeline.py --query "What do people think about organic coffee?"

# Database stats
python scripts/run_pipeline.py --stats
```

Open `http://localhost:7860` for the web interface.

## 🖥️ Web UI Features

- 💬 **Streaming chat** — real-time token-by-token responses
- 📄 **Sources panel** — shows retrieved reviews with similarity scores
- ⚙️ **Adjustable settings** — Top-K and temperature controls
- 💡 **Example queries** — pre-built questions to try
- 📊 **Database stats** — live data overview

## 🧪 Example Queries

```
> What do people think about organic coffee? Is it worth buying?
> Which dog food products have the best reviews and why?
> What are common complaints about chocolate products?
> Are there any highly rated gluten-free snacks?
> What's the best tea according to reviewers?
> Do people like sugar-free candy?
```

## 🔬 How RAG Works

1. **Embed**: Your question is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
2. **Retrieve**: pgvector HNSW index finds the Top-K most similar reviews (~7ms)
3. **Augment**: Retrieved reviews are injected into the prompt as context
4. **Generate**: Qwen 2.5 14B generates an answer grounded ONLY in retrieved reviews

All processing happens **locally on your machine**. No data is sent to any external service.

## 💻 Hardware Used

| Component | Specification |
|-----------|--------------|
| Laptop | Lenovo Legion 5 Pro |
| RAM | 32 GB |
| Storage | 2 TB NVMe |
| GPU | NVIDIA RTX 5070 Ti (12GB VRAM) |
| OS | Ubuntu 22.04 |

## 📈 Future Improvements

- [ ] Add re-ranking after retrieval (cross-encoder)
- [ ] Upgrade to larger embedding model (bge-large-en-v1.5)
- [ ] Implement hybrid search (semantic + keyword)
- [ ] Add conversation memory with context windowing
- [ ] Support multiple datasets
- [ ] Docker containerization

## 📄 License

MIT License

## 🤝 Acknowledgments

- [Ollama](https://ollama.com/) — local LLM serving
- [pgvector](https://github.com/pgvector/pgvector) — vector similarity for PostgreSQL
- [Sentence Transformers](https://www.sbert.net/) — embedding models
- [Amazon Fine Food Reviews](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) — dataset
- [Gradio](https://gradio.app/) — web UI framework
