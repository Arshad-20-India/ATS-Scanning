"use client";

import { Sun, Moon } from "lucide-react";
import { useTheme } from "./theme-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-xl border transition-all flex items-center gap-1.5 text-xs font-semibold shadow-sm bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
      title={`Switch to ${theme === "light" ? "Dark" : "Light"} Theme`}
      aria-label="Toggle theme"
    >
      {theme === "light" ? (
        <>
          <Sun className="w-4 h-4 text-amber-500 fill-amber-500/20" />
          <span className="hidden sm:inline-block font-mono">Light Mode</span>
        </>
      ) : (
        <>
          <Moon className="w-4 h-4 text-indigo-400 fill-indigo-400/20" />
          <span className="hidden sm:inline-block font-mono">Dark Mode</span>
        </>
      )}
    </button>
  );
}
