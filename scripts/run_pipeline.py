"""
CLI entry point for the LocalLLM-RAG pipeline.

Usage:
    python -m scripts.run_pipeline --serve        # Launch web UI
    python -m scripts.run_pipeline --chat         # Interactive terminal chat
    python -m scripts.run_pipeline --query "..."  # Single query
    python -m scripts.run_pipeline --stats        # Show database stats
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(description="LocalLLM-RAG Pipeline")
    parser.add_argument("--serve", action="store_true", help="Launch Gradio web UI")
    parser.add_argument("--chat", action="store_true", help="Interactive terminal chat")
    parser.add_argument("--query", type=str, help="Run a single query")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--top-k", type=int, default=5, help="Number of reviews to retrieve")
    parser.add_argument("--temperature", type=float, default=0.3, help="LLM temperature")

    args = parser.parse_args()

    if args.stats:
        from src.database.schema import get_stats
        stats = get_stats()
        print("\n📊 Database Statistics:")
        for table, count in stats.items():
            print(f"   {table}: {count:,}")

    elif args.query:
        from src.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline(top_k=args.top_k, temperature=args.temperature)
        result = pipeline.query(args.query, show_context=True)
        print(f"\n🤖 Answer:\n{result['answer']}")
        print(f"\n⏱️ Retrieval: {result['retrieval_time']:.2f}s | "
              f"Generation: {result['generation_time']:.2f}s")

    elif args.chat:
        from src.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline(top_k=args.top_k, temperature=args.temperature)
        pipeline.chat_interactive()

    elif args.serve:
        from src.api.app import app, CUSTOM_THEME, CUSTOM_CSS
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            theme=CUSTOM_THEME,
            css=CUSTOM_CSS,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
