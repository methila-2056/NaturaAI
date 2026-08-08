"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

function ResetPasswordContent() {
  const params = useSearchParams();
  const token = params.get("token");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [state, setState] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError("Missing reset token.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.resetPassword(token, password);
      setState("success");
      setMessage(res.message);
    } catch (err) {
      setState("error");
      setMessage(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  }

  if (state === "success") {
    return (
      <AuthShell title="Password reset" description="Your password has been updated.">
        <div className="flex flex-col items-center gap-4 text-center">
          <CheckCircle2 className="h-12 w-12 text-leaf-400" />
          <p className="text-sm text-cream-200/80">{message}</p>
          <Button asChild className="w-full">
            <Link href="/login">Go to sign in</Link>
          </Button>
        </div>
      </AuthShell>
    );
  }

  if (state === "error") {
    return (
      <AuthShell title="Password reset" description="We could not reset your password.">
        <div className="flex flex-col items-center gap-4 text-center">
          <XCircle className="h-12 w-12 text-terra-500" />
          <p className="text-sm text-cream-200/80">{message}</p>
          <Button asChild variant="outline" className="w-full">
            <Link href="/forgot-password">Request a new link</Link>
          </Button>
        </div>
      </AuthShell>
    );
  }

  if (!token) {
    return (
      <AuthShell title="Reset your password" description="Invalid reset link.">
        <p className="text-sm text-terra-500">
          Missing reset token. Use the link from your email.
        </p>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Choose a new password"
      description="Enter a new password for your account."
      footer={
        <Link href="/login" className="text-leaf-400 hover:underline">
          Back to sign in
        </Link>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="password">
            New password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="confirm">
            Confirm new password
          </label>
          <input
            id="confirm"
            type="password"
            required
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
        </div>
        {error && <p className="text-sm text-terra-500">{error}</p>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Resetting…" : "Reset Password"}
        </Button>
      </form>
    </AuthShell>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <AuthShell title="Reset your password" description="Loading…">
          <p className="text-sm text-cream-200/80">Loading…</p>
        </AuthShell>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
