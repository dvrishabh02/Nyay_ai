import Avatar from "@/components/Avatar";

export default function ErrorCard({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="flex gap-3 items-start">
      <Avatar />
      <div className="flex-1 min-w-0 bg-surface border border-ink/[9%] rounded-[4px_18px_18px_18px] px-5 pt-[18px] pb-5">
        <p className="text-[15px] leading-[1.55] text-ink/[82%]">{message}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-3.5 border border-ink/[18%] bg-surface text-ink rounded-full px-3.5 py-2 text-[13px] font-medium hover:bg-ink hover:text-surface hover:border-ink transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
