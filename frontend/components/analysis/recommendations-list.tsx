"use client";

import { Sparkles, ArrowRight, Lightbulb, CheckCircle2 } from "lucide-react";
import { formatCategoryLabel } from "@/lib/format";
import type { Recommendation } from "@/lib/types";

export function RecommendationsList({
  recommendations,
  onApplyRewriter,
}: {
  recommendations: Recommendation[];
  onApplyRewriter?: () => void;
}) {
  if (recommendations.length === 0) {
    return (
      <div className="p-6 rounded-3xl glass-card bg-emerald-500/10 dark:bg-emerald-950/20 border border-emerald-500/30 text-center h-full flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-3 border border-emerald-500/40 shadow-md">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h3 className="font-display font-extrabold text-emerald-800 dark:text-emerald-300 text-lg">100% Criteria Passed!</h3>
        <p className="text-xs text-slate-700 dark:text-slate-300 max-w-sm mx-auto mt-1 leading-relaxed">
          No critical gaps detected — your resume profile satisfies all requirements for this position.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 rounded-3xl glass-card border border-slate-200/90 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 space-y-4 shadow-lg dark:shadow-2xl h-full flex flex-col justify-between">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200/80 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-[10px] font-mono rounded bg-amber-500/10 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 uppercase font-semibold">
              Action Plan
            </span>
          </div>
          <h3 className="font-display font-extrabold text-slate-900 dark:text-slate-100 text-lg flex items-center gap-2 mt-1">
            <Lightbulb className="w-5 h-5 text-amber-600 dark:text-amber-400" /> Executive Recommendations
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Prioritized steps to maximize your ATS pass probability.
          </p>
        </div>

        {onApplyRewriter && (
          <button
            onClick={onApplyRewriter}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-xs font-extrabold text-slate-950 shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-all shrink-0 self-start sm:self-auto cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> Rewrite Resume <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
        {recommendations.map((rec, i) => (
          <div
            key={`${rec.criterion}-${i}`}
            className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200/90 dark:border-slate-800/90 flex items-start gap-3.5 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-xs"
          >
            <div className="mt-0.5 p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-[11px] font-mono uppercase tracking-wider text-slate-900 dark:text-slate-200 font-bold">
                  {formatCategoryLabel(rec.category)}
                </span>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded-md bg-amber-500/10 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 font-bold">
                  HIGH IMPACT
                </span>
              </div>
              <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">{rec.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
