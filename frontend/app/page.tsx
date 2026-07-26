"use client";

import { useState, useRef, useEffect } from "react";
import { Sparkles, ScanLine, Layout, ArrowRight, CheckCircle2, RefreshCw, AlertCircle, LogIn, UserPlus, Shield, Cpu, Binary, Lock, FileText, Gauge } from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/layout/navbar";
import { ResumeUpload } from "@/components/analysis/resume-upload";
import { DocumentStats } from "@/components/analysis/document-stats";
import { VerdictGauge } from "@/components/analysis/verdict-gauge";
import { CategoryPanel } from "@/components/analysis/category-panel";
import { RecommendationsList } from "@/components/analysis/recommendations-list";
import { KeywordRecommender } from "@/components/analysis/keyword-recommender";
import { ScanningOverlay } from "@/components/analysis/scanning-overlay";
import { ResumeRewriter } from "@/components/rewriter/resume-rewriter";
import { AtsBuilder } from "@/components/builder/ats-builder";
import { useAuth } from "@/components/auth/auth-provider";
import { api } from "@/lib/api-client";
import type { AnalysisResponse } from "@/lib/types";

const SAMPLE_JOB_DESCRIPTION = `Senior Full-Stack Software Engineer

Role Overview:
We are seeking a Senior Full-Stack Software Engineer to build scalable microservices and modern frontend applications.

Required Qualifications:
- 4+ years of experience with Python (FastAPI, Django, or Flask)
- Proficiency in JavaScript/TypeScript (React, Next.js, or Node.js)
- Solid database experience with PostgreSQL and Redis caching
- Hands-on experience with Docker, Kubernetes, and AWS cloud infrastructure
- Strong understanding of RESTful API design and CI/CD automation

Preferred:
- Experience with ATS resume optimization systems and AI/NLP tools
- Bachelor's degree in Computer Science or Software Engineering`;

export default function WorkspacePage() {
  const { user, login, register } = useAuth();
  const [authMode, setAuthMode] = useState<"signin" | "signup">("signin");

  // Auth Form State for Gateway Page
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isSubmittingAuth, setIsSubmittingAuth] = useState(false);

  const [activeTab, setActiveTab] = useState<"scanner" | "rewriter" | "builder">("scanner");
  const [selectedPreset, setSelectedPreset] = useState<"tech" | "marketing" | "healthcare" | "finance">("tech");
  const [scannerStage, setScannerStage] = useState<"setup" | "results">("setup");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescriptionText, setJobDescriptionText] = useState(SAMPLE_JOB_DESCRIPTION);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasScannedCurrentInput, setHasScannedCurrentInput] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setAuthError("Please fill in all required email and password fields.");
      return;
    }

    setAuthError(null);
    setIsSubmittingAuth(true);

    try {
      if (authMode === "signup") {
        if (!fullName) {
          setAuthError("Please enter your full name.");
          setIsSubmittingAuth(false);
          return;
        }
        await register(email, password, fullName);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setAuthError(err?.message || "Authentication failed. Please verify your email and password.");
    } finally {
      setIsSubmittingAuth(false);
    }
  };

  // Multi-Industry Presets (Tech, Marketing, Healthcare, Finance)
  const handleLoadPreset = (field: "tech" | "marketing" | "healthcare" | "finance") => {
    setSelectedPreset(field);
    let name = "Alex Rivera";
    let text = "";
    let jd = "";

    if (field === "marketing") {
      name = "Sarah Jenkins";
      text = "Sarah Jenkins\nNew York, NY | (555) 890-1234 | sjenkins@example.com\n\nSummary:\nSenior Marketing & Growth Director with 7+ years of experience driving multi-channel digital campaigns.\n\nExperience:\nMarketing Manager - Growth Media (3 years)\n- Increased organic search traffic by 150% through SEO content optimization.\n- Managed $500k ad spend across Google Ads, Meta, and LinkedIn with 4.2x ROAS.\n\nSkills:\nDigital Marketing, SEO, SEM, Content Strategy, Google Analytics, Brand Strategy, CRM, Hubspot";
      jd = "Senior Growth Marketing Manager\n\nRequirements:\n- 5+ years of digital marketing experience\n- Proficiency in Google Analytics, SEO, and paid ad campaign management\n- Demonstrated track record of scaling organic traffic and ROI\n- Bachelor's degree in Marketing, Business, or Communications";
    } else if (field === "healthcare") {
      name = "David Chen";
      text = "David Chen, RN\nBoston, MA | (555) 678-9012 | dchen@example.com\n\nSummary:\nRegistered Nurse with 5+ years of clinical emergency care and patient management experience.\n\nExperience:\nStaff Nurse - General Hospital (4 years)\n- Administered acute patient care across 30+ bed unit maintaining 99% patient satisfaction.\n- Supervised clinical compliance and medical records documentation.\n\nSkills:\nClinical Care, Patient Assessment, Emergency Nursing, Electronic Health Records (EHR), CPR/BLS, Medication Administration";
      jd = "Registered Nurse (RN) - Clinical Care\n\nRequirements:\n- Active RN license with BSN degree\n- 3+ years of clinical hospital experience\n- Proficiency in Electronic Health Records (EHR) systems\n- Strong patient assessment and communication skills";
    } else if (field === "finance") {
      name = "Marcus Vance";
      text = "Marcus Vance\nChicago, IL | (555) 456-7890 | mvance@example.com\n\nSummary:\nSenior Financial Analyst specializing in corporate forecasting, budget planning, and M&A valuation.\n\nExperience:\nFinancial Analyst - Vertex Capital (4 years)\n- Built 3-statement financial models predicting annual revenue variance within 2%.\n- Analyzed quarterly financial performance for $50M portfolio.\n\nSkills:\nFinancial Modeling, Valuation, Forecasting, Excel, SQL, Financial Reporting, Risk Analysis, Budgeting";
      jd = "Senior Financial Analyst\n\nRequirements:\n- 4+ years of corporate finance or investment banking experience\n- Advanced financial modeling and forecasting skills in Excel and SQL\n- Strong understanding of financial statements and variance reporting\n- Bachelor's degree in Finance, Economics, or Accounting";
    } else {
      name = "Alex Devon";
      text = `Alex Devon\nSeattle, WA | (555) 234-5678 | alex@example.com\n\nSummary:\nSenior Software Engineer with 5 years experience building scalable backend APIs and web applications.\n\nExperience:\nSenior Developer - Tech Corp (3 years)\n- Built Python FastAPI microservices and React frontend apps.\n\nSkills:\nPython, JavaScript, React, PostgreSQL, Docker, Git, REST APIs`;
      jd = SAMPLE_JOB_DESCRIPTION;
    }

    const sampleBlob = new Blob([text], { type: "text/plain" });
    const sampleFile = new File([sampleBlob], `${name.toLowerCase().replace(" ", "_")}_resume.pdf`, { type: "application/pdf" });
    setResumeFile(sampleFile);
    setJobDescriptionText(jd);
    setHasScannedCurrentInput(false);
  };

  const resultsRef = useRef<HTMLDivElement>(null);

  // Auto Scroll UP instantly when resume file or job description is provided
  useEffect(() => {
    if (resumeFile || jobDescriptionText) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [resumeFile]);

  useEffect(() => {
    if (result) {
      const doScroll = () => {
        const target = document.getElementById("ats-results-section") || resultsRef.current;
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          window.scrollTo({ top: 500, behavior: "smooth" });
        }
      };

      const timer1 = setTimeout(doScroll, 150);
      const timer2 = setTimeout(doScroll, 400);
      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
      };
    }
  }, [result]);

  const handleAnalyze = async () => {
    if (!resumeFile) {
      setError("Please select or upload your resume file (PDF, DOCX, or PNG/JPG image) first.");
      return;
    }

    const effectiveJd = jobDescriptionText.trim().length >= 10
      ? jobDescriptionText
      : "General ATS Health Audit: Evaluate overall candidate resume layout, contact info header, experience impact density, core skills, projects, and education structure.";

    setError(null);
    setIsAnalyzing(true);
    setResult(null);

    try {
      const response = await api.analyses.analyzeSync(resumeFile, effectiveJd);
      setResult(response);
      setHasScannedCurrentInput(true);
    } catch (err: any) {
      setError(err?.message || "Error processing resume analysis. Please verify your file is readable and try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isWorkspaceUnlocked = Boolean(user);

  return (
    <div className="min-h-screen pb-16">
      {/* High-Tech Futuristic Live Scanning Overlay */}
      <ScanningOverlay isAnalyzing={isAnalyzing} fileName={resumeFile?.name} />

      <Navbar />

      {/* PROFESSIONAL ENTERPRISE AUTH GATEWAY VIEW (When not logged in) */}
      {!isWorkspaceUnlocked ? (
        <main className="mx-auto max-w-6xl px-6 pt-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Content (7 Cols) */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-mono font-semibold">
                <Sparkles className="w-3.5 h-3.5" /> Next-Gen AI Resume Platform
              </div>
              <h1 className="font-display text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-slate-100 leading-tight tracking-tight">
                Optimize Your Resume for <span className="gradient-text-emerald">Enterprise ATS Systems</span>
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-xl">
                Get instant evidence scoring, missing keyword detection, and AI-powered bullet rewrites tailored to target job descriptions.
              </p>
            </div>

            {/* Right Gateway Form Card (5 Cols) */}
            <div className="lg:col-span-5">
              <div className="p-8 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 rounded-3xl shadow-lg dark:shadow-2xl space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setAuthMode("signin")}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                        authMode === "signin"
                          ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-300 dark:border-slate-700 shadow-xs"
                          : "text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                      }`}
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => setAuthMode("signup")}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                        authMode === "signup"
                          ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-300 dark:border-slate-700 shadow-xs"
                          : "text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                      }`}
                    >
                      Create Account
                    </button>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-700 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/30 font-semibold">
                    Instant Access
                  </span>
                </div>

                {authError && (
                  <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" /> {authError}
                  </div>
                )}

                <form onSubmit={handleAuthSubmit} className="space-y-4">
                  {authMode === "signup" && (
                    <div>
                      <label className="block text-xs font-mono uppercase text-slate-600 dark:text-slate-400 mb-1.5 font-semibold">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Alex Rivera"
                        className="w-full p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input font-mono focus:border-emerald-500 transition-all outline-none"
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-mono uppercase text-slate-600 dark:text-slate-400 mb-1.5 font-semibold">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="alex.rivera@example.com"
                      className="w-full p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input font-mono focus:border-emerald-500 transition-all outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-mono uppercase text-slate-600 dark:text-slate-400 mb-1.5 font-semibold">
                      Password
                    </label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input font-mono focus:border-emerald-500 transition-all outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmittingAuth}
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-extrabold text-xs uppercase tracking-wider shadow-xl shadow-emerald-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
                  >
                    {isSubmittingAuth ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" /> Authenticating...
                      </>
                    ) : authMode === "signup" ? (
                      <>
                        <UserPlus className="w-4 h-4" /> Create Workspace & Enter
                      </>
                    ) : (
                      <>
                        <LogIn className="w-4 h-4" /> Sign In To Workspace
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </main>
      ) : (
        /* WORKSPACE WORKFLOW VIEW (When Logged In) */
        <main className="mx-auto max-w-7xl px-6 pt-6 space-y-6">
          {/* Workspace Top Header Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 rounded-2xl shadow-lg shadow-slate-200/50 dark:shadow-2xl">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-bold text-sm font-mono shadow-sm">
                AI
              </div>
              <div>
                <h2 className="font-display font-bold text-slate-900 dark:text-slate-100 text-sm flex items-center gap-2">
                  Candidate Workspace
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Welcome, <span className="text-slate-800 dark:text-slate-200 font-semibold">{user?.full_name || user?.email}</span>
                </p>
              </div>
            </div>

            {/* Navigation Tabs (Section 1, Section 2, Section 3) */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800">
              <button
                onClick={() => setActiveTab("scanner")}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === "scanner"
                    ? "bg-emerald-500 text-slate-950 shadow-md font-extrabold"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                }`}
              >
                <ScanLine className="w-3.5 h-3.5" /> Section 1: ATS Audit Scanner
              </button>

              <button
                onClick={() => setActiveTab("rewriter")}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === "rewriter"
                    ? "bg-emerald-500 text-slate-950 shadow-md font-extrabold"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" /> Section 2: Reasonable AI Rewriter
              </button>

              <button
                onClick={() => setActiveTab("builder")}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
                  activeTab === "builder"
                    ? "bg-emerald-500 text-slate-950 shadow-md font-extrabold"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                }`}
              >
                <Layout className="w-3.5 h-3.5" /> Section 3: ATS Resume Builder
              </button>
            </div>

            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-x-auto">
              <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase tracking-wider px-2 shrink-0 font-semibold">Presets:</span>
              {[
                { id: "tech", label: "Tech / Eng" },
                { id: "marketing", label: "Marketing" },
                { id: "healthcare", label: "Healthcare" },
                { id: "finance", label: "Finance" },
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => handleLoadPreset(p.id as any)}
                  className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-[11px] font-semibold transition-all border border-slate-200 dark:border-slate-700/60 shrink-0 shadow-xs"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab 1: Scanner & Optimizer */}
          {activeTab === "scanner" && (
            <div className="space-y-6 animate-fade-in">
              {/* STAGE 1: Setup View */}
              {(scannerStage === "setup" || !result) && (
                <div className="space-y-6 animate-fade-in">
                  {/* Input Section Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left Column: Upload (5 Cols) */}
                    <div className="lg:col-span-5 space-y-4">
                      <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800">
                        <h3 className="font-display font-bold text-sm text-slate-900 dark:text-slate-100 mb-1">
                          1. Upload Candidate Resume
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
                          Accepts PDF, DOCX, or PNG/JPG resume scans.
                        </p>
                        <ResumeUpload
                          file={resumeFile}
                          onFileSelected={(f) => {
                            setResumeFile(f);
                            setHasScannedCurrentInput(false);
                          }}
                        />
                      </div>
                    </div>

                    {/* Right Column: Job Description (7 Cols) */}
                    <div className="lg:col-span-7 space-y-4">
                      <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 flex flex-col h-full">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-display font-bold text-sm text-slate-900 dark:text-slate-100">
                            2. Target Job Description
                          </h3>
                          <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">
                            {jobDescriptionText.length} chars
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                          Paste target job requirements for evidence matching.
                        </p>

                        <textarea
                          rows={7}
                          value={jobDescriptionText}
                          onChange={(e) => {
                            setJobDescriptionText(e.target.value);
                            setHasScannedCurrentInput(false);
                          }}
                          className="w-full flex-1 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input font-mono leading-relaxed resize-none"
                          placeholder="Paste job description text here (optional)..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* Clean Action Row: Run ATS button presented directly below upload & JD on right side */}
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing || hasScannedCurrentInput}
                      className={`px-6 py-3 rounded-xl font-extrabold text-xs flex items-center gap-2 transition-all ${
                        hasScannedCurrentInput
                          ? "bg-slate-200 dark:bg-slate-800/80 text-slate-400 dark:text-slate-500 border border-slate-300 dark:border-slate-700/60 cursor-not-allowed opacity-50 shadow-none"
                          : "bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20"
                      }`}
                    >
                      {isAnalyzing ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Scanning Resume...
                        </>
                      ) : hasScannedCurrentInput ? (
                        <>
                          ✓ ATS Scan Completed
                        </>
                      ) : (
                        <>
                          Run Real ATS Analysis <ArrowRight className="w-3.5 h-3.5" />
                        </>
                      )}
                    </button>
                  </div>

                  {error && (
                    <div className="p-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 shadow-lg">
                      <AlertCircle className="w-4 h-4 shrink-0" /> {error}
                    </div>
                  )}

                  {/* Pre-Scan Document Diagnostics & Statistics with Audit button in bottom right ONLY AFTER SCAN COMPLETED */}
                  {result && (
                    <DocumentStats
                      file={resumeFile}
                      hasJobDescription={jobDescriptionText.trim().length >= 10}
                      parsedEvidence={result.scorecard.category_scores.flatMap((cs) => cs.evidence)}
                      onNavigateToResults={() => setScannerStage("results")}
                    />
                  )}
                </div>
              )}

              {/* STAGE 2: Analysis Results View */}
              {scannerStage === "results" && result && (
                <div id="ats-results-section" ref={resultsRef} className="space-y-6 animate-fade-in scroll-mt-6">
                  {/* Top Bar with Back to Stage 1 button */}
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <button
                      onClick={() => setScannerStage("setup")}
                      className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-2 transition-all"
                    >
                      ← Back to Stage 1 Setup
                    </button>
                    <span className="text-xs font-mono text-emerald-400 font-bold">
                      Enterprise ATS Audit Verdict: {Math.round(result.scorecard.overall_score)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
                    {/* Speedometer Gauge (5 Cols) */}
                    <div className="lg:col-span-5">
                      <VerdictGauge scorePercent={result.scorecard.overall_score} />
                    </div>

                    {/* Recommendations Cards (7 Cols) */}
                    <div className="lg:col-span-7">
                      <RecommendationsList
                        recommendations={result.recommendations}
                        onApplyRewriter={() => setActiveTab("rewriter")}
                      />
                    </div>
                  </div>

                  {/* Missing Keyword Recommender Card */}
                  <KeywordRecommender
                    evidenceList={result.scorecard.category_scores.flatMap((cs) => cs.evidence)}
                    onApplyRewriter={() => setActiveTab("rewriter")}
                  />

                  {/* Evidence Accordion Panel */}
                  <div className="p-6 glass-card bg-slate-900/90 border border-slate-800 space-y-4 rounded-3xl shadow-2xl">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                      <div>
                        <h3 className="font-display font-bold text-slate-100 text-base">
                          Detailed Evidence Ledger
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Line-by-line proof extracted from your resume against job criteria
                        </p>
                      </div>
                      <span className="text-xs font-mono text-emerald-400">
                        {result.scorecard.category_scores.length} Categories Evaluated
                      </span>
                    </div>

                    {result.scorecard.category_scores.map((cs) => (
                      <CategoryPanel key={cs.category} categoryScore={cs} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: AI Resume Rewriter */}
          {activeTab === "rewriter" && (
            <ResumeRewriter
              resumeFile={resumeFile}
              parsedResumeText={result?.raw_text}
              originalResumeText={resumeFile ? resumeFile.name : "Uploaded Resume"}
              jobDescriptionText={jobDescriptionText}
              recommendations={result?.recommendations || []}
              onBackToScanner={() => setActiveTab("scanner")}
            />
          )}

          {/* Tab 3: ATS Resume Builder */}
          {activeTab === "builder" && (
            <AtsBuilder
              key={selectedPreset}
              activePreset={selectedPreset}
              onSelectPreset={(p) => handleLoadPreset(p)}
              onAuditInScanner={(builtText) => {
                const blob = new Blob([builtText], { type: "text/plain" });
                const file = new File([blob], "built_ats_resume.pdf", { type: "application/pdf" });
                setResumeFile(file);
                setActiveTab("scanner");
              }}
            />
          )}
        </main>
      )}
    </div>
  );
}
