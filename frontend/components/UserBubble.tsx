export default function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[82%] sm:max-w-[74%] bg-ink text-canvas px-[17px] py-[13px] rounded-[18px_18px_4px_18px] text-[15px] leading-[1.5]">
        {text}
      </div>
    </div>
  );
}
