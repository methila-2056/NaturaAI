export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";
export const ML_URL = process.env.NEXT_PUBLIC_ML_URL ?? "http://localhost:8000";

type RequestOptions = RequestInit & {
  token?: string | null;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, headers, ...rest } = options;
  const url = path.startsWith("http") ? path : `${API_URL}${path}`;
  const res = await fetch(url, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.message ?? `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export interface AnalyzeRequest {
  ingredients: string[];
  remedyType: "internal" | "external";
  profile?: {
    age: number;
    gender: string;
    diseases: string[];
    allergies: string[];
    medications: string[];
  };
}

export interface AnalyzeResponse {
  compatibilityScore: number;
  safetyScore: number;
  benefitScore: number;
  riskScore: number;
  scientificConfidence: number;
  toxicityLevel: "low" | "medium" | "high";
  verdict: "safe" | "caution" | "unsafe";
  benefits: string[];
  risks: string[];
  preparation: string[];
  quantity: string;
  usageFrequency: string;
  rationale: string;
}

export interface SuggestResult {
  ingredient: string;
  verdict: "safe" | "caution" | "unsafe";
  confidence: number;
  compatibility: number | null;
  benefits: string[];
  note?: string | null;
}

export const api = {
  analyze: (payload: AnalyzeRequest) =>
    request<AnalyzeResponse>("/api/v1/remedies/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  predict: (payload: AnalyzeRequest) =>
    request<AnalyzeResponse>(`${ML_URL}/predict`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  suggest: (ingredient: string, exclude: string[], limit = 5) =>
    request<{ ingredient: string; suggestions: SuggestResult[] }>(`${ML_URL}/suggest`, {
      method: "POST",
      body: JSON.stringify({ ingredient, exclude, limit }),
    }),
  login: (email: string, password: string) =>
    request<{ token: string; user: unknown }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: Record<string, unknown>) =>
    request<{ token: string; user: unknown }>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  forgotPassword: (email: string) =>
    request<{ message: string }>("/api/v1/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  verifyEmail: (token: string) =>
    request<{ message: string }>("/api/v1/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  me: (token: string) =>
    request<Record<string, unknown>>("/api/v1/users/me", { token }),
  herbs: () => request<Array<Record<string, unknown>>>("/api/v1/herbs"),
  recognize: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${ML_URL}/recognize`, {
      method: "POST",
      body: form,
    }).then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? body?.message ?? `Request failed with status ${res.status}`);
      }
      return res.json();
    });
  },
};
