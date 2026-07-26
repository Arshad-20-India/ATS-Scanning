"use client";

import { Sparkles, LogOut, FileText } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { ThemeToggle } from "@/components/theme/theme-toggle";

export function Navbar() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  return (
    <header className="sticky top-0 z-50 glass-nav">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-slate-950 flex items-center justify-center shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform font-black">
            <Sparkles className="h-5 w-5 fill-slate-950/20" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg text-slate-900 dark:text-slate-100 tracking-tight block leading-none">
              AI Resume <span className="gradient-text-emerald">Intelligence</span>
            </span>
            <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 tracking-wider uppercase block mt-0.5 font-medium">
              ATS Scanner & Rewriter
            </span>
          </div>
        </Link>

        {/* Navigation Links & Theme Toggle */}
        <nav className="flex items-center gap-3">
          <ThemeToggle />

          <Link
            href="/"
            className="text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-emerald-500 transition-colors flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <FileText className="w-3.5 h-3.5" /> Workspace
          </Link>

          {!isLoading && user && (
            <div className="flex items-center gap-3 border-l border-slate-200 dark:border-slate-800 pl-3">
              <span className="text-xs text-slate-600 dark:text-slate-300 font-mono hidden sm:inline-block font-medium">
                {user.email}
              </span>
              <button
                onClick={() => {
                  logout();
                  router.push("/");
                }}
                className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-500 hover:text-rose-500 dark:text-slate-400 dark:hover:text-rose-400 transition-all"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}

          {!isLoading && !user && (
            <div className="flex items-center gap-2 border-l border-slate-200 dark:border-slate-800 pl-3">
              <Link
                href="/login"
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-xs font-bold text-slate-950 shadow-md shadow-emerald-500/20 transition-all"
              >
                Get started
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
