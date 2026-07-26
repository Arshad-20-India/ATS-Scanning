"use client";

import { useEffect, useState } from "react";
import { Cpu, ScanLine } from "lucide-react";

interface ScanningOverlayProps {
  isAnalyzing: boolean;
  fileName?: string;
}

const SCAN_STAGES = [
  { threshold: 20, label: "📄 Extracting Text & Parsing Document Structure...", detail: "pdfplumber OCR & spaCy NLP parsing" },
  { threshold: 45, label: "🧬 Computing 384-Dim Vector Embeddings...", detail: "SentenceTransformers dense vector cosine similarity" },
  { threshold: 75, label: "🔍 Auditing 8-Tier Rule-Based ATS Criteria...", detail: "Greenhouse / Workday / Lever weighted matrix" },
  { threshold: 92, label: "📊 Evaluating Keyword & Metric Density...", detail: "Action verb frequency & quantified impact audit" },
  { threshold: 99, label: "⚡ Finalizing Structured ScoreCard & Ledger...", detail: "Assembling evidence-grounded recommendations" },
];

export function ScanningOverlay({ isAnalyzing, fileName }: ScanningOverlayProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isAnalyzing) {
      setProgress(0);
      return;
    }

    // Realistic smooth asymptotic progress curve
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 30) return prev + 3;
        if (prev < 60) return prev + 2;
        if (prev < 85) return prev + 1;
        if (prev < 95) return prev + 0.5;
        if (prev < 98) return prev + 0.2;
        return 98;
      });
    }, 60);

    return () => clearInterval(interval);
  }, [isAnalyzing]);

  if (!isAnalyzing) return null;

  const activeStage = SCAN_STAGES.find((s) => progress <= s.threshold) ?? SCAN_STAGES[0];
  const currentStage = activeStage ?? { label: "Processing Document...", detail: "Auditing ATS criteria" };
  const displayPercent = Math.min(100, Math.floor(progress));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 dark:bg-slate-950/90 backdrop-blur-xl animate-fade-in p-6">
      {/* Background Ambient Glow */}
      <div className="absolute w-[450px] h-[450px] bg-emerald-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" />

      {/* Main Theme-Adaptable Scanning Card */}
      <div className="relative w-full max-w-lg p-8 bg-white/95 dark:bg-slate-900/95 border border-slate-200/90 dark:border-emerald-500/30 rounded-3xl shadow-2xl space-y-6 text-center overflow-hidden transition-all">
        {/* Top Scanner Pulse Indicator */}
        <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-2 border-emerald-500/20 border-t-emerald-500 animate-spin" />
          <div className="absolute inset-2 rounded-full border border-teal-500/30 border-b-teal-400 animate-spin [animation-duration:3s]" />
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shadow-md shadow-emerald-500/10">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
        </div>

        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 text-[11px] font-mono font-bold mb-2">
            <ScanLine className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 animate-pulse" /> Enterprise ATS Engine Active
          </div>
          <h2 className="text-xl font-display font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
            Scanning Candidate Profile
          </h2>
          <p className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-1 truncate max-w-xs mx-auto">
            {fileName || "Uploaded Resume Document"}
          </p>
        </div>

        {/* Dynamic Progress Indicator Box */}
        <div className="space-y-3 p-4 rounded-2xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200/90 dark:border-slate-800">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-800 dark:text-slate-200 font-sans font-semibold text-left truncate max-w-[280px]">
              {currentStage.label}
            </span>
            <span className="text-emerald-600 dark:text-emerald-400 font-extrabold text-sm shrink-0 font-mono ml-2">
              {displayPercent}%
            </span>
          </div>

          {/* Glow Progress Bar */}
          <div className="h-3 w-full bg-slate-200 dark:bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-300 dark:border-slate-800 relative">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-150 shadow-[0_0_12px_#10b981]"
              style={{ width: `${displayPercent}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 dark:text-slate-400 pt-1 font-medium">
            <span>{currentStage.detail}</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">100% Target</span>
          </div>
        </div>

        {/* 8-Tier Pipeline Badges */}
        <div className="grid grid-cols-4 gap-1.5 pt-1 text-[10px] font-mono font-semibold">
          <div className={`p-1.5 rounded-lg border transition-all ${progress >= 20 ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border-emerald-500/30 dark:border-emerald-500/40 font-bold" : "bg-slate-100 dark:bg-slate-950/60 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-800"}`}>
            Parser
          </div>
          <div className={`p-1.5 rounded-lg border transition-all ${progress >= 45 ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border-emerald-500/30 dark:border-emerald-500/40 font-bold" : "bg-slate-100 dark:bg-slate-950/60 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-800"}`}>
            Embeddings
          </div>
          <div className={`p-1.5 rounded-lg border transition-all ${progress >= 75 ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border-emerald-500/30 dark:border-emerald-500/40 font-bold" : "bg-slate-100 dark:bg-slate-950/60 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-800"}`}>
            8-Tier Audit
          </div>
          <div className={`p-1.5 rounded-lg border transition-all ${progress >= 95 ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border-emerald-500/30 dark:border-emerald-500/40 font-bold" : "bg-slate-100 dark:bg-slate-950/60 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-800"}`}>
            ScoreCard
          </div>
        </div>
      </div>
    </div>
  );
}
