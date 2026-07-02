export default function DisclaimerFooter({ disclaimer }: { disclaimer: string }) {
  return (
    <div className="sticky bottom-0 border-t border-slate-800 bg-slate-950/95 px-6 py-3 backdrop-blur no-print">
      <p className="mx-auto max-w-6xl text-[11px] leading-relaxed text-slate-500">{disclaimer}</p>
    </div>
  )
}
