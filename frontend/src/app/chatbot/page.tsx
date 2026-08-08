"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, Bot, Send, User } from "lucide-react";
import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Button } from "@/components/ui/button";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Can I use Aloe Vera with Neem?",
  "Is Turmeric safe for diabetics?",
  "Can Hibiscus improve hair growth?",
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Namaste! I'm the NaturaAI herbal assistant. Ask me about herb combinations, benefits, preparation methods, or safety considerations.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(text: string) {
    const question = text.trim();
    if (!question || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_ML_URL ?? "http://localhost:8000"}/assistant`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: question }),
        },
      );
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.answer ?? "I couldn't answer that right now." },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "The assistant service isn't reachable yet. Start the ML engine to enable live answers.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-3xl flex-col px-6 py-10">
        <Link
          href="/"
          className="mb-6 inline-flex items-center gap-2 text-sm text-cream-200/70 transition-colors hover:text-leaf-400"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-forest-800 text-leaf-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Herbal Assistant</h1>
            <p className="text-sm text-cream-200/70">
              Powered by an LLM grounded in the herbal knowledge base.
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-forest-700 bg-forest-900/40 p-6">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {m.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-forest-800 text-leaf-400">
                  <Bot className="h-4 w-4" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                  m.role === "user"
                    ? "bg-leaf-500 text-forest-950"
                    : "bg-forest-800 text-cream-100"
                }`}
              >
                {m.content}
              </div>
              {m.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-leaf-500/20 text-leaf-400">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-forest-800 text-leaf-400">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-2xl bg-forest-800 px-4 py-3 text-sm text-cream-200/70">
                Thinking…
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-forest-600 px-4 py-1.5 text-xs text-cream-200/70 transition-colors hover:border-leaf-400/50 hover:text-leaf-400"
            >
              {s}
            </button>
          ))}
        </div>

        <form
          className="mt-4 flex gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about any herb or combination…"
            className="flex-1 rounded-full border border-forest-600 bg-forest-950 px-5 py-3 text-sm outline-none focus:border-leaf-400"
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            <Send className="h-4 w-4" />
            Send
          </Button>
        </form>
      </div>
      <Footer />
    </main>
  );
}
