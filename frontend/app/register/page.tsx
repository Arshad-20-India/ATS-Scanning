"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Shield, UserPlus, AlertCircle, RefreshCw } from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/layout/navbar";
import { useAuth } from "@/components/auth/auth-provider";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !fullName) {
      setError("Please fill in all required fields.");
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await register(email, password, fullName);
      router.push("/");
    } catch (err: any) {
      setError(err?.message || "Could not create account. Please try again.");
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
                Create Account
              </h1>
              <UserPlus className="w-5 h-5 text-emerald-400" />
            </div>
            <p className="text-xs text-slate-400">
              Create your account to access enterprise AI resume optimization tools.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 font-semibold block">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Alex Devon"
                className="w-full p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-100 glass-input font-mono"
                required
              />
            </div>

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
                  <RefreshCw className="w-4 h-4 animate-spin" /> Creating Account...
                </>
              ) : (
                <>
                  Create Account <UserPlus className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400">Already have an account?</span>
            <Link href="/login" className="text-emerald-400 font-bold hover:underline">
              Sign In →
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
