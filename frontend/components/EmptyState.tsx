const SUGGESTIONS = [
  "My landlord cut off my electricity — is that legal?",
  "My employer hasn’t paid my salary for 2 months.",
  "How do I file an RTI application?",
];

export default function EmptyState({
  onSuggestionClick,
}: {
  onSuggestionClick: (text: string) => void;
}) {
  return (
    <div className="pt-12 pb-6 px-2 text-center flex flex-col items-center">
      <div className="w-14 h-14 rounded-2xl bg-ink text-surface flex items-center justify-center font-devanagari text-[30px] font-semibold mb-[22px]">
        न
      </div>
      <h1 className="font-serif text-[32px] leading-[1.25] font-medium tracking-[-0.02em] max-w-[15ch] mb-3">
        How can we help you understand your rights?
      </h1>
      <p className="text-[15px] leading-[1.55] text-ink/60 max-w-[44ch] mb-[30px]">
        Ask about a legal problem in your own words — we&rsquo;ll explain it simply and show you
        where it comes from.
      </p>
      <div className="flex flex-col gap-2.5 w-full max-w-[440px]">
        {SUGGESTIONS.map((text) => (
          <button
            key={text}
            type="button"
            onClick={() => onSuggestionClick(text)}
            className="text-left border border-ink/[14%] bg-surface text-ink rounded-[13px] px-4 py-3.5 text-[14.5px] font-medium flex items-center gap-[11px] hover:border-ink hover:bg-white transition-colors"
          >
            <span className="flex-none text-ink/35 text-base">→</span>
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}
