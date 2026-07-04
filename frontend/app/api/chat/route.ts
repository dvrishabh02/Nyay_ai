import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const question = typeof body?.question === "string" ? body.question.trim() : "";

  if (!question) {
    return NextResponse.json({ error: "question is required" }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { error: "Could not reach the Nyay backend. Is it running?" },
      { status: 502 },
    );
  }

  const payload = await upstream.json().catch(() => null);

  if (!upstream.ok) {
    return NextResponse.json(
      { error: payload?.detail ?? `Backend error (${upstream.status})` },
      { status: upstream.status },
    );
  }

  return NextResponse.json(payload);
}
