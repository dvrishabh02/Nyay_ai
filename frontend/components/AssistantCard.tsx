import Avatar from "@/components/Avatar";
import type { AssistantCardData } from "@/lib/types";

export default function AssistantCard({ data }: { data: AssistantCardData }) {
  return (
    <div className="flex gap-3 items-start">
      <Avatar />
      <div className="flex-1 min-w-0 bg-surface border border-ink/[9%] rounded-[4px_18px_18px_18px] px-5 pt-[18px] pb-5">
        <div className="flex items-center gap-[9px] mb-3.5">
          <div className="flex gap-[3px]">
            {[1, 2, 3].map((i) => (
              <span
                key={i}
                className={`w-4 h-1.5 rounded-[3px] ${i <= data.barsFilled ? "bg-ink" : "bg-ink/[18%]"}`}
              />
            ))}
          </div>
          <span className="text-[11.5px] font-semibold tracking-[0.04em] uppercase text-ink/60">
            {data.confLabel}
          </span>
        </div>

        <p className="font-serif text-[20px] leading-[1.4] font-medium tracking-[-0.01em]">
          {data.lead}
        </p>

        {data.sources.length > 0 && (
          <div className="border-t border-ink/[8%] pt-3.5 mt-[18px]">
            <div className="text-[10.5px] font-semibold tracking-[0.06em] uppercase text-ink/45 mb-[9px]">
              Based on
            </div>
            <div className="flex flex-wrap gap-2">
              {data.sources.map((src, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 border border-ink/[14%] rounded-[9px] px-[11px] py-[7px]"
                >
                  <span className="text-[10px] font-bold bg-ink text-surface rounded-[5px] px-[5px] py-0.5">
                    {src.tag}
                  </span>
                  <span className="text-[12.5px] font-medium">{src.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
