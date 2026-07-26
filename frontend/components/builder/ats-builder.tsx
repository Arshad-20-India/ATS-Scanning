"use client";

import { useState, useEffect } from "react";
import { User, Briefcase, GraduationCap, Award, Code, Sparkles, FolderGit2, Printer, Wand2, Eye, ScanLine } from "lucide-react";

export type TemplateId = "executive" | "modern" | "corporate" | "minimalist";

export type IndustryPreset = "tech" | "marketing" | "healthcare" | "finance";

interface AtsBuilderProps {
  activePreset?: IndustryPreset;
  onSelectPreset?: (preset: IndustryPreset) => void;
  onAuditInScanner?: (builtResumeText: string) => void;
}

const PRESET_DATA: Record<IndustryPreset, any> = {
  tech: {
    fullName: "Alex Devon",
    title: "Senior Full-Stack Software Engineer",
    email: "alex.devon@example.com",
    phone: "(555) 234-5678",
    location: "Seattle, WA",
    linkedin: "linkedin.com/in/alexdevon",
    summary: "Results-driven Senior Full-Stack Software Engineer with 5+ years of experience engineering scalable microservices and high-throughput web applications. Demonstrated track record of optimizing database query latency by 38% and automating multi-cloud CI/CD deployment pipelines.",
    skills: "Python, JavaScript, TypeScript, React, Next.js, Node.js, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, RESTful APIs, Git, CI/CD Automation",
    company: "Tech Corp Solutions",
    jobTitle: "Senior Software Engineer",
    dates: "Jan 2021 – Present",
    experienceBullets: [
      "Engineered core Python & FastAPI microservices handling over 1.2M daily REST API requests with 99.9% uptime.",
      "Optimized PostgreSQL database queries and implemented Redis caching, reducing average response latency by 38%.",
      "Containerized core services using Docker & Kubernetes, streamlining deployment cycles across multi-cloud infrastructure."
    ].join("\n"),
    projectName: "Enterprise Microservice Infrastructure",
    projectDescription: "Architected real-time streaming data pipeline for high-concurrency event processing.",
    projectBullets: [
      "Built asynchronous messaging workers in Python servicing 50,000 events per second.",
      "Implemented comprehensive automated integration test suite in CI/CD pipeline."
    ].join("\n"),
    degree: "B.S. in Computer Science",
    institution: "State University",
    gradYear: "2019",
  },
  marketing: {
    fullName: "Sarah Jenkins",
    title: "Senior Marketing & Growth Director",
    email: "sjenkins@example.com",
    phone: "(555) 890-1234",
    location: "New York, NY",
    linkedin: "linkedin.com/in/sjenkins-growth",
    summary: "Dynamic Senior Growth Marketing Director with 7+ years of experience driving multi-channel digital acquisition campaigns, brand strategy, and revenue optimization across B2B & SaaS markets.",
    skills: "Digital Marketing, SEO, SEM, Paid Search, Content Strategy, Google Analytics 4, Meta Ads, Hubspot CRM, Email Automation, A/B Testing",
    company: "Growth Media Interactive",
    jobTitle: "Senior Growth Marketing Manager",
    dates: "Mar 2020 – Present",
    experienceBullets: [
      "Scaled organic search traffic by 150% YoY through strategic SEO content optimization and technical backlink acquisition.",
      "Managed $500k annual performance marketing budget across Google & LinkedIn Ads, achieving a 4.2x average ROAS.",
      "Spearheaded automated lead nurturing email workflows, increasing qualified sales lead conversion by 28%."
    ].join("\n"),
    projectName: "Omnichannel Acquisition Campaign",
    projectDescription: "Executed multi-channel digital growth campaign for flagship enterprise software product launch.",
    projectBullets: [
      "Generated 12,000+ marketing qualified leads (MQLs) within 90 days of campaign launch.",
      "Optimized landing page conversion rates by 34% using targeted A/B split testing."
    ].join("\n"),
    degree: "B.S. in Marketing & Communications",
    institution: "New York University",
    gradYear: "2017",
  },
  healthcare: {
    fullName: "David Chen, RN",
    title: "Clinical Nurse Specialist & Patient Care Coordinator",
    email: "dchen.rn@example.com",
    phone: "(555) 678-9012",
    location: "Boston, MA",
    linkedin: "linkedin.com/in/dchen-rn",
    summary: "Compassionate Registered Nurse (RN) with 5+ years of clinical emergency care, triage assessment, and patient care management experience in high-volume regional medical centers.",
    skills: "Clinical Care, Patient Assessment, Emergency Nursing, Electronic Health Records (EHR), Epic Systems, CPR/BLS, Medication Administration, Triage",
    company: "Metropolitan General Hospital",
    jobTitle: "Staff Registered Nurse (RN)",
    dates: "Aug 2019 – Present",
    experienceBullets: [
      "Administered acute emergency patient care across a 30-bed unit, maintaining a 99% patient satisfaction rating.",
      "Supervised clinical medical documentation compliance across Epic & Cerner EHR systems.",
      "Trained 12 junior nursing staff members on emergency triage protocols and infection control safety standards."
    ].join("\n"),
    projectName: "Emergency Department Triage Streamlining",
    projectDescription: "Led quality improvement initiative to reduce emergency department intake waiting times.",
    projectBullets: [
      "Reduced patient triage intake processing time from 24 minutes down to 14 minutes.",
      "Developed standard operating procedure (SOP) adopted across regional emergency care facilities."
    ].join("\n"),
    degree: "B.S. in Nursing (BSN)",
    institution: "Boston College School of Nursing",
    gradYear: "2018",
  },
  finance: {
    fullName: "Marcus Vance",
    title: "Senior Corporate Financial Analyst",
    email: "mvance@example.com",
    phone: "(555) 456-7890",
    location: "Chicago, IL",
    linkedin: "linkedin.com/in/mvance-finance",
    summary: "Results-oriented Senior Financial Analyst specializing in corporate valuation, 3-statement financial modeling, variance forecasting, and M&A due diligence across commercial enterprise sectors.",
    skills: "Financial Modeling, Valuation, Corporate Forecasting, Advanced Excel, SQL, Financial Reporting, Risk Analysis, Budget Planning, PowerBI",
    company: "Vertex Capital Management",
    jobTitle: "Senior Financial Analyst",
    dates: "Jun 2020 – Present",
    experienceBullets: [
      "Constructed 3-statement financial forecasting models predicting annual corporate revenue variance within 2% accuracy.",
      "Analyzed quarterly financial performance across a $50M commercial asset portfolio.",
      "Automated monthly financial variance reporting dashboards in SQL & PowerBI, saving 15 analyst hours weekly."
    ].join("\n"),
    projectName: "M&A Acquisition Valuation Model",
    projectDescription: "Developed discounted cash flow (DCF) model for $35M strategic tech company buyout.",
    projectBullets: [
      "Identified $1.8M in operational synergy cost savings during pre-acquisition due diligence.",
      "Presented financial sensitivity models to executive board and investment committee."
    ].join("\n"),
    degree: "B.S. in Finance & Accounting",
    institution: "University of Illinois",
    gradYear: "2018",
  },
};

export function AtsBuilder({ activePreset = "tech", onSelectPreset, onAuditInScanner }: AtsBuilderProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateId>("executive");
  const [activeStep, setActiveStep] = useState<"contact" | "summary" | "skills" | "experience" | "projects" | "education">("contact");
  const [formData, setFormData] = useState(PRESET_DATA[activePreset] || PRESET_DATA.tech);

  // Sync builder form data whenever activePreset prop changes
  useEffect(() => {
    if (activePreset && PRESET_DATA[activePreset]) {
      setFormData(PRESET_DATA[activePreset]);
    }
  }, [activePreset]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleAiEnhanceSummary = () => {
    setFormData((prev: any) => ({
      ...prev,
      summary: `High-impact ${prev.title || "Professional"} with proven expertise driving strategic technical initiatives and scalable solution architecture. Expert in ${prev.skills.split(",").slice(0, 4).join(", ")}, with a strong track record of optimizing performance metrics and delivering enterprise-grade business value.`,
    }));
  };

  const handleSendToScanner = () => {
    const fullText = `${formData.fullName}\n${formData.title}\n${formData.location} | ${formData.phone} | ${formData.email} | ${formData.linkedin}\n\nPROFESSIONAL SUMMARY:\n${formData.summary}\n\nCORE SKILLS:\n${formData.skills}\n\nWORK EXPERIENCE:\n${formData.jobTitle} - ${formData.company} (${formData.dates})\n${formData.experienceBullets}\n\nEDUCATION:\n${formData.degree} - ${formData.institution} (${formData.gradYear})`;

    if (onAuditInScanner) {
      onAuditInScanner(fullText);
    }
  };

  const handleExportPDF = () => {
    const printWindow = window.open("", "_blank", "width=850,height=950");
    if (!printWindow) {
      window.print();
      return;
    }

    const expBullets = formData.experienceBullets.split("\n").filter(Boolean).map((b: string) => `<li style="margin-bottom: 3.5px;">${b}</li>`).join("");
    const projBullets = formData.projectBullets.split("\n").filter(Boolean).map((b: string) => `<li style="margin-bottom: 3.5px;">${b}</li>`).join("");

    let templateStyles = "";
    let templateHTML = "";

    if (selectedTemplate === "modern") {
      templateStyles = `
        body { font-family: 'Inter', Arial, sans-serif; font-size: 9.5pt; color: #0f172a; margin: 0; padding: 20px; }
        .header { border-left: 4px solid #10b981; padding-left: 14px; margin-bottom: 16px; }
        h1 { font-size: 20pt; margin: 0; color: #0f172a; font-weight: 800; }
        .title { font-size: 11pt; color: #059669; font-weight: 700; margin-top: 2px; }
        .contact { font-size: 9pt; color: #475569; margin-top: 4px; }
        h2 { font-size: 11pt; text-transform: uppercase; font-weight: 800; color: #0f172a; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 3px; margin-top: 14px; margin-bottom: 6px; }
      `;
    } else if (selectedTemplate === "corporate") {
      templateStyles = `
        body { font-family: 'Georgia', Times, serif; font-size: 10pt; color: #111827; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 16px; border-bottom: 2px double #111827; padding-bottom: 10px; }
        h1 { font-size: 21pt; margin: 0; color: #111827; font-weight: normal; letter-spacing: 1px; text-transform: uppercase; }
        .title { font-size: 10.5pt; color: #374151; font-style: italic; margin-top: 3px; }
        .contact { font-size: 9pt; color: #4b5563; margin-top: 6px; }
        h2 { font-size: 11pt; text-transform: uppercase; font-weight: bold; color: #111827; border-bottom: 1px solid #111827; padding-bottom: 2px; margin-top: 14px; margin-bottom: 6px; }
      `;
    } else if (selectedTemplate === "minimalist") {
      templateStyles = `
        body { font-family: 'Courier New', Courier, monospace; font-size: 9.5pt; color: #1e293b; margin: 0; padding: 20px; }
        .header { margin-bottom: 14px; }
        h1 { font-size: 18pt; margin: 0; color: #0f172a; font-weight: bold; }
        .title { font-size: 10pt; color: #334155; margin-top: 2px; }
        .contact { font-size: 8.5pt; color: #64748b; margin-top: 4px; }
        h2 { font-size: 10.5pt; text-transform: uppercase; font-weight: bold; color: #0f172a; border-bottom: 1px dashed #64748b; padding-bottom: 2px; margin-top: 12px; margin-bottom: 6px; }
      `;
    } else {
      // Executive default
      templateStyles = `
        body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #111827; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 14px; border-bottom: 2px solid #111827; padding-bottom: 8px; }
        h1 { font-size: 20pt; margin: 0; color: #111827; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
        .title { font-size: 11pt; color: #1f2937; font-weight: 600; margin-top: 2px; }
        .contact { font-size: 9pt; color: #374151; margin-top: 4px; }
        h2 { font-size: 11pt; text-transform: uppercase; font-weight: bold; color: #111827; border-bottom: 1.5px solid #4b5563; padding-bottom: 3px; margin-top: 14px; margin-bottom: 6px; }
      `;
    }

    templateHTML = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${formData.fullName.replace(/\s+/g, "_")}_Resume</title>
          <style>
            @page { size: letter; margin: 15mm 20mm 15mm 20mm; }
            ${templateStyles}
            p, ul, li { margin: 0 0 6px 0; }
            ul { padding-left: 18px; list-style-type: disc; }
            .exp-row { display: flex; justify-content: space-between; font-weight: bold; margin-top: 8px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${formData.fullName}</h1>
            <div class="title">${formData.title}</div>
            <div class="contact">${formData.location} | ${formData.phone} | ${formData.email} | ${formData.linkedin}</div>
          </div>

          <h2>Professional Summary</h2>
          <p>${formData.summary}</p>

          <h2>Core Technical Skills & Competencies</h2>
          <p>${formData.skills}</p>

          <h2>Professional Experience</h2>
          <div class="exp-row">
            <span>${formData.jobTitle} — ${formData.company}</span>
            <span>${formData.dates}</span>
          </div>
          <ul style="margin-top: 4px;">${expBullets}</ul>

          ${formData.projectName ? `
            <h2>Projects & Key Initiatives</h2>
            <p><strong>${formData.projectName}</strong> — <em>${formData.projectDescription}</em></p>
            <ul style="margin-top: 4px;">${projBullets}</ul>
          ` : ""}

          <h2>Education & Credentials</h2>
          <p><strong>${formData.degree}</strong> — ${formData.institution} (${formData.gradYear})</p>

          <script>
            window.onload = function() {
              window.print();
              setTimeout(function() { window.close(); }, 500);
            };
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(templateHTML);
    printWindow.document.close();
  };

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Header Banner */}
      <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg dark:shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-[10px] font-mono rounded bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 uppercase font-semibold">
              Section 3: Industry Grade ATS Resume Builder
            </span>
          </div>
          <h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-slate-100 mt-1 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400" /> Executive ATS Resume Builder
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Fill in candidate details, export clean PDFs, or auto-audit directly inside Section 1.
          </p>
        </div>

        {/* Clean Right Action Group */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          {onAuditInScanner && (
            <button
              onClick={handleSendToScanner}
              className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-emerald-700 dark:text-emerald-300 font-bold text-xs border border-emerald-500/30 dark:border-emerald-500/40 flex items-center gap-1.5 transition-all shadow-xs cursor-pointer"
            >
              <ScanLine className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Audit in Section 1
            </button>
          )}

          <button
            onClick={handleExportPDF}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-extrabold text-xs shadow-md shadow-emerald-500/20 flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <Printer className="w-4 h-4" /> Export ATS PDF
          </button>
        </div>
      </div>

      {/* BUILDER WORKSPACE GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form Navigator & Inputs (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Step Selector */}
          <div className="flex items-center gap-1.5 p-1.5 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 rounded-xl overflow-x-auto shadow-xs">
            {[
              { id: "contact", label: "Contact", icon: User },
              { id: "summary", label: "Summary", icon: Award },
              { id: "skills", label: "Skills", icon: Code },
              { id: "experience", label: "Experience", icon: Briefcase },
              { id: "projects", label: "Projects", icon: FolderGit2 },
              { id: "education", label: "Education", icon: GraduationCap },
            ].map((step) => {
              const Icon = step.icon;
              const isActive = activeStep === step.id;
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all shrink-0 cursor-pointer ${
                    isActive
                      ? "bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 font-extrabold"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" /> {step.label}
                </button>
              );
            })}
          </div>

          {/* Form Step Body */}
          <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-slate-800 space-y-4 shadow-lg dark:shadow-xl">
            {activeStep === "contact" && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Header & Contact Details</h4>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Full Name</label>
                  <input
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Target Role Title</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Phone</label>
                    <input
                      type="text"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Location & LinkedIn URL</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
              </div>
            )}

            {activeStep === "summary" && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Professional Summary</h4>
                  <button
                    onClick={handleAiEnhanceSummary}
                    className="px-2.5 py-1 rounded-lg bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 text-[10px] font-bold flex items-center gap-1 hover:bg-emerald-500/20 transition-all cursor-pointer"
                  >
                    <Wand2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" /> AI Enhance Summary
                  </button>
                </div>
                <textarea
                  name="summary"
                  value={formData.summary}
                  onChange={handleChange}
                  rows={6}
                  className="w-full p-3 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input resize-none font-sans leading-relaxed"
                />
              </div>
            )}

            {activeStep === "skills" && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Technical Skills & Tools (Comma Separated)</h4>
                <textarea
                  name="skills"
                  value={formData.skills}
                  onChange={handleChange}
                  rows={6}
                  className="w-full p-3 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input resize-none font-mono"
                />
              </div>
            )}

            {activeStep === "experience" && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Work Experience & Metrics</h4>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Company</label>
                    <input
                      type="text"
                      name="company"
                      value={formData.company}
                      onChange={handleChange}
                      className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Job Title</label>
                    <input
                      type="text"
                      name="jobTitle"
                      value={formData.jobTitle}
                      onChange={handleChange}
                      className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Dates</label>
                  <input
                    type="text"
                    name="dates"
                    value={formData.dates}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Experience Bullets (One per line)</label>
                  <textarea
                    name="experienceBullets"
                    value={formData.experienceBullets}
                    onChange={handleChange}
                    rows={6}
                    className="w-full p-3 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1 resize-none font-mono leading-relaxed"
                  />
                </div>
              </div>
            )}

            {activeStep === "projects" && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Projects & Key Initiatives</h4>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Project Name</label>
                  <input
                    type="text"
                    name="projectName"
                    value={formData.projectName}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Project Description</label>
                  <input
                    type="text"
                    name="projectDescription"
                    value={formData.projectDescription}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Project Bullets (One per line)</label>
                  <textarea
                    name="projectBullets"
                    value={formData.projectBullets}
                    onChange={handleChange}
                    rows={5}
                    className="w-full p-3 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1 resize-none font-mono leading-relaxed"
                  />
                </div>
              </div>
            )}

            {activeStep === "education" && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase font-bold text-slate-900 dark:text-slate-200">Education & Certification Credentials</h4>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Degree</label>
                  <input
                    type="text"
                    name="degree"
                    value={formData.degree}
                    onChange={handleChange}
                    className="w-full p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input mt-1"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-semibold">Institution & Graduation Year</label>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <input
                      type="text"
                      name="institution"
                      value={formData.institution}
                      onChange={handleChange}
                      className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input"
                    />
                    <input
                      type="text"
                      name="gradYear"
                      value={formData.gradYear}
                      onChange={handleChange}
                      className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 glass-input"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Live Paper Preview (7 Cols) */}
        <div className="lg:col-span-7">
          <div className="p-6 glass-card bg-white/90 dark:bg-slate-900/90 border border-slate-200/90 dark:border-emerald-500/30 rounded-2xl flex flex-col shadow-lg dark:shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
              <span className="text-xs font-mono font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Eye className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Live Resume Preview
              </span>

              {/* Compact Format Option Dropdown */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300 uppercase">Format:</span>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value as TemplateId)}
                  className="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-950/90 border border-slate-300 dark:border-emerald-500/40 text-emerald-800 dark:text-emerald-300 font-mono text-xs font-bold focus:outline-none focus:ring-2 focus:ring-emerald-500/50 cursor-pointer shadow-xs"
                >
                  <option value="executive">🎨 Executive Single-Column (ATS Default)</option>
                  <option value="modern">💼 Modern Slate & Accent Line</option>
                  <option value="corporate">📊 Corporate Classic (Georgia Serif)</option>
                  <option value="minimalist">⚡ Minimalist Developer (Monospace)</option>
                </select>
              </div>
            </div>

            {/* Live Paper Document */}
            <div className="p-8 sm:p-10 rounded-2xl bg-white text-slate-900 font-sans text-xs leading-relaxed max-h-[700px] overflow-y-auto shadow-2xl resume-paper-preview">
              {/* Header Render */}
              <div className={`mb-4 pb-3 ${selectedTemplate === "modern" ? "border-l-4 border-emerald-600 pl-3 border-b-0" : selectedTemplate === "corporate" ? "text-center border-b-2 border-double border-slate-900 pb-3" : "text-center border-b-2 border-slate-900 pb-3"}`}>
                <h1 className={`text-xl font-bold uppercase tracking-tight text-slate-900 ${selectedTemplate === "corporate" ? "font-serif tracking-widest text-2xl font-normal" : selectedTemplate === "minimalist" ? "font-mono text-lg" : ""}`}>{formData.fullName}</h1>
                <p className={`text-xs text-slate-700 font-semibold ${selectedTemplate === "modern" ? "text-emerald-700" : selectedTemplate === "corporate" ? "italic text-slate-600 font-normal" : ""}`}>{formData.title}</p>
                <p className="text-[11px] text-slate-500 mt-1 font-mono">
                  {formData.location} | {formData.phone} | {formData.email} | {formData.linkedin}
                </p>
              </div>

              {/* Summary Render */}
              <div className="mb-4">
                <h2 className={`text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-1.5 ${selectedTemplate === "minimalist" ? "font-mono border-dashed border-slate-500" : ""}`}>
                  Professional Summary
                </h2>
                <p className="text-slate-700 leading-relaxed font-normal">{formData.summary}</p>
              </div>

              {/* Skills Render */}
              <div className="mb-4">
                <h2 className={`text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-1.5 ${selectedTemplate === "minimalist" ? "font-mono border-dashed border-slate-500" : ""}`}>
                  Core Technical Skills & Competencies
                </h2>
                <p className="text-slate-700 font-medium">{formData.skills}</p>
              </div>

              {/* Experience Render */}
              <div className="mb-4">
                <h2 className={`text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-1.5 ${selectedTemplate === "minimalist" ? "font-mono border-dashed border-slate-500" : ""}`}>
                  Professional Experience
                </h2>
                <div className="flex items-center justify-between font-bold text-slate-900 mt-1 text-xs">
                  <span>{formData.jobTitle} — {formData.company}</span>
                  <span className="text-[11px] text-slate-600 font-medium">{formData.dates}</span>
                </div>
                <ul className="list-disc pl-4 mt-1.5 space-y-1 text-slate-700">
                  {formData.experienceBullets.split("\n").filter(Boolean).map((bullet: string, idx: number) => (
                    <li key={idx}>{bullet}</li>
                  ))}
                </ul>
              </div>

              {/* Projects Render */}
              {formData.projectName && (
                <div className="mb-4">
                  <h2 className={`text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-1.5 ${selectedTemplate === "minimalist" ? "font-mono border-dashed border-slate-500" : ""}`}>
                    Projects & Key Initiatives
                  </h2>
                  <p className="font-bold text-slate-900">{formData.projectName}</p>
                  <p className="text-slate-600 italic mb-1 text-[11px]">{formData.projectDescription}</p>
                  <ul className="list-disc pl-4 space-y-1 text-slate-700">
                    {formData.projectBullets.split("\n").filter(Boolean).map((bullet: string, idx: number) => (
                      <li key={idx}>{bullet}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Education Render */}
              <div>
                <h2 className={`text-xs font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1 mb-1.5 ${selectedTemplate === "minimalist" ? "font-mono border-dashed border-slate-500" : ""}`}>
                  Education & Credentials
                </h2>
                <p className="font-bold text-slate-900">{formData.degree}</p>
                <p className="text-slate-600">{formData.institution} ({formData.gradYear})</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
