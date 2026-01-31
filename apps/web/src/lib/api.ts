const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  role: "seeker" | "offerer";
  is_active: boolean;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const tokens = await this.request<AuthTokens>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("access_token", tokens.access_token);
    return tokens;
  }

  async register(email: string, password: string, role: "seeker" | "offerer", company?: string): Promise<AuthTokens> {
    const tokens = await this.request<AuthTokens>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, role, company }),
    });
    localStorage.setItem("access_token", tokens.access_token);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  logout() {
    localStorage.removeItem("access_token");
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient(API_BASE_URL);
