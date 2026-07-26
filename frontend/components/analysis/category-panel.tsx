"use client";

import { ChevronDown, CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { useState } from "react";
import { EvidenceRow } from "@/components/analysis/evidence-row";
import { formatCategoryLabel, scoreTier } from "@/lib/format";
import type { CategoryScore } from "@/lib/types";

export function CategoryPanel({ categoryScore }: { categoryScore: CategoryScore }) {
  const [isOpen, setIsOpen] = useState(false);
  const tier = scoreTier(categoryScore.score_percent);
  const failedCount = categoryScore.evidence.filter((e) => !e.passed).length;
  const scoreRound = Math.round(categoryScore.score_percent);

  let barClass = "bg-emerald-500";
  let badgeClass = "badge-pass";
  if (tier === "warn") {
    barClass = "bg-amber-500";
    badgeClass = "badge-warn";
  } else if (tier === "fail") {
    barClass = "bg-rose-500";
    badgeClass = "badge-fail";
  }

  return (
    <div className="glass-card bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden mb-3">
      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left hover:bg-slate-800/50 transition-colors"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-3 min-w-[160px]">
          {tier === "pass" ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          ) : tier === "warn" ? (
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
          ) : (
            <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
          )}
          <span className="font-display font-medium text-sm text-slate-100">
            {formatCategoryLabel(categoryScore.category)}
          </span>
        </div>

        <div className="flex-1 max-w-md hidden sm:block">
          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${barClass}`}
              style={{ width: `${scoreRound}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-md font-mono ${badgeClass}`}>
            {scoreRound}%
          </span>
          {failedCount > 0 && (
            <span className="text-xs text-rose-400 font-mono hidden md:inline">
              {failedCount} flagged
            </span>
          )}
          <ChevronDown
            className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </div>
      </button>

      {isOpen && (
        <div className="px-5 py-4 border-t border-slate-800/80 bg-slate-950/40">
          <div className="mb-2 text-xs font-mono text-slate-400 uppercase tracking-wider">
            Detailed Evidence & Evaluation:
          </div>
          {categoryScore.evidence.map((evidence, i) => (
            <EvidenceRow key={`${evidence.criterion}-${i}`} evidence={evidence} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
