"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { api, User } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, role: "seeker" | "offerer", company?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
      setError(null);
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : "Failed to fetch user");
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      refreshUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refreshUser]);

  const login = async (email: string, password: string) => {
    setError(null);
    setLoading(true);
    try {
      await api.login(email, password);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string, role: "seeker" | "offerer", company?: string) => {
    setError(null);
    setLoading(true);
    try {
      await api.register(email, password, role, company);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setError(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
