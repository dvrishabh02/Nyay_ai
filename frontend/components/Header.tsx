export default function Header() {
  return (
    <header className="flex-none bg-surface border-b border-ink/[8%]">
      <div className="max-w-[820px] mx-auto flex items-center justify-between px-5 py-3.5">
        <div className="flex items-center gap-[11px]">
          <div className="w-9 h-9 rounded-[10px] bg-ink text-surface flex items-center justify-center font-devanagari text-[19px] font-semibold">
            न
          </div>
          <div className="flex flex-col leading-[1.1]">
            <span className="font-bold text-[16px] tracking-[-0.01em]">Nyay</span>
            <span className="text-[11px] text-ink/50">Know your rights</span>
          </div>
        </div>
        <span className="text-xs text-ink/50 whitespace-nowrap">7 of 10 free left</span>
      </div>
    </header>
  );
}
