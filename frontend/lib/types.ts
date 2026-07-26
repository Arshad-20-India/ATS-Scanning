/**
 * Types mirroring backend/app/api/schemas/*.py.
 *
 * Kept in sync by hand, deliberately -- same reasoning as the
 * backend's mappers.py (explicit > generic/inferred). A future
 * iteration could generate these from the live OpenAPI schema
 * (FastAPI serves one at /openapi.json) via a codegen step; noted as
 * a natural next hardening step in the project README rather than
 * done here, to avoid adding a build-time dependency this phase
 * doesn't strictly need yet.
 */

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ContactInfo {
  full_name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin_url: string | null;
}

export interface Skill {
  name: string;
  normalized_name: string;
  category: string | null;
}

export interface DateRange {
  start: string;
  end: string | null;
  is_current: boolean;
}

export interface ExperienceEntry {
  title: string;
  company: string;
  date_range: DateRange;
  bullets: string[];
}

export interface EducationEntry {
  degree: string;
  field_of_study: string;
  institution: string;
  graduation_date: string | null;
  gpa: number | null;
}

export interface ProjectEntry {
  name: string;
  description: string;
  technologies: string[];
  outcomes: string[];
}

export interface CertificationEntry {
  name: string;
  issuer: string | null;
  date_earned: string | null;
}

export interface FormattingFlags {
  uses_tables: boolean;
  uses_text_boxes: boolean;
  non_standard_fonts: boolean;
  has_images_with_text: boolean;
  page_count: number;
}

export interface ResumeResponse {
  id: string;
  filename: string;
  contact_info: ContactInfo;
  skills: Skill[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  sections_detected: string[];
  formatting_flags: FormattingFlags;
  total_experience_years: number;
  created_at: string;
}

export interface JobDescriptionResponse {
  id: string;
  title: string;
  required_skills: string[];
  preferred_skills: string[];
  min_years_experience: number | null;
  required_education: string | null;
  required_certifications: string[];
  created_at: string;
}

// found_value / expected_value are intentionally `unknown` here, not
// `any` -- every place that reads them must narrow the type first
// (see formatEvidenceValue in lib/format.ts), mirroring how the
// backend's Evidence.found_value is typed as Any but every consumer
// still has to reason about what's actually in it.
export interface Evidence {
  criterion: string;
  description: string;
  found_value: unknown;
  expected_value: unknown;
  weight: number;
  passed: boolean;
  confidence: number;
  source_span: string | null;
}

export type ScoreCategory =
  | "skills"
  | "experience"
  | "education"
  | "projects"
  | "certifications"
  | "grammar"
  | "ats_compatibility"
  | "semantic_alignment";

export interface CategoryScore {
  category: ScoreCategory;
  score_percent: number;
  weighted_contribution: number;
  evidence: Evidence[];
}

export interface ScoreCard {
  overall_score: number;
  category_scores: CategoryScore[];
  generated_at: string;
}

export interface Recommendation {
  criterion: string;
  category: ScoreCategory;
  message: string;
  is_llm_generated: boolean;
}

export interface AnalysisResponse {
  resume_id: string;
  job_description_id: string;
  scorecard: ScoreCard;
  recommendations: Recommendation[];
  raw_text?: string;
}

export interface TaskEnqueuedResponse {
  task_id: string;
  status: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE";
  result: AnalysisResponse | null;
  error: string | null;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
