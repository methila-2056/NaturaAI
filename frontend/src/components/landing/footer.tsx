import Link from "next/link";
import { Leaf } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-forest-800 bg-forest-950">
      <div className="mx-auto max-w-6xl px-6 py-14">
        <div className="grid gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center gap-2">
              <Leaf className="h-6 w-6 text-leaf-400" />
              <span className="font-semibold">
                Natura<span className="text-leaf-400">AI</span>
              </span>
            </Link>
            <p className="mt-4 max-w-sm text-sm text-cream-200/70">
              Intelligent herbal remedy prediction and recommendation system. Combining herbal
              science with AI for safer, evidence-informed natural remedies.
            </p>
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-cream-100">Product</p>
            <ul className="space-y-2 text-sm text-cream-200/70">
              <li><Link className="hover:text-leaf-400" href="/analyze">Remedy Analyzer</Link></li>
              <li><Link className="hover:text-leaf-400" href="/scan">Plant Scanner</Link></li>
              <li><Link className="hover:text-leaf-400" href="/chatbot">AI Assistant</Link></li>
              <li><Link className="hover:text-leaf-400" href="/dashboard">Dashboard</Link></li>
            </ul>
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-cream-100">Company</p>
            <ul className="space-y-2 text-sm text-cream-200/70">
              <li><Link className="hover:text-leaf-400" href="#about">About</Link></li>
              <li><Link className="hover:text-leaf-400" href="#features">Features</Link></li>
              <li><Link className="hover:text-leaf-400" href="/register">Get Started</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-forest-800 pt-6 text-center">
          <p className="text-xs text-cream-200/60">
            NaturaAI is for educational and informational purposes only and does not replace
            professional medical advice. Consult a qualified healthcare professional before
            consuming or applying any herbal remedy, especially if you have existing medical
            conditions, are pregnant, nursing, or taking prescription medications.
          </p>
          <p className="mt-3 text-xs text-cream-200/40">
            Herbal reference data includes the Amidha Ayurveda Herb Database (Amidha Ayurveda),
            used under CC BY 4.0.
          </p>
        </div>
      </div>
    </footer>
  );
}
