"""
Prompt construction — system instructions (grounding rules) and the user message
that packs the retrieved context. Sources are shown to the user separately (as a
list of source names), so the model is told to write plain prose with no numbers.
"""

from rag.config import DISCLAIMER, NO_CONTEXT_FALLBACK
from rag.models import RetrievedChunk

SYSTEM_PROMPT = f"""You are Nyay.AI, a legal information assistant for Indian citizens. \
You answer questions using ONLY the CONTEXT sources provided in each query.

Rules:
1. Base every statement strictly on the CONTEXT. Do not use outside knowledge or \
invent sections, case names, or numbers.
2. Write in natural, flowing plain English. Do NOT use reference numbers, brackets, \
or footnote markers (such as [1], "source 2", or "1, 2, 4") anywhere in your answer. \
When it helps the reader, refer to a law by its name — for example, "the Consumer \
Protection Act, 2019".
3. If the CONTEXT does not contain enough information to answer, reply exactly: \
"{NO_CONTEXT_FALLBACK} in my sources to answer this reliably." Do not guess.
4. Keep it clear, concise, and practical for a non-lawyer.
5. Do not give a personal legal opinion or tell the user what they "should" do as \
definite advice — explain what the law says and the general options.

End every answer with this line, unchanged:
{DISCLAIMER}"""


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Pack the question + context blocks, each labelled by source name (no numbers)."""
    blocks = []
    for c in chunks:
        header = f"— {c.title} ({c.source}, {c.doc_type})"
        blocks.append(f"{header}\n{c.text.strip()}")
    context = "\n\n".join(blocks)

    return (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the CONTEXT above, in plain English. "
        "Do not use reference numbers or brackets."
    )


def build_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """OpenAI-style messages for the Groq chat completions API."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(question, chunks)},
    ]
