"""
Prompt templates for the RAG pipeline.
"""


def build_rag_prompt(query: str, contexts: list[dict], chat_history: list = None) -> str:
    """
    Build a RAG prompt that instructs the LLM to answer from retrieved context only.

    Args:
        query: User's question
        contexts: List of retrieved review dicts
        chat_history: Optional list of [user_msg, bot_msg] pairs
    """
    context_text = ""
    for i, ctx in enumerate(contexts, 1):
        review_text = ctx.get("review_text", "")[:500]
        context_text += f"""
--- Review {i} ---
Product ID: {ctx.get('product_id', 'N/A')}
Rating: {ctx.get('score', 'N/A')}/5
Helpfulness: {ctx.get('helpfulness_num', 0)}/{ctx.get('helpfulness_den', 0)}
Summary: {ctx.get('summary', 'N/A')}
Review: {review_text}
Similarity Score: {ctx.get('similarity', 0):.4f}
"""

    history_text = ""
    if chat_history and len(chat_history) > 0:
        recent = chat_history[-3:]
        for user_msg, bot_msg in recent:
            history_text += f"\nUser: {user_msg}\nAssistant: {bot_msg}\n"

    prompt = f"""You are a helpful food product review assistant. You answer questions ONLY based on the provided customer reviews from an Amazon food product database.

STRICT RULES:
- ONLY use information explicitly stated in the reviews below
- NEVER add facts, opinions, or details not present in the reviews
- If reviews don't contain enough information, say "Based on the available reviews, I don't have enough information to answer this fully."
- Cite specific reviews when making claims (e.g., "Review 1 mentions...")
- Include ratings when relevant
- Present both perspectives if reviews conflict
- Be concise but thorough
{f"Previous conversation:{history_text}" if history_text else ""}

Here are the relevant customer reviews retrieved from the database:
{context_text}

Based ONLY on the reviews above, answer this question:

Question: {query}

Answer:"""

    return prompt


def build_eval_prompt(query: str, context_summary: str, answer: str) -> str:
    """
    Build an evaluation prompt for judging response quality.

    Args:
        query: Original question
        context_summary: Summary of retrieved context
        answer: LLM's answer to evaluate
    """
    return f"""You are an evaluation judge. Given a QUESTION, CONTEXT (retrieved reviews), and an ANSWER, evaluate:

1. **Faithfulness** (1-5): Does the answer ONLY use information from the context? 5 = perfectly grounded, 1 = mostly hallucinated.
2. **Relevance** (1-5): Does the answer address the question? 5 = directly answers, 1 = off-topic.
3. **Completeness** (1-5): Does the answer use the available context well? 5 = thorough, 1 = ignores most context.
4. **Hallucination**: Does the answer contain claims NOT in the context? (yes/no)

Respond in this EXACT format:
Faithfulness: <score>
Relevance: <score>
Completeness: <score>
Hallucination: <yes/no>
Reasoning: <brief explanation>

QUESTION: {query}

CONTEXT:
{context_summary}

ANSWER: {answer}

Evaluation:"""
