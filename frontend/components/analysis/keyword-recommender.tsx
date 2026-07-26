"use client";

import { Key, Sparkles, PlusCircle, ArrowRight, CheckCircle2, ShieldAlert } from "lucide-react";
import type { Evidence } from "@/lib/types";

interface KeywordRecommenderProps {
  evidenceList: Evidence[];
  onApplyRewriter: () => void;
}

export function KeywordRecommender({ evidenceList, onApplyRewriter }: KeywordRecommenderProps) {
  // Extract missing skills safely
  const missingSkillEvidence = evidenceList.filter(
    (e) => !e.passed && (e.criterion === "required_skill_present" || e.criterion === "preferred_skill_present")
  );

  const passedSkillEvidence = evidenceList.filter(
    (e) => e.passed && (e.criterion === "required_skill_present" || e.criterion === "preferred_skill_present")
  );

  // Clean helper to extract pure skill name without malformed regex artifacts
  const cleanSkillName = (ev: Evidence) => {
    if (ev.expected_value && typeof ev.expected_value === "string" && ev.expected_value.length < 40) {
      return ev.expected_value;
    }
    const match = ev.description.match(/skill\s+'([^']+)'/i);
    if (match && match[1]) {
      return match[1];
    }
    return ev.expected_value ? String(ev.expected_value) : "Required Competency";
  };

  const getSuggestedPhrase = (skillName: string) => {
    return `Spearheaded strategic deliverables utilizing ${skillName} to optimize operational performance and throughput.`;
  };

  return (
    <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 rounded-3xl space-y-6 shadow-lg dark:shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-[10px] font-mono rounded bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 uppercase font-semibold">
              Real-Time Keyword Audit
            </span>
          </div>
          <h3 className="font-display font-extrabold text-slate-900 dark:text-slate-100 text-lg flex items-center gap-2 mt-1">
            <Key className="w-5 h-5 text-emerald-600 dark:text-emerald-400" /> ATS Keyword Optimization Engine
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Identify exact missing ATS keywords and inject recommended phrasing to clear candidate screening filters.
          </p>
        </div>

        {missingSkillEvidence.length > 0 && (
          <button
            onClick={onApplyRewriter}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 text-xs font-extrabold shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-all shrink-0 self-start sm:self-auto cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> Auto-Inject in AI Rewriter <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Verified Found Skills */}
      {passedSkillEvidence.length > 0 && (
        <div className="space-y-2">
          <span className="text-[11px] font-mono uppercase text-emerald-700 dark:text-emerald-400 tracking-wider font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Verified Found Keywords ({passedSkillEvidence.length}):
          </span>
          <div className="flex flex-wrap gap-2 pt-1">
            {passedSkillEvidence.map((e, idx) => {
              const skillName = cleanSkillName(e);
              return (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 text-xs font-mono font-medium flex items-center gap-1.5 shadow-xs"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  {skillName}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Missing Keywords Section */}
      <div className="space-y-3 pt-2">
        <span className="text-[11px] font-mono uppercase text-rose-600 dark:text-rose-400 tracking-wider font-bold flex items-center gap-1.5">
          <ShieldAlert className="w-4 h-4 text-rose-600 dark:text-rose-400" /> Missing High-Impact Keywords ({missingSkillEvidence.length}):
        </span>

        {missingSkillEvidence.length === 0 ? (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs flex items-center gap-2 font-mono font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" /> 100% Keyword Alignment! Your resume contains all mandatory job description skills.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[420px] overflow-y-auto pr-1">
            {missingSkillEvidence.map((ev, i) => {
              const rawKeyword = cleanSkillName(ev);
              const isRequired = ev.criterion.includes("required");

              return (
                <div
                  key={i}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200/90 dark:border-slate-800 flex flex-col justify-between gap-3 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-xs"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="px-3 py-1 rounded-xl bg-rose-500/10 dark:bg-rose-500/20 text-rose-700 dark:text-rose-300 border border-rose-500/30 text-xs font-mono font-bold flex items-center gap-1.5">
                      <PlusCircle className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" /> Missing: {rawKeyword}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                      {isRequired ? "Required" : "Preferred"}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-300 font-sans leading-relaxed">
                    <span className="text-[10px] font-mono text-emerald-700 dark:text-emerald-400 font-bold uppercase block mb-1">
                      Recommended Bullet Placement:
                    </span>
                    &ldquo;{getSuggestedPhrase(rawKeyword)}&rdquo;
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
