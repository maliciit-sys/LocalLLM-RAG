#!/bin/bash
# ============================================================
# LocalLLM-RAG: Git Commit Script
# Creates 30+ meaningful commits for a clean Git history
# ============================================================

set -e
cd ~/ml-projects/python-projects/LocalLLM-RAG

# Ensure git is initialized
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# ── Helper function ───────────────────────────────────────────
commit() {
    git add $1
    git commit -m "$2"
    echo "✅ Commit: $2"
}

# ══════════════════════════════════════════════════════════════
# Phase 1: Project Foundation (Commits 1-6)
# ══════════════════════════════════════════════════════════════

# 1
git add .gitignore
git commit -m "chore: add .gitignore for Python, data, and model files"
echo "✅ Commit 1: .gitignore"

# 2
git add .env.example
git commit -m "chore: add environment variable template"
echo "✅ Commit 2: .env.example"

# 3
git add requirements.txt
git commit -m "chore: add Python dependencies (torch, sqlalchemy, gradio, etc.)"
echo "✅ Commit 3: requirements.txt"

# 4
git add README.md
git commit -m "docs: add project README with architecture and setup guide"
echo "✅ Commit 4: README.md"

# 5
git add config/.gitkeep
git commit -m "chore: create config directory structure"
echo "✅ Commit 5: config/"

# 6
git add docs/.gitkeep tests/.gitkeep
git commit -m "chore: create docs and tests directories"
echo "✅ Commit 6: docs/ and tests/"

# ══════════════════════════════════════════════════════════════
# Phase 2: Data Directory (Commits 7-8)
# ══════════════════════════════════════════════════════════════

# 7
git add data/raw/.gitkeep 2>/dev/null || touch data/raw/.gitkeep && git add data/raw/.gitkeep
git commit -m "chore: create raw data directory for Kaggle datasets"
echo "✅ Commit 7: data/raw/"

# 8
git add data/processed/.gitkeep
git commit -m "chore: create processed data directory"
echo "✅ Commit 8: data/processed/"

# ══════════════════════════════════════════════════════════════
# Phase 3: Source Package Init (Commits 9-14)
# ══════════════════════════════════════════════════════════════

# 9
git add src/__init__.py
git commit -m "feat: initialize src package"
echo "✅ Commit 9: src/__init__.py"

# 10
git add src/utils/__init__.py
git commit -m "feat: initialize utils module"
echo "✅ Commit 10: src/utils/__init__"

# 11
git add src/utils/config.py
git commit -m "feat: add configuration loader with dataclass-based settings"
echo "✅ Commit 11: config.py"

# 12
git add src/database/__init__.py
git commit -m "feat: initialize database module"
echo "✅ Commit 12: src/database/__init__"

# 13
git add src/database/connection.py
git commit -m "feat: add PostgreSQL connection manager with SQLAlchemy engine"
echo "✅ Commit 13: connection.py"

# 14
git add src/database/schema.py
git commit -m "feat: add database schema with products, users, reviews tables and pgvector"
echo "✅ Commit 14: schema.py"

# ══════════════════════════════════════════════════════════════
# Phase 4: Database Queries (Commit 15)
# ══════════════════════════════════════════════════════════════

# 15
git add src/database/queries.py
git commit -m "feat: add database queries for vector similarity search and CRUD"
echo "✅ Commit 15: queries.py"

# ══════════════════════════════════════════════════════════════
# Phase 5: Embeddings Module (Commits 16-18)
# ══════════════════════════════════════════════════════════════

# 16
git add src/embeddings/__init__.py
git commit -m "feat: initialize embeddings module"
echo "✅ Commit 16: src/embeddings/__init__"

# 17
git add src/embeddings/generator.py
git commit -m "feat: add embedding generator with GPU batch processing (all-MiniLM-L6-v2)"
echo "✅ Commit 17: generator.py"

# 18
git add src/embeddings/search.py
git commit -m "feat: add semantic search using pgvector cosine similarity"
echo "✅ Commit 18: search.py"

# ══════════════════════════════════════════════════════════════
# Phase 6: LLM Module (Commits 19-21)
# ══════════════════════════════════════════════════════════════

# 19
git add src/llm/__init__.py
git commit -m "feat: initialize LLM module"
echo "✅ Commit 19: src/llm/__init__"

# 20
git add src/llm/ollama_client.py
git commit -m "feat: add Ollama API client with streaming and sync generation"
echo "✅ Commit 20: ollama_client.py"

# 21
git add src/llm/prompts.py
git commit -m "feat: add RAG prompt templates with strict grounding instructions"
echo "✅ Commit 21: prompts.py"

# ══════════════════════════════════════════════════════════════
# Phase 7: RAG Pipeline (Commits 22-23)
# ══════════════════════════════════════════════════════════════

# 22
git add src/rag/__init__.py
git commit -m "feat: initialize RAG module"
echo "✅ Commit 22: src/rag/__init__"

# 23
git add src/rag/pipeline.py
git commit -m "feat: add end-to-end RAG pipeline (retrieve → prompt → generate)"
echo "✅ Commit 23: pipeline.py"

# ══════════════════════════════════════════════════════════════
# Phase 8: Web UI (Commits 24-25)
# ══════════════════════════════════════════════════════════════

# 24
git add src/api/__init__.py
git commit -m "feat: initialize API module"
echo "✅ Commit 24: src/api/__init__"

# 25
git add src/api/app.py
git commit -m "feat: add Gradio web UI with streaming chat, sources panel, and settings"
echo "✅ Commit 25: app.py"

# ══════════════════════════════════════════════════════════════
# Phase 9: Scripts (Commits 26-27)
# ══════════════════════════════════════════════════════════════

# 26
git add scripts/run_pipeline.py
git commit -m "feat: add CLI entry point (--serve, --chat, --query, --stats)"
echo "✅ Commit 26: run_pipeline.py"

# 27
if [ -f scripts/start.sh ]; then
    git add scripts/start.sh
    git commit -m "feat: add quick launch script for one-command startup"
    echo "✅ Commit 27: start.sh"
else
    # Create start.sh if missing
    cat > scripts/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting LocalLLM-RAG..."
sudo systemctl start postgresql
sleep 1
cd ~/ml-projects/python-projects/LocalLLM-RAG
source ~/ml-projects/ml-env/bin/activate
python src/api/app.py
EOF
    chmod +x scripts/start.sh
    git add scripts/start.sh
    git commit -m "feat: add quick launch script for one-command startup"
    echo "✅ Commit 27: start.sh"
fi

# ══════════════════════════════════════════════════════════════
# Phase 10: Notebooks (Commits 28-31)
# ══════════════════════════════════════════════════════════════

# 28
if [ -f notebooks/00_Creating_PostgreSQL_DB.ipynb ]; then
    git add notebooks/00_Creating_PostgreSQL_DB.ipynb
    git commit -m "docs: add notebook for PostgreSQL database setup and data loading"
    echo "✅ Commit 28: notebook 00"
fi

# 29
if [ -f notebooks/01_embedding.ipynb ]; then
    git add notebooks/01_embedding.ipynb
    git commit -m "docs: add notebook for embedding generation on GPU (564K reviews)"
    echo "✅ Commit 29: notebook 01"
fi

# 30
if [ -f notebooks/02_rag_pipeline.ipynb ]; then
    git add notebooks/02_rag_pipeline.ipynb
    git commit -m "docs: add notebook for RAG pipeline testing and interactive chat"
    echo "✅ Commit 30: notebook 02"
fi

# 31
if [ -f notebooks/03_evaluation.ipynb ]; then
    git add notebooks/03_evaluation.ipynb
    git commit -m "docs: add evaluation notebook with retrieval, groundedness, and performance metrics"
    echo "✅ Commit 31: notebook 03"
fi

# ══════════════════════════════════════════════════════════════
# Phase 11: Final Touches (Commits 32-34)
# ══════════════════════════════════════════════════════════════

# 32 - Catch any remaining files
git add -A
git diff --cached --quiet || git commit -m "chore: add remaining project files"
echo "✅ Commit 32: remaining files"

# 33 - Update README with final evaluation results
git add README.md
git diff --cached --quiet || git commit -m "docs: update README with evaluation results and hardware specs"
echo "✅ Commit 33: README update"

# 34 - Final tag
git add -A
git diff --cached --quiet || git commit -m "release: v1.0.0 — fully functional self-hosted RAG pipeline"
echo "✅ Commit 34: v1.0.0 release"

# ══════════════════════════════════════════════════════════════
# Push to GitHub
# ══════════════════════════════════════════════════════════════

echo ""
echo "══════════════════════════════════════════════════════════"
echo "📊 Commit Summary:"
git log --oneline | head -40
echo ""
echo "Total commits: $(git rev-list --count HEAD)"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "🚀 Pushing to GitHub..."
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:maliciit-sys/LocalLLM-RAG.git
git branch -M main
git push -u origin main

echo ""
echo "✅ All done! Repository live at:"
echo "   https://github.com/maliciit-sys/LocalLLM-RAG"
