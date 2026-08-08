"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const remedies = [
  {
    name: "Immunity Infusion",
    ingredients: ["Tulsi", "Ginger"],
    type: "Internal",
    score: 97,
  },
  {
    name: "Acne-Fighting Face Wash",
    ingredients: ["Neem", "Aloe Vera"],
    type: "External",
    score: 94,
  },
  {
    name: "Calm & Focus Blend",
    ingredients: ["Ashwagandha", "Brahmi"],
    type: "Internal",
    score: 95,
  },
  {
    name: "Hair Strength Duo",
    ingredients: ["Amla", "Hibiscus"],
    type: "External",
    score: 92,
  },
];

export function Featured() {
  return (
    <section id="remedies" className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 max-w-2xl"
        >
          <h2 className="text-4xl font-bold tracking-tight">Featured Remedies</h2>
          <p className="mt-4 text-cream-200/70">
            Hand-crafted combinations validated by our ML compatibility predictor and backed by
            herbal research.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {remedies.map((remedy, i) => (
            <motion.div
              key={remedy.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="h-full transition-colors hover:border-leaf-500/50">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Badge variant={remedy.type === "Internal" ? "success" : "default"}>
                      {remedy.type}
                    </Badge>
                    <span className="text-sm font-semibold text-leaf-400">{remedy.score}%</span>
                  </div>
                  <CardTitle className="mt-3">{remedy.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="flex flex-wrap gap-2">
                    {remedy.ingredients.map((ing) => (
                      <span key={ing} className="rounded-full bg-forest-800 px-3 py-1 text-xs text-cream-100">
                        {ing}
                      </span>
                    ))}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
