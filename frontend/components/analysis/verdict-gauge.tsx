"use client";

import { useEffect, useState } from "react";
import { scoreTier } from "@/lib/format";
import { Gauge } from "lucide-react";

export function VerdictGauge({ scorePercent }: { scorePercent: number }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const tier = scoreTier(scorePercent);

  useEffect(() => {
    const timeout = setTimeout(() => setAnimatedScore(scorePercent), 80);
    return () => clearTimeout(timeout);
  }, [scorePercent]);

  const roundedScore = Math.round(animatedScore);
  const needleAngle = -90 + (roundedScore / 100) * 180;
  const percentile = Math.min(99, Math.max(5, Math.round((roundedScore / 100) ** 1.4 * 100)));

  let strokeColor = "#10b981"; // Emerald
  let bgGlowClass = "from-emerald-50/50 via-white to-slate-50 border-emerald-500/30 dark:from-emerald-950/40 dark:via-slate-900/90 dark:to-slate-950 dark:border-emerald-500/40";
  let tierLabel = "Strong ATS Match";
  let badgeClass = "bg-emerald-500/10 text-emerald-800 dark:text-emerald-300 border-emerald-500/30 dark:border-emerald-500/40";
  let needleColor = "fill-emerald-600 dark:fill-emerald-400 stroke-emerald-500 dark:stroke-emerald-300";
  let scoreTextColor = "text-emerald-700 dark:text-emerald-400";
  let glowBadgeBg = "bg-emerald-500/10 border-emerald-500/30";

  if (tier === "warn") {
    strokeColor = "#f59e0b"; // Amber
    bgGlowClass = "from-amber-50/50 via-white to-slate-50 border-amber-500/30 dark:from-amber-950/40 dark:via-slate-900/90 dark:to-slate-950 dark:border-amber-500/40";
    tierLabel = "Moderate ATS Match";
    badgeClass = "bg-amber-500/10 text-amber-800 dark:text-amber-300 border-amber-500/30 dark:border-amber-500/40";
    needleColor = "fill-amber-600 dark:fill-amber-400 stroke-amber-500 dark:stroke-amber-300";
    scoreTextColor = "text-amber-700 dark:text-amber-400";
    glowBadgeBg = "bg-amber-500/10 border-amber-500/30";
  } else if (tier === "fail") {
    strokeColor = "#f43f5e"; // Rose
    bgGlowClass = "from-rose-50/50 via-white to-slate-50 border-rose-500/30 dark:from-rose-950/40 dark:via-slate-900/90 dark:to-slate-950 dark:border-rose-500/40";
    tierLabel = "Needs Optimization";
    badgeClass = "bg-rose-500/10 text-rose-800 dark:text-rose-300 border-rose-500/30 dark:border-rose-500/40";
    needleColor = "fill-rose-600 dark:fill-rose-400 stroke-rose-500 dark:stroke-rose-300";
    scoreTextColor = "text-rose-700 dark:text-rose-400";
    glowBadgeBg = "bg-rose-500/10 border-rose-500/30";
  }

  const dashArray = 220;
  const dashOffset = dashArray - (dashArray * roundedScore) / 100;

  return (
    <div className={`p-6 rounded-3xl glass-card border bg-gradient-to-b ${bgGlowClass} flex flex-col items-center justify-between text-center relative overflow-hidden shadow-lg dark:shadow-2xl h-full min-h-[380px]`}>
      {/* Top Header Badge */}
      <div className="w-full flex items-center justify-between gap-2 border-b border-slate-200/80 dark:border-slate-800/80 pb-3 mb-2">
        <span className="text-[11px] font-mono text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5 font-bold">
          <Gauge className={`w-4 h-4 ${scoreTextColor}`} /> Executive ATS ScoreCard
        </span>
        <div className="flex items-center gap-1.5">
          <span className="px-2.5 py-0.5 text-[10px] font-mono rounded-lg bg-slate-100 dark:bg-slate-800/90 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 font-semibold">
            Top {100 - percentile}% Applicant
          </span>
          <span className={`px-2.5 py-0.5 text-[11px] font-bold rounded-lg uppercase tracking-wider border ${badgeClass}`}>
            {tierLabel}
          </span>
        </div>
      </div>

      {/* Speedometer Gauge Arc */}
      <div className="w-64 h-32 flex items-center justify-center relative my-2">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 200 115">
          <defs>
            <linearGradient id="speedoTrackGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f43f5e" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>

          {/* Background Semi-Circle Track */}
          <path
            d="M 25 95 A 75 75 0 0 1 175 95"
            fill="none"
            className="stroke-slate-200 dark:stroke-slate-800"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Gradient Active Arc */}
          <path
            d="M 25 95 A 75 75 0 0 1 175 95"
            fill="none"
            stroke="url(#speedoTrackGrad)"
            strokeWidth="14"
            strokeDasharray={dashArray}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />

          {/* Speedometer Ticks */}
          <text x="18" y="112" fill="currentColor" className="text-slate-400 dark:text-slate-500" fontSize="10" fontFamily="monospace" textAnchor="middle">0%</text>
          <text x="45" y="38" fill="currentColor" className="text-slate-400 dark:text-slate-500" fontSize="10" fontFamily="monospace" textAnchor="middle">25%</text>
          <text x="100" y="14" fill="currentColor" className="text-slate-400 dark:text-slate-500" fontSize="10" fontFamily="monospace" textAnchor="middle">50%</text>
          <text x="155" y="38" fill="currentColor" className="text-slate-400 dark:text-slate-500" fontSize="10" fontFamily="monospace" textAnchor="middle">75%</text>
          <text x="182" y="112" fill="currentColor" className="text-slate-400 dark:text-slate-500" fontSize="10" fontFamily="monospace" textAnchor="middle">100%</text>

          {/* Dynamic Moving Needle */}
          <g
            transform={`rotate(${needleAngle}, 100, 95)`}
            className="transition-transform duration-1000 ease-out"
          >
            <polygon points="97,95 103,95 100,24" className={needleColor} />
            <circle cx="100" cy="95" r="7" fill="#ffffff" stroke={strokeColor} strokeWidth="3" className="dark:fill-slate-900" />
            <circle cx="100" cy="95" r="3" fill={strokeColor} />
          </g>
        </svg>
      </div>

      {/* Digital Score Display */}
      <div className={`px-6 py-2 rounded-2xl border backdrop-blur-md ${glowBadgeBg} flex flex-col items-center justify-center shadow-md transition-all w-full max-w-[220px]`}>
        <div className={`text-4xl font-black font-display tracking-tight flex items-baseline justify-center gap-1 ${scoreTextColor}`}>
          <span>{roundedScore}</span>
          <span className={`text-2xl font-bold ${scoreTextColor}`}>%</span>
        </div>
        <span className="text-[10px] uppercase font-mono tracking-widest text-slate-700 dark:text-slate-300 font-extrabold">
          Overall ATS Match Score
        </span>
      </div>

      {/* Narrative Score Assessment */}
      <p className="text-xs text-slate-700 dark:text-slate-300 max-w-xs mt-2 leading-relaxed font-medium">
        {roundedScore >= 75
          ? "Target criteria satisfied! High probability of clearing automated ATS screeners."
          : roundedScore >= 50
          ? "Moderate match. Core qualifications present, but targeted keyword optimizations will boost ranking."
          : "Needs optimization. Key required skills or contact information are missing."}
      </p>

      {/* 8-Tier Enterprise ATS Category Breakdown Pills */}
      <div className="w-full mt-3 pt-3 border-t border-slate-200/80 dark:border-slate-800/80 grid grid-cols-4 gap-1 text-[9px] font-mono text-slate-600 dark:text-slate-400 font-semibold">
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Keyword: 30%</span>
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Skills: 20%</span>
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Exp: 15%</span>
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Edu: 10%</span>
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Layout: 10%</span>
        <span className="p-1 rounded bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50">Verbs: 5%</span>
        <span className="p-1 rounded bg-slate-800/50 border border-slate-700/50">Clarity: 5%</span>
        <span className="p-1 rounded bg-slate-800/50 border border-slate-700/50">Reqs: 5%</span>
      </div>
    </div>
  );
}
