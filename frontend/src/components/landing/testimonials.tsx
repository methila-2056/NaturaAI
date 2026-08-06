"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const testimonials = [
  {
    name: "Ananya S.",
    role: "Ayurveda Student",
    quote:
      "I scanned a plant I found in my garden and NaturaAI identified it as Brahmi with a 96% confidence score. Incredible for learning.",
  },
  {
    name: "Rahul M.",
    role: "Fitness Enthusiast",
    quote:
      "The compatibility check warned me that my Ashwagandha habit could interfere with my thyroid medication. That warning mattered.",
  },
  {
    name: "Dr. Priya K.",
    role: "Pharmacologist",
    quote:
      "As a researcher, I appreciate that every recommendation carries a scientific confidence score and references. Responsible design.",
  },
];

export function Testimonials() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h2 className="text-4xl font-bold tracking-tight">Loved by Users</h2>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="flex gap-1">
                    {Array.from({ length: 5 }).map((_, s) => (
                      <Star key={s} className="h-4 w-4 fill-sun-400 text-sun-400" />
                    ))}
                  </div>
                  <CardTitle className="text-base">{t.name}</CardTitle>
                  <CardDescription>{t.role}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-cream-200/80">&ldquo;{t.quote}&rdquo;</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
