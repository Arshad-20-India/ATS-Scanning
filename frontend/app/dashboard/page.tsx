"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function DashboardRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-emerald-400 font-mono text-xs">
      Redirecting to AI Resume Workspace...
    </div>
  );
}
