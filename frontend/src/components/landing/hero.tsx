"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Leaf, ScanLine, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-16 pb-20">
      <div
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 30%, rgba(74,191,130,0.15), transparent 40%), radial-gradient(circle at 80% 70%, rgba(242,182,77,0.12), transparent 40%)",
        }}
      />

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-6 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-leaf-500/40 bg-forest-800 px-4 py-1.5 text-xs text-leaf-400">
            <Sparkles className="h-3.5 w-3.5" />
            AI-powered herbal intelligence
          </span>
          <h1 className="mt-6 text-5xl font-bold leading-tight tracking-tight md:text-6xl">
            Discover Nature with <span className="text-gradient">AI</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg text-cream-200/80">
            Predict herb-to-herb compatibility, uncover benefits and risks, and receive
            personalized natural remedy recommendations — before you prepare or consume
            anything.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Button size="lg" asChild>
              <Link href="/analyze">
                <Leaf className="h-5 w-5" />
                Analyze a Remedy
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/register">
                <ScanLine className="h-5 w-5" />
                Scan a Plant
              </Link>
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="relative hidden justify-center lg:flex"
        >
          <div className="animate-float relative h-80 w-80 rounded-full bg-forest-800/50 blur-sm" />
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-6">
            {["Tulsi", "Neem", "Turmeric", "Ashwagandha"].map((herb, i) => (
              <motion.div
                key={herb}
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.12 }}
                className={`animate-float flex items-center gap-3 rounded-2xl border border-forest-600 bg-forest-900/80 px-5 py-3 backdrop-blur ${
                  i % 2 === 0 ? "self-start" : "self-end"
                }`}
              >
                <span className="text-2xl">🌿</span>
                <div>
                  <p className="text-sm font-medium">{herb}</p>
                  <p className="text-xs text-leaf-400">97% compatible</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
