import { Check, X } from "lucide-react";
import { cn } from "@/lib/utils";

export function StampBadge({ passed, animate = false }: { passed: boolean; animate?: boolean }) {
  return (
    <span
      className={cn(
        "stamp",
        passed ? "stamp-pass" : "stamp-fail",
        animate && "stamp-animate"
      )}
    >
      {passed ? <Check className="h-3 w-3" strokeWidth={3} /> : <X className="h-3 w-3" strokeWidth={3} />}
      {passed ? "Pass" : "Fail"}
    </span>
  );
}
