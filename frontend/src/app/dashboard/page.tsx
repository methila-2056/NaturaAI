"use client";

import Link from "next/link";
import {
  Activity,
  Bookmark,
  FileHeart,
  History,
  LineChart,
  ScanLine,
  UserRound,
} from "lucide-react";
import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useUserStore } from "@/store/useUserStore";

const savedRemedies = [
  { name: "Immunity Herbal Tea", score: 97, tag: "Cold" },
  { name: "Hibiscus Hair Oil", score: 91, tag: "Hair Loss" },
];

export default function DashboardPage() {
  const { user } = useUserStore();

  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-10 flex items-center gap-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-forest-800 text-leaf-400">
            <UserRound className="h-8 w-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Welcome, {user?.fullName ?? "Explorer"}
            </h1>
            <p className="mt-1 text-cream-200/70">
              Your personalized herbal intelligence dashboard.
            </p>
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Activity, label: "Health Conditions", value: user?.diseases?.length ?? 0 },
            { icon: Bookmark, label: "Saved Remedies", value: savedRemedies.length },
            { icon: History, label: "Recent Analyses", value: 12 },
            { icon: LineChart, label: "Health Streak", value: "6 days" },
          ].map((stat) => (
            <Card key={stat.label}>
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-forest-800 text-leaf-400">
                  <stat.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-sm text-cream-200/70">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <CardTitle>Saved Remedies</CardTitle>
              <Link href="/analyze" className="text-sm text-leaf-400 hover:underline">
                New analysis
              </Link>
            </CardHeader>
            <CardContent className="space-y-4">
              {savedRemedies.map((r) => (
                <div
                  key={r.name}
                  className="flex items-center justify-between rounded-xl border border-forest-700 bg-forest-950/50 p-4"
                >
                  <div>
                    <p className="font-medium">{r.name}</p>
                    <div className="mt-1 flex items-center gap-2">
                      <Badge>{r.tag}</Badge>
                      <span className="text-xs text-leaf-400">{r.score}% compatible</span>
                    </div>
                  </div>
                  <Bookmark className="h-4 w-4 text-leaf-400" />
                </div>
              ))}
              {savedRemedies.length === 0 && (
                <p className="text-sm text-cream-200/60">No saved remedies yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { href: "/analyze", icon: FileHeart, label: "Analyze a remedy" },
                { href: "/scan", icon: ScanLine, label: "Scan a plant" },
                { href: "/chatbot", icon: Activity, label: "Ask the AI assistant" },
              ].map((action) => (
                <Link
                  key={action.label}
                  href={action.href}
                  className="flex items-center gap-3 rounded-xl border border-forest-700 bg-forest-950/50 p-4 text-sm transition-colors hover:border-leaf-400/50"
                >
                  <action.icon className="h-4 w-4 text-leaf-400" />
                  {action.label}
                </Link>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
      <Footer />
    </main>
  );
}
