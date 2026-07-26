import { formatEvidenceValue } from "@/lib/format";
import type { Evidence } from "@/lib/types";

export function EvidenceRow({ evidence, index }: { evidence: Evidence; index: number }) {
  const isPass = evidence.passed;

  return (
    <div
      className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200/90 dark:border-slate-800/90 hover:border-slate-300 dark:hover:border-slate-700 transition-all mb-3 shadow-xs"
      style={{ animationDelay: `${Math.min(index, 8) * 40}ms` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
              isPass
                ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 border border-emerald-500/40"
                : "bg-rose-500/20 text-rose-700 dark:text-rose-400 border border-rose-500/40"
            }`}
          >
            {isPass ? "✓" : "✕"}
          </span>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 leading-snug">{evidence.description}</h4>
            <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
              {evidence.criterion}
            </span>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1 shrink-0">
          <span
            className={`px-2.5 py-0.5 text-[10px] font-mono font-bold rounded-lg ${
              isPass
                ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30"
                : "bg-rose-500/10 dark:bg-rose-500/20 text-rose-800 dark:text-rose-300 border border-rose-500/30"
            }`}
          >
            {isPass ? "VERIFIED" : "FLAGGED GAP"}
          </span>
          <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 font-semibold">
            Weight: {evidence.weight.toFixed(1)}
          </span>
        </div>
      </div>

      {/* Found vs Expected Comparison Grid */}
      <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
        <div className="p-3 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] uppercase font-bold block mb-1">Found in Candidate Profile:</span>
          <span className="text-emerald-700 dark:text-emerald-300 font-bold break-all">
            {formatEvidenceValue(evidence.found_value)}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
          <span className="text-slate-500 dark:text-slate-400 text-[10px] uppercase font-bold block mb-1">Expected Criteria:</span>
          <span className="text-slate-900 dark:text-slate-200 font-bold break-all">
            {formatEvidenceValue(evidence.expected_value)}
          </span>
        </div>
      </div>

      {/* Source Span Callout */}
      {evidence.source_span && (
        <div className="mt-3 p-3 rounded-xl bg-slate-100 dark:bg-slate-900/70 border-l-4 border-emerald-500 text-xs text-slate-700 dark:text-slate-300 font-sans leading-relaxed">
          <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase block font-bold mb-0.5">Evidence Proof Span:</span>
          &ldquo;{evidence.source_span}&rdquo;
        </div>
      )}
    </div>
  );
}
