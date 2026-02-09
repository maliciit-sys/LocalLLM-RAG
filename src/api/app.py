"""
LocalLLM-RAG: Gradio Web UI
============================
Chat interface for querying the food review database.

Usage:
    cd ~/ml-projects/python-projects/LocalLLM-RAG
    python -m src.api.app
"""

import time
import gradio as gr
import torch

from src.rag.pipeline import RAGPipeline
from src.database.schema import get_stats
from src.llm.ollama_client import get_ollama_client
from src.utils.config import config

# ── Initialize ────────────────────────────────────────────────

print("🔄 Initializing LocalLLM-RAG...")

pipeline = RAGPipeline(top_k=5, temperature=0.3)
ollama = get_ollama_client()

# Verify Ollama
if ollama.is_available():
    print(f"  ✅ Ollama connected ({config.ollama.model})")
else:
    print(f"  ⚠️ Ollama not reachable — run: ollama serve")

print("🚀 Ready!\n")


# ── Helper Functions ──────────────────────────────────────────

def format_sources(contexts: list[dict]) -> str:
    """Format retrieved sources for the sidebar."""
    if not contexts:
        return "No sources found."

    sources_md = ""
    for i, ctx in enumerate(contexts, 1):
        stars = "⭐" * ctx["score"]
        sim_pct = f"{ctx['similarity'] * 100:.1f}%"
        review_preview = ctx["review_text"][:200]
        sources_md += f"""### Review {i} — Match: {sim_pct}
**{ctx['summary']}** {stars}
- **Product:** `{ctx['product_id']}`
- **Helpfulness:** {ctx['helpfulness_num']}/{ctx['helpfulness_den']} found helpful

> {review_preview}{"..." if len(ctx["review_text"]) > 200 else ""}

---
"""
    return sources_md


def respond(message, chat_history, top_k, temperature):
    """Main chat response function with streaming."""
    if not message.strip():
        return "", chat_history, ""

    # Update pipeline settings
    pipeline.top_k = int(top_k)
    pipeline.temperature = temperature

    # Get streaming result
    result = pipeline.query(message, stream=True)
    contexts = result["contexts"]
    retrieval_time = result["retrieval_time"]
    sources = format_sources(contexts)

    # Add user message
    chat_history = chat_history + [{"role": "user", "content": message}]
    chat_history = chat_history + [{"role": "assistant", "content": ""}]

    # Stream response
    gen_start = time.time()
    for token in result["stream"]:
        chat_history[-1]["content"] += token
        yield "", chat_history, sources

    gen_time = time.time() - gen_start
    timing = f"\n\n---\n*🔍 Retrieval: {retrieval_time:.2f}s | 🤖 Generation: {gen_time:.2f}s | Total: {retrieval_time + gen_time:.2f}s*"
    chat_history[-1]["content"] += timing

    yield "", chat_history, sources


def clear_chat():
    return [], ""


# ── Database Stats ────────────────────────────────────────────

def get_db_stats_text():
    try:
        stats = get_stats()
        return (f"📊 **{stats['reviews']:,}** reviews | "
                f"**{stats['products']:,}** products | "
                f"**{stats['users']:,}** users | "
                f"**{stats['embedded']:,}** embedded")
    except Exception:
        return "📊 Database stats unavailable"


# ── Build UI ──────────────────────────────────────────────────

EXAMPLE_QUERIES = [
    "What do people think about organic coffee?",
    "Which dog food products have the best reviews?",
    "What are common complaints about chocolate products?",
    "Are there any highly rated gluten-free snacks?",
    "What's the best tea according to reviewers?",
    "Do people like sugar-free candy?",
    "What do customers say about baby food quality?",
    "Which snack bars have the most helpful reviews?",
]

CUSTOM_CSS = """
    .main-header { text-align: center; padding: 1.5rem 0 0.5rem; }
    .main-header h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.25rem; }
    .main-header p { opacity: 0.7; font-size: 1rem; }
    .stats-bar { text-align: center; padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem; }
    footer { display: none !important; }
"""

CUSTOM_THEME = gr.themes.Soft(
    primary_hue="amber",
    secondary_hue="orange",
    neutral_hue="stone",
)

with gr.Blocks(title="LocalLLM-RAG") as app:

    gr.HTML("""
        <div class="main-header">
            <h1>🧠 LocalLLM-RAG</h1>
            <p>Self-hosted food review assistant — powered by your database, not the web</p>
        </div>
    """)

    gr.Markdown(get_db_stats_text(), elem_classes="stats-bar")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=520, show_label=False)

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask about food products, reviews, ratings...",
                    show_label=False, scale=6, container=False,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
                clear_btn = gr.Button("Clear", scale=1)

            gr.Examples(examples=EXAMPLE_QUERIES, inputs=msg, label="💡 Try these queries")

        with gr.Column(scale=2):
            with gr.Tab("📄 Sources"):
                sources_display = gr.Markdown(
                    value="*Sources will appear here after you ask a question...*",
                )

            with gr.Tab("⚙️ Settings"):
                top_k = gr.Slider(3, 10, value=5, step=1, label="Reviews to retrieve (Top-K)")
                temperature = gr.Slider(0.0, 1.0, value=0.3, step=0.1, label="Temperature")
                gr.Markdown(f"""
### Model Info
- **LLM:** `{config.ollama.model}`
- **Embeddings:** `{config.embedding.model_name}` ({config.embedding.dimension}d)
- **Vector DB:** PostgreSQL + pgvector (HNSW)
- **GPU:** `{torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}`
                """)

            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
### How it works
1. Your question is converted into a vector embedding
2. pgvector finds the most similar reviews in the database
3. Retrieved reviews are sent as context to the LLM
4. The LLM generates an answer based ONLY on those reviews

*All processing happens locally. No data leaves your machine.*
                """)

    # Events
    msg.submit(respond, [msg, chatbot, top_k, temperature], [msg, chatbot, sources_display])
    send_btn.click(respond, [msg, chatbot, top_k, temperature], [msg, chatbot, sources_display])
    clear_btn.click(clear_chat, outputs=[chatbot, sources_display])


# ── Launch ────────────────────────────────────────────────────

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=CUSTOM_THEME,
        css=CUSTOM_CSS,
    )
