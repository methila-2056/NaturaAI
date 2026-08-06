"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Globe } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { api, API_URL } from "@/lib/api";
import { useUserStore } from "@/store/useUserStore";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useUserStore((s) => s.setAuth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) return;
    (async () => {
      try {
        const user = await api.me(token);
        setAuth(user as never, token);
        router.replace("/dashboard");
      } catch {
        setError("Google sign-in succeeded but the session could not be loaded.");
      }
    })();
  }, [router, setAuth]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.login(email, password);
      setAuth(res.user as never, res.token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      description="Sign in to continue to your herbal intelligence dashboard."
      footer={
        <>
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-leaf-400 hover:underline">
            Register
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
          <div className="mt-2 text-right">
            <Link href="/forgot-password" className="text-xs text-leaf-400 hover:underline">
              Forgot password?
            </Link>
          </div>
        </div>
        {error && <p className="text-sm text-terra-500">{error}</p>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Signing in…" : "Sign In"}
        </Button>
      </form>

      <div className="my-5 flex items-center gap-3 text-xs text-cream-200/50">
        <div className="h-px flex-1 bg-forest-700" />
        or continue with
        <div className="h-px flex-1 bg-forest-700" />
      </div>

      <Button variant="outline" className="w-full" asChild disabled={!GOOGLE_CLIENT_ID}>
        <a href={`${API_URL}/oauth2/authorization/google`}>
          <Globe className="h-4 w-4" />
          Continue with Google
        </a>
      </Button>
    </AuthShell>
  );
}
