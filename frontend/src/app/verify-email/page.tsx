"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

function VerifyEmailContent() {
  const params = useSearchParams();
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = params.get("token");
      if (!token) {
        if (!cancelled) {
          setState("error");
          setMessage("Missing verification token.");
        }
        return;
      }
      try {
        const res = await api.verifyEmail(token);
        if (!cancelled) {
          setState("success");
          setMessage(res.message);
        }
      } catch (err) {
        if (!cancelled) {
          setState("error");
          setMessage(err instanceof Error ? err.message : "Verification failed");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params]);

  return (
    <AuthShell
      title={state === "success" ? "Email verified" : "Verify your email"}
      description="Confirming your account so you can sign in."
    >
      <div className="flex flex-col items-center gap-4 text-center">
        {state === "loading" && <p className="text-sm text-cream-200/80">Verifying…</p>}
        {state === "success" && (
          <>
            <CheckCircle2 className="h-12 w-12 text-leaf-400" />
            <p className="text-sm text-cream-200/80">{message}</p>
            <Button asChild className="w-full">
              <Link href="/login">Go to sign in</Link>
            </Button>
          </>
        )}
        {state === "error" && (
          <>
            <XCircle className="h-12 w-12 text-terra-500" />
            <p className="text-sm text-cream-200/80">{message}</p>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Back to sign in</Link>
            </Button>
          </>
        )}
      </div>
    </AuthShell>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <AuthShell title="Verify your email" description="Confirming your account…">
          <p className="text-sm text-cream-200/80">Loading…</p>
        </AuthShell>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
