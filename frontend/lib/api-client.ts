import { clearToken, getToken } from "./auth";
import type {
  AnalysisResponse,
  ApiErrorBody,
  JobDescriptionResponse,
  ResumeResponse,
  TaskEnqueuedResponse,
  TaskStatusResponse,
  TokenResponse,
  UserResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const { auth = false, headers, ...rest } = options;
  const finalHeaders = new Headers(headers);

  if (auth) {
    const token = getToken();
    if (token) finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
  });

  if (response.status === 401 && auth) {
    // Token expired/invalid -- clear it so the UI can prompt re-login
    // rather than silently keep sending a dead token on every request.
    clearToken();
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await response.json();
    } catch {
      // response wasn't JSON -- fall through to generic message below
    }
    throw new ApiError(
      response.status,
      body?.error?.code ?? "unknown_error",
      body?.error?.message ?? `Request failed with status ${response.status}`
    );
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  auth: {
    register: (email: string, password: string, fullName?: string) =>
      request<UserResponse>("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName ?? null }),
      }),

    login: (email: string, password: string) => {
      const form = new URLSearchParams();
      form.set("username", email);
      form.set("password", password);
      return request<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
      });
    },

    me: () => request<UserResponse>("/api/v1/auth/me", { auth: true }),
  },

  resumes: {
    list: () => request<ResumeResponse[]>("/api/v1/resumes", { auth: true }),
    get: (id: string) => request<ResumeResponse>(`/api/v1/resumes/${id}`, { auth: true }),
    rewrite: (resumeFile: File, jobDescriptionText: string) => {
      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("job_description_text", jobDescriptionText);
      return request<{ rewritten_text: string }>("/api/v1/resumes/rewrite", {
        method: "POST",
        body: formData,
      });
    },
  },

  jobDescriptions: {
    list: () =>
      request<JobDescriptionResponse[]>("/api/v1/job-descriptions", { auth: true }),
  },

  analyses: {
    analyzeSync: (resumeFile: File, jobDescriptionText: string) => {
      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("job_description_text", jobDescriptionText);
      return request<AnalysisResponse>("/api/v1/analyses/sync", {
        method: "POST",
        body: formData,
        auth: true,
      });
    },

    analyzeAsync: (resumeFile: File, jobDescriptionText: string) => {
      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("job_description_text", jobDescriptionText);
      return request<TaskEnqueuedResponse>("/api/v1/analyses/async", {
        method: "POST",
        body: formData,
        auth: true,
      });
    },

    getTaskStatus: (taskId: string) =>
      request<TaskStatusResponse>(`/api/v1/analyses/tasks/${taskId}`, { auth: true }),

    get: (id: string) => request<AnalysisResponse>(`/api/v1/analyses/${id}`, { auth: true }),
  },
};
