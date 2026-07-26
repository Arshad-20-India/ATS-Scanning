"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, ApiError } from "@/lib/api-client";
import { clearToken, getToken, setToken } from "@/lib/auth";
import type { UserResponse } from "@/lib/types";

interface AuthContextValue {
  user: UserResponse | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Runs once on mount to restore session from a stored token. Inlined
  // (rather than calling a shared useCallback) with a `cancelled` guard
  // so a fast unmount can't set state on an unmounted component -- the
  // recommended pattern for effect-driven data fetching.
  useEffect(() => {
    let cancelled = false;

    async function checkStoredSession() {
      if (!getToken()) {
        if (!cancelled) setIsLoading(false);
        return;
      }
      try {
        const me = await api.auth.me();
        if (!cancelled) setUser(me);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) clearToken();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void checkStoredSession();
    return () => {
      cancelled = true;
    };
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    try {
      const me = await api.auth.me();
      setUser(me);
    } catch {
      setUser(null);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await api.auth.login(email, password);
      setToken(token.access_token);
      await refreshCurrentUser();
    },
    [refreshCurrentUser]
  );

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await api.auth.register(email, password, fullName);
      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
