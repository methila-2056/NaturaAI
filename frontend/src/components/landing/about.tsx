"use client";

import { motion } from "framer-motion";

export function About() {
  return (
    <section id="about" className="py-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold tracking-tight">About NaturaAI</h2>
          <p className="mt-6 text-cream-200/80">
            People use herbal medicines without understanding herb-to-herb interactions, side
            effects, contraindications, safe dosages, or scientific evidence. NaturaAI predicts
            all possible outcomes before you prepare or consume a remedy.
          </p>
          <p className="mt-4 text-cream-200/80">
            Our architecture layers a herbal knowledge base, a vector database for semantic
            search, ML classifiers trained on curated herb-combination datasets, and an LLM that
            explains every recommendation in plain language.
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 24 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 gap-4"
        >
          {[
            ["Internal", "Tea · Juice · Powder · Capsules"],
            ["External", "Face Wash · Hair Oil · Soap · Cream"],
            ["Evidence", "PubMed · NIH · WHO · OpenFDA"],
            ["Safety First", "Contraindication & allergy aware"],
          ].map(([title, sub]) => (
            <div
              key={title}
              className="rounded-2xl border border-forest-700 bg-forest-900/60 p-6"
            >
              <p className="font-semibold text-leaf-400">{title}</p>
              <p className="mt-2 text-sm text-cream-200/70">{sub}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
