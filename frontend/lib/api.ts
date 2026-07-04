import type { AssistantCardData, Confidence, QueryResponseDTO } from "@/lib/types";

function normalizeConfidence(value: string): Confidence {
  const upper = value.toUpperCase();
  return upper === "HIGH" || upper === "MEDIUM" ? upper : "LOW";
}

function mapResponseToCard(dto: QueryResponseDTO): AssistantCardData {
  const confidence = normalizeConfidence(dto.confidence);
  const barsFilled = confidence === "HIGH" ? 3 : confidence === "MEDIUM" ? 2 : 1;

  return {
    confidence,
    confLabel: `${confidence.toLowerCase()} confidence`,
    barsFilled,
    lead: dto.answer,
    sources: [...dto.citations]
      .sort((a, b) => a.n - b.n)
      .map((c) => ({
        tag: c.doc_type.toUpperCase(),
        text: c.source && c.source !== c.title ? `${c.title} · ${c.source}` : c.title,
      })),
  };
}

export async function sendQuery(question: string): Promise<AssistantCardData> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error ?? `Request failed (${res.status})`);
  }

  const data: QueryResponseDTO = await res.json();
  return mapResponseToCard(data);
}
