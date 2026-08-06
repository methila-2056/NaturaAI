"use client";

import { motion } from "framer-motion";
import {
  BrainCircuit,
  Image as ImageIcon,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const capabilities = [
  {
    icon: ShieldCheck,
    title: "Compatibility Predictor",
    description:
      "Machine learning over 500,000+ herb-pair records to flag safe, caution, and unsafe combinations.",
  },
  {
    icon: UserRound,
    title: "Personalized Recommendations",
    description:
      "Tailored remedies based on your age, gender, diseases, allergies, medications, and treatment type.",
  },
  {
    icon: BrainCircuit,
    title: "LLM Health Assistant",
    description:
      "Ask natural-language questions about benefits, preparation, risks, and interactions with any herb.",
  },
  {
    icon: ScanSearch,
    title: "Plant Recognition",
    description:
      "Upload a photo of a leaf, flower, or root and get plant identification with confidence scoring.",
  },
  {
    icon: ImageIcon,
    title: "Ingredient Selection",
    description:
      "Pick from the knowledge base, search by text, or upload an image to add ingredients to your remedy.",
  },
  {
    icon: Sparkles,
    title: "Formulation Assistant",
    description:
      "Generate complete herbal tea, face wash, hair oil, or soap recipes with quantities and steps.",
  },
];

export function Capabilities() {
  return (
    <section id="features" className="bg-forest-900/40 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 max-w-2xl"
        >
          <h2 className="text-4xl font-bold tracking-tight">AI Capabilities</h2>
          <p className="mt-4 text-cream-200/70">
            A layered AI architecture — knowledge base, vector search, ML prediction, and LLM
            reasoning — working together.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((cap, i) => (
            <motion.div
              key={cap.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-forest-800 text-leaf-400">
                    <cap.icon className="h-5 w-5" />
                  </div>
                  <CardTitle className="mt-4">{cap.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">{cap.description}</CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
