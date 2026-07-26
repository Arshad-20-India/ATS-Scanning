import type { ScoreCategory } from "./types";

/**
 * Evidence.found_value / expected_value are `unknown` on the wire
 * (see lib/types.ts) because the backend's Evidence.found_value is
 * typed Any -- it can legitimately be a bool, number, string, array,
 * or null depending on which criterion produced it. This is the one
 * place that reasons about all those shapes so every call site stays
 * simple.
 */
export function formatEvidenceValue(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (typeof value === "boolean") return value ? "yes" : "no";
  if (Array.isArray(value)) {
    return value.length === 0 ? "none" : value.join(", ");
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}

const CATEGORY_LABELS: Record<ScoreCategory, string> = {
  semantic_alignment: "1. Keyword Match (30% Weight)",
  skills: "2. Skills Match (20% Weight)",
  experience: "3. Experience (15% Weight)",
  education: "4. Education (10% Weight)",
  ats_compatibility: "5. Formatting & ATS Layout (10% Weight)",
  grammar: "6. Action Verbs (5% Weight)",
  projects: "7. Readability & Clarity (5% Weight)",
  certifications: "8. Missing Requirements (5% Weight)",
};

export function formatCategoryLabel(category: ScoreCategory): string {
  return CATEGORY_LABELS[category] ?? category;
}

export function scoreTier(scorePercent: number): "pass" | "warn" | "fail" {
  if (scorePercent >= 75) return "pass";
  if (scorePercent >= 40) return "warn";
  return "fail";
}
