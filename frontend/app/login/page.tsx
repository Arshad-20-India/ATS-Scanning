"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Shield, Lock, LogIn, AlertCircle, RefreshCw } from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/layout/navbar";
import { useAuth } from "@/components/auth/auth-provider";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err?.message || "Authentication failed. Please verify your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen pb-16">
      <Navbar />

      <main className="mx-auto max-w-md px-6 pt-16">
        <div className="p-8 glass-card bg-slate-900/95 border border-slate-800 rounded-3xl shadow-2xl space-y-6">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h1 className="font-display font-extrabold text-2xl text-slate-100">
                Sign In
              </h1>
              <Lock className="w-5 h-5 text-emerald-400" />
            </div>
            <p className="text-xs text-slate-400">
              Access your saved ATS scans, resume rewrites, and PDF downloads.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 font-semibold block">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="candidate@example.com"
                className="w-full p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-100 glass-input font-mono"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 font-semibold block">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-100 glass-input font-mono"
                required
              />
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" /> {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold text-sm shadow-xl shadow-emerald-500/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Authenticating...
                </>
              ) : (
                <>
                  Sign In <LogIn className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400">Don't have an account?</span>
            <Link href="/register" className="text-emerald-400 font-bold hover:underline">
              Create Account →
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
