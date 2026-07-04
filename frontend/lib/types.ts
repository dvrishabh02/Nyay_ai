// Real FastAPI /query contract — see api/schemas.py and rag/models.py.
export interface CitationDTO {
  n: number;
  title: string;
  source: string;
  doc_type: string;
}

export interface QueryResponseDTO {
  question: string;
  answer: string;
  confidence: string; // "HIGH" | "MEDIUM" | "LOW" at the boundary, normalized on the client
  citations: CitationDTO[];
  latency_ms: number;
}

export type Confidence = "HIGH" | "MEDIUM" | "LOW";

export interface SourceChip {
  tag: string;
  text: string;
}

export interface AssistantCardData {
  confidence: Confidence;
  confLabel: string;
  barsFilled: 1 | 2 | 3;
  lead: string;
  sources: SourceChip[];
}

export type ChatMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; data: AssistantCardData }
  | { id: string; role: "assistant-error"; message: string; question: string };
