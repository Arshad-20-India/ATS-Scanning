/**
 * Token storage. Plain localStorage is appropriate here -- this is a
 * real, deployed Next.js application (not a Claude.ai artifact, where
 * browser storage APIs are unavailable). A production hardening pass
 * might move to an httpOnly cookie set by the backend to reduce XSS
 * exposure; noted in the README as a Phase 9 (observability/hardening)
 * candidate rather than done here.
 */

const TOKEN_KEY = "resume_scanner_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}
