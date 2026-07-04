export default function Composer({
  value,
  onChange,
  onSubmit,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
}) {
  return (
    <footer className="flex-none bg-surface border-t border-ink/[8%]">
      <div className="max-w-[820px] mx-auto px-5 pt-3.5 pb-3">
        <div className="flex items-center gap-3 border border-ink/[16%] rounded-[14px] py-1.5 pl-4 pr-1.5">
          <input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                onSubmit();
              }
            }}
            placeholder="Ask about your legal situation…"
            className="flex-1 min-w-0 border-none outline-none bg-transparent text-[14.5px] text-ink placeholder:text-ink/[42%]"
          />
          <button
            type="button"
            onClick={onSubmit}
            disabled={disabled}
            aria-label="Send"
            className="flex-none w-[38px] h-[38px] rounded-[10px] bg-ink text-surface text-base flex items-center justify-center disabled:opacity-50"
          >
            ↑
          </button>
        </div>
        <p className="mt-2 mx-1 text-[11px] text-ink/[42%] text-center">
          Nyay gives legal information, not legal advice. For your situation, talk to a lawyer.
        </p>
      </div>
    </footer>
  );
}
