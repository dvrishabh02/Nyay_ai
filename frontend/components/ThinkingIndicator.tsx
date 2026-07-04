import Avatar from "@/components/Avatar";

export default function ThinkingIndicator() {
  return (
    <div className="flex gap-3 items-center">
      <Avatar />
      <div className="flex gap-[5px] bg-surface border border-ink/[9%] rounded-[4px_16px_16px_16px] px-4 py-[15px]">
        <span className="w-[7px] h-[7px] rounded-full bg-ink animate-ny-blink" />
        <span
          className="w-[7px] h-[7px] rounded-full bg-ink animate-ny-blink"
          style={{ animationDelay: "0.2s" }}
        />
        <span
          className="w-[7px] h-[7px] rounded-full bg-ink animate-ny-blink"
          style={{ animationDelay: "0.4s" }}
        />
      </div>
    </div>
  );
}
