"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.forgotPassword(email);
    } catch {
      // Always show the generic confirmation to avoid leaking account existence.
    } finally {
      setSent(true);
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Reset your password"
      description="We&apos;ll email you a secure link to reset your password."
      footer={
        <Link href="/login" className="text-leaf-400 hover:underline">
          Back to sign in
        </Link>
      }
    >
      {sent ? (
        <p className="text-sm text-leaf-400">
          If an account exists for {email}, a reset link has been sent. Check your inbox.
        </p>
      ) : (
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
          {error && <p className="text-sm text-terra-500">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Sending…" : "Send Reset Link"}
          </Button>
        </form>
      )}
    </AuthShell>
  );
}
