"""
RAG Pipeline - Orchestrates retrieval → prompt → generation.
"""

import time
from src.embeddings.search import semantic_search
from src.llm.ollama_client import get_ollama_client
from src.llm.prompts import build_rag_prompt


class RAGPipeline:
    """End-to-end RAG pipeline."""

    def __init__(self, top_k: int = 5, temperature: float = 0.3):
        self.top_k = top_k
        self.temperature = temperature
        self.llm = get_ollama_client()

    def retrieve(self, query: str) -> list[dict]:
        """Retrieve relevant reviews for a query."""
        return semantic_search(query, top_k=self.top_k)

    def generate(self, query: str, contexts: list[dict],
                 chat_history: list = None, stream: bool = False):
        """Generate a response from the LLM."""
        prompt = build_rag_prompt(query, contexts, chat_history)

        if stream:
            return self.llm.generate_stream(prompt, temperature=self.temperature)
        else:
            return self.llm.generate(prompt, temperature=self.temperature)

    def query(self, query: str, chat_history: list = None,
              stream: bool = False, show_context: bool = False) -> dict:
        """
        Full RAG pipeline: retrieve → generate.

        Args:
            query: User's question
            chat_history: Optional conversation history
            stream: If True, returns a generator for streaming
            show_context: If True, prints retrieved context

        Returns:
            Dict with query, answer, contexts, and timing info
        """
        # Step 1: Retrieve
        start = time.time()
        contexts = self.retrieve(query)
        retrieval_time = time.time() - start

        if show_context:
            print(f"\n🔍 Retrieved {len(contexts)} reviews ({retrieval_time:.3f}s):")
            for i, ctx in enumerate(contexts, 1):
                print(f"   {i}. [{ctx['score']}/5 | Sim: {ctx['similarity']:.4f}] {ctx['summary']}")

        if not contexts:
            return {
                "query": query,
                "answer": "No relevant reviews found in the database.",
                "contexts": [],
                "retrieval_time": retrieval_time,
                "generation_time": 0,
            }

        # Step 2: Generate
        if stream:
            # Return generator for streaming use cases
            return {
                "query": query,
                "contexts": contexts,
                "retrieval_time": retrieval_time,
                "stream": self.generate(query, contexts, chat_history, stream=True),
            }

        start = time.time()
        answer = self.generate(query, contexts, chat_history, stream=False)
        generation_time = time.time() - start

        return {
            "query": query,
            "answer": answer,
            "contexts": contexts,
            "retrieval_time": retrieval_time,
            "generation_time": generation_time,
            "total_time": retrieval_time + generation_time,
        }

    def chat_interactive(self):
        """Interactive chat loop in the terminal."""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║   🧠 LocalLLM-RAG: Food Review Assistant                ║")
        print("║   Type 'quit' to exit                                   ║")
        print("╚══════════════════════════════════════════════════════════╝\n")

        history = []

        while True:
            query = input("\n💬 You: ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                break
            if not query:
                continue

            result = self.query(query, chat_history=history, show_context=True)
            print(f"\n🤖 Assistant: {result['answer']}")
            print(f"\n⏱️ Retrieval: {result['retrieval_time']:.2f}s | "
                  f"Generation: {result['generation_time']:.2f}s")

            history.append([query, result["answer"]])


# Convenience function
def quick_query(query: str, top_k: int = 5) -> str:
    """Quick one-shot query."""
    pipeline = RAGPipeline(top_k=top_k)
    result = pipeline.query(query)
    return result["answer"]
