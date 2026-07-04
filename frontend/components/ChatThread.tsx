import EmptyState from "@/components/EmptyState";
import UserBubble from "@/components/UserBubble";
import AssistantCard from "@/components/AssistantCard";
import ErrorCard from "@/components/ErrorCard";
import ThinkingIndicator from "@/components/ThinkingIndicator";
import type { ChatMessage } from "@/lib/types";

export default function ChatThread({
  messages,
  pending,
  onSuggestionClick,
  onRetry,
}: {
  messages: ChatMessage[];
  pending: boolean;
  onSuggestionClick: (text: string) => void;
  onRetry: (question: string) => void;
}) {
  if (messages.length === 0 && !pending) {
    return <EmptyState onSuggestionClick={onSuggestionClick} />;
  }

  return (
    <>
      {messages.map((m) => (
        <div key={m.id} className="animate-ny-rise">
          {m.role === "user" && <UserBubble text={m.text} />}
          {m.role === "assistant" && <AssistantCard data={m.data} />}
          {m.role === "assistant-error" && (
            <ErrorCard message={m.message} onRetry={() => onRetry(m.question)} />
          )}
        </div>
      ))}
      {pending && <ThinkingIndicator />}
    </>
  );
}
