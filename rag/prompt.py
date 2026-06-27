"""
Prompt construction — system instructions (grounding + citation rules) and the
user message that packs the retrieved context as numbered, citable sources.
"""

from rag.config import DISCLAIMER, NO_CONTEXT_FALLBACK
from rag.models import RetrievedChunk

SYSTEM_PROMPT = f"""You are Nyay.AI, a legal information assistant for Indian citizens. \
You answer questions using ONLY the numbered CONTEXT sources provided in each query.

Rules:
1. Base every statement strictly on the CONTEXT. Do not use outside knowledge or \
invent sections, case names, or numbers.
2. Cite the sources you use inline with their bracket numbers, e.g. [1], [2]. Cite \
the specific source(s) each claim comes from.
3. If the CONTEXT does not contain enough information to answer, reply exactly: \
"{NO_CONTEXT_FALLBACK} in my sources to answer this reliably." Do not guess.
4. Answer in clear, plain English a non-lawyer can understand. Be concise and practical.
5. Do not give a personal legal opinion or tell the user what they "should" do as \
definite advice — explain what the law says and the general options.

End every answer with this line, unchanged:
{DISCLAIMER}"""


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Pack the question + numbered context blocks. The [n] order here is what
    the model cites and what citations are mapped back to."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        header = f"[{i}] {c.title} (source: {c.source}, type: {c.doc_type})"
        blocks.append(f"{header}\n{c.text.strip()}")
    context = "\n\n".join(blocks)

    return (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the CONTEXT above, citing sources as [n]."
    )


def build_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """OpenAI-style messages for the Groq chat completions API."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(question, chunks)},
    ]
