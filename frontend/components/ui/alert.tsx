import { AlertTriangle, Info } from "lucide-react";
import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "error" | "info";
}

export function Alert({ className, variant = "info", children, ...props }: AlertProps) {
  const Icon = variant === "error" ? AlertTriangle : Info;
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      className={cn(
        "flex items-start gap-2.5 rounded-sm border px-3.5 py-3 text-sm",
        variant === "error"
          ? "border-signal-fail/40 bg-signal-fail-soft text-signal-fail"
          : "border-accent/30 bg-accent-soft text-ink",
        className
      )}
      {...props}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      <div>{children}</div>
    </div>
  );
}
