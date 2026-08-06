"use client";

import Link from "next/link";
import { useState } from "react";
import { MailCheck } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: "",
    age: 0,
    gender: "",
    country: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.register(form);
      setRegisteredEmail(form.email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  if (registeredEmail) {
    return (
      <AuthShell
        title="Verify your email"
        description="Almost there! We just sent you a verification link."
      >
        <div className="flex flex-col items-center gap-4 text-center">
          <MailCheck className="h-12 w-12 text-leaf-400" />
          <p className="text-sm text-cream-200/80">
            A verification email was sent to{" "}
            <span className="font-medium text-leaf-400">{registeredEmail}</span>.
            Click the link in the email to verify your account, then sign in.
          </p>
          <p className="text-xs text-cream-200/50">
            Didn&apos;t receive it? Check your spam folder.
          </p>
          <Button asChild className="w-full">
            <Link href="/login">Go to sign in</Link>
          </Button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Create your account"
      description="Set up your profile so recommendations can be personalized to you."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="text-leaf-400 hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="fullName">
            Full Name
          </label>
          <input
            id="fullName"
            required
            value={form.fullName}
            onChange={(e) => update("fullName", e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm text-cream-200" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
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
            minLength={8}
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
          />
        </div>
        <div className="grid grid-cols-1 gap-3 min-[520px]:grid-cols-3">
          <div>
            <label className="mb-1.5 block text-sm text-cream-200" htmlFor="age">
              Age
            </label>
            <input
              id="age"
              type="number"
              min={1}
              max={120}
              required
              value={form.age || ""}
              onChange={(e) => update("age", Number(e.target.value))}
              className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm text-cream-200" htmlFor="gender">
              Gender
            </label>
            <select
              id="gender"
              required
              value={form.gender}
              onChange={(e) => update("gender", e.target.value)}
              className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
            >
              <option value="">Select</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm text-cream-200" htmlFor="country">
              Country
            </label>
            <input
              id="country"
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
              className="w-full rounded-xl border border-forest-600 bg-forest-950 px-4 py-2.5 text-sm outline-none focus:border-leaf-400"
            />
          </div>
        </div>
        {error && <p className="text-sm text-terra-500">{error}</p>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Creating account…" : "Create Account"}
        </Button>
      </form>
    </AuthShell>
  );
}
