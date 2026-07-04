"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Header from "@/components/Header";
import ChatThread from "@/components/ChatThread";
import Composer from "@/components/Composer";
import { sendQuery } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

export default function ChatApp() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const scrollRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, pending]);

  const submit = useCallback(
    async (raw: string) => {
      const text = raw.trim();
      if (!text || pending) return;

      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "user", text }]);
      setInput("");
      setPending(true);

      try {
        const data = await sendQuery(text);
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "assistant", data }]);
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant-error",
            message: err instanceof Error ? err.message : "Something went wrong.",
            question: text,
          },
        ]);
      } finally {
        setPending(false);
      }
    },
    [pending],
  );

  return (
    <div className="h-screen flex flex-col bg-canvas">
      <Header />
      <main ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="max-w-[820px] mx-auto px-5 pt-[26px] pb-3 flex flex-col gap-[22px]">
          <ChatThread
            messages={messages}
            pending={pending}
            onSuggestionClick={submit}
            onRetry={submit}
          />
        </div>
      </main>
      <Composer value={input} onChange={setInput} onSubmit={() => submit(input)} disabled={pending} />
    </div>
  );
}
