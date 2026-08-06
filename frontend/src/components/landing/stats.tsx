"use client";

import { motion } from "framer-motion";

const stats = [
  { value: "20,000+", label: "Plants catalogued" },
  { value: "500,000+", label: "Combination records" },
  { value: "5,000+", label: "Diseases mapped" },
  { value: "97%", label: "Prediction accuracy" },
];

export function Stats() {
  return (
    <section className="border-y border-forest-800 bg-forest-900/40">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-14 md:grid-cols-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-leaf-400 md:text-4xl">{stat.value}</p>
            <p className="mt-2 text-sm text-cream-200/70">{stat.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
