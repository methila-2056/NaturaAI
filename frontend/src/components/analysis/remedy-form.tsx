"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Leaf, Loader2, Plus, RotateCcw, Search, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type AnalyzeResponse, type SuggestResult } from "@/lib/api";
import { useUserStore } from "@/store/useUserStore";

const HERBS = [
  "Neem", "Tulsi", "Hibiscus", "Aloe Vera", "Rose", "Mint", "Brahmi", "Ashwagandha",
  "Turmeric", "Ginger", "Lemon", "Moringa", "Green Tea", "Amla", "Fenugreek", "Honey",
];

const DISEASES = [
  "Diabetes", "Hypertension", "Asthma", "Thyroid", "PCOS", "Skin Allergy",
  "Eczema", "Psoriasis", "Acne", "Hair Loss", "Fever", "Cold",
  "Stress", "Anxiety", "Insomnia", "None",
];

const REMEDY_TYPES = [
  { value: "tea", label: "Herbal Tea", internal: true },
  { value: "juice", label: "Herbal Juice", internal: true },
  { value: "powder", label: "Herbal Powder", internal: true },
  { value: "capsules", label: "Herbal Capsules", internal: true },
  { value: "immunity", label: "Immunity Booster", internal: true },
  { value: "facewash", label: "Face Wash", internal: false },
  { value: "hairoil", label: "Hair Oil", internal: false },
  { value: "facepack", label: "Face Pack", internal: false },
  { value: "shampoo", label: "Shampoo", internal: false },
  { value: "soap", label: "Soap", internal: false },
  { value: "cream", label: "Cream", internal: false },
  { value: "lotion", label: "Lotion", internal: false },
  { value: "gel", label: "Gel", internal: false },
];

type Step = "health" | "type" | "ingredients" | "result";

export default function RemedyForm() {
  const profile = useUserStore((s) => s.user);
  const [step, setStep] = useState<Step>("health");
  const [diseases, setDiseases] = useState<string[]>(profile?.diseases ?? []);
  const [allergies, setAllergies] = useState<string[]>(profile?.allergies ?? []);
  const [remedyType, setRemedyType] = useState<string>("tea");
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<SuggestResult[]>([]);
  const [suggesting, setSuggesting] = useState(false);
  const [suggestNote, setSuggestionNote] = useState<string | null>(null);
  const [allHerbs, setAllHerbs] = useState<string[]>(HERBS);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [analyzedAt, setAnalyzedAt] = useState<string | null>(null);

  useEffect(() => {
    api
      .herbs()
      .then((list) => {
        const names = (list ?? [])
          .map((h) => String((h as { name?: unknown }).name ?? ""))
          .filter(Boolean);
        setAllHerbs(Array.from(new Set([...HERBS, ...names])).sort());
      })
      .catch(() => {});
  }, []);

  const searchMatches = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return [];
    return allHerbs.filter(
      (h) => h.toLowerCase().includes(q) && !ingredients.includes(h),
    );
  }, [allHerbs, search, ingredients]);

  const isInternal = useMemo(
    () => REMEDY_TYPES.find((t) => t.value === remedyType)?.internal ?? true,
    [remedyType],
  );

  function toggle(list: string[], setList: (v: string[]) => void, value: string) {
    if (value === "None") {
      setList(list.includes("None") ? [] : ["None"]);
      return;
    }
    setList(
      list.includes(value) ? list.filter((v) => v !== value) : [...list.filter((v) => v !== "None"), value],
    );
  }

  function addIngredient(name: string) {
    const clean = name.trim();
    if (!clean) return;
    setIngredients((list) => (list.includes(clean) ? list : [...list, clean]));
  }

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ingredients,
        remedyType: (isInternal ? "internal" : "external") as "internal" | "external",
        profile: {
          age: profile?.age ?? 25,
          gender: profile?.gender ?? "unknown",
          diseases,
          allergies,
          medications: profile?.medications ?? [],
        },
      };
      const res = await api.analyze(payload);
      setResult(res);
      setAnalysisId(
        `NA-${Date.now().toString(36).toUpperCase()}${Math.random()
          .toString(36)
          .slice(2, 6)
          .toUpperCase()}`,
      );
      setAnalyzedAt(new Date().toLocaleString());
      setStep("result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  function reset(target: Step = "health") {
    setStep(target);
    setResult(null);
    setIngredients([]);
    setError(null);
    setAiSuggestions([]);
    setSuggestionNote(null);
    setSearch("");
    setAnalysisId(null);
    setAnalyzedAt(null);
  }

  async function loadAiSuggestions() {
    if (ingredients.length === 0) return;
    setSuggesting(true);
    setError(null);
    setSuggestionNote(null);
    try {
      const results = await Promise.all(ingredients.map((ing) => api.suggest(ing, ingredients)));
      const seen = new Set<string>();
      const merged: SuggestResult[] = [];
      const notes: string[] = [];
      for (const res of results) {
        const note = (res as { note?: string }).note;
        if (note) notes.push(note);
        for (const s of res.suggestions) {
          if (ingredients.includes(s.ingredient) || seen.has(s.ingredient)) continue;
          seen.add(s.ingredient);
          merged.push(s);
        }
      }
      const rank = { safe: 0, caution: 1, unsafe: 2 };
      merged.sort(
        (a, b) =>
          rank[a.verdict] - rank[b.verdict] || b.confidence - a.confidence,
      );
      setAiSuggestions(merged.slice(0, 6));
      setSuggestionNote(notes.join(" ") || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI suggestions failed");
    } finally {
      setSuggesting(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-2 text-sm text-cream-200/70 transition-colors hover:text-leaf-400"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to home
      </Link>
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Remedy Analyzer</h1>
          <p className="mt-2 text-cream-200/70">
            Answer a few questions and let the AI engine predict compatibility and safety.
          </p>
        </div>
        <Button variant="ghost" onClick={() => reset("health")}>
          <RotateCcw className="mr-2 h-4 w-4" />
          Start over
        </Button>
      </div>

      <AnimatePresence mode="wait">
        {step === "health" && (
          <motion.div
            key="health"
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Health Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-8">
                <div>
                  <p className="mb-3 text-sm font-medium text-cream-100">Existing conditions</p>
                  <div className="flex flex-wrap gap-2">
                    {DISEASES.map((d) => (
                      <button
                        key={d}
                        onClick={() => toggle(diseases, setDiseases, d)}
                        className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                          diseases.includes(d)
                            ? "border-leaf-400 bg-leaf-500/15 text-leaf-400"
                            : "border-forest-600 text-cream-200/70 hover:border-leaf-400/50"
                        }`}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="mb-3 text-sm font-medium text-cream-100">Allergies</p>
                  <div className="flex flex-wrap gap-2">
                    {["Pollen", "Latex", "Nuts", "Honey", "Citrus", "None"].map((a) => (
                      <button
                        key={a}
                        onClick={() => toggle(allergies, setAllergies, a)}
                        className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                          allergies.includes(a)
                            ? "border-leaf-400 bg-leaf-500/15 text-leaf-400"
                            : "border-forest-600 text-cream-200/70 hover:border-leaf-400/50"
                        }`}
                      >
                        {a}
                      </button>
                    ))}
                  </div>
                </div>
                <Button onClick={() => setStep("type")} className="w-full">
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {step === "type" && (
          <motion.div
            key="type"
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Choose Remedy Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {REMEDY_TYPES.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => setRemedyType(t.value)}
                      className={`rounded-2xl border p-4 text-sm font-medium transition-colors ${
                        remedyType === t.value
                          ? "border-leaf-400 bg-leaf-500/15 text-leaf-400"
                          : "border-forest-600 text-cream-200/70 hover:border-leaf-400/50"
                      }`}
                    >
                      {t.label}
                      <span className="mt-1 block text-xs font-normal opacity-60">
                        {t.internal ? "Internal" : "External"}
                      </span>
                    </button>
                  ))}
                </div>
                <div className="mt-6 flex gap-3">
                  <Button variant="ghost" onClick={() => setStep("health")}>
                    Back
                  </Button>
                  <Button onClick={() => setStep("ingredients")} className="flex-1">
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {step === "ingredients" && (
          <motion.div
            key="ingredients"
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Select Ingredients</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-wrap gap-2">
                  {allHerbs.map((h) => (
                    <button
                      key={h}
                      onClick={() =>
                        setIngredients((list) =>
                          list.includes(h) ? list.filter((x) => x !== h) : [...list, h],
                        )
                      }
                      className={`flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm transition-colors ${
                        ingredients.includes(h)
                          ? "border-leaf-400 bg-leaf-500/15 text-leaf-400"
                          : "border-forest-600 text-cream-200/70 hover:border-leaf-400/50"
                      }`}
                    >
                      <Leaf className="h-3.5 w-3.5" />
                      {h}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-cream-200/50" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setShowDropdown(true);
                    }}
                    onFocus={() => setShowDropdown(true)}
                    onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        if (search.trim()) {
                          addIngredient(search);
                          setSearch("");
                          setShowDropdown(false);
                        }
                      }
                    }}
                    placeholder="Search for an ingredient to add…"
                    className="w-full rounded-xl border border-forest-600 bg-forest-950 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-leaf-400"
                  />
                  {showDropdown && search.trim() && (
                    <div className="absolute z-10 mt-1 max-h-48 w-full overflow-auto rounded-xl border border-forest-600 bg-forest-900 p-1 shadow-lg">
                      {searchMatches.map((h) => (
                        <button
                          key={h}
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => {
                            setIngredients((list) => [...list, h]);
                            setSearch("");
                            setShowDropdown(false);
                          }}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-cream-200/80 hover:bg-forest-800"
                        >
                          <Leaf className="h-3.5 w-3.5 text-leaf-400" />
                          {h}
                        </button>
                      ))}
                      {searchMatches.length === 0 && (
                        <button
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => {
                            addIngredient(search);
                            setSearch("");
                            setShowDropdown(false);
                          }}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-cream-200/80 hover:bg-forest-800"
                        >
                          <Plus className="h-3.5 w-3.5 text-leaf-400" />
                          Add &ldquo;{search}&rdquo; as a custom ingredient
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-leaf-500/20 bg-forest-900/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="flex items-center gap-2 text-sm font-medium text-cream-100">
                      <Sparkles className="h-4 w-4 text-leaf-400" />
                      AI complementary ingredients
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={loadAiSuggestions}
                      disabled={ingredients.length < 1 || suggesting}
                    >
                      {suggesting ? (
                        <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="mr-1 h-4 w-4" />
                      )}
                      {suggesting ? "Thinking…" : "Suggest with AI"}
                    </Button>
                  </div>
                  {ingredients.length === 0 ? (
                    <p className="mt-3 text-xs text-cream-200/50">
                      Select at least one ingredient above to see AI-suggested complementary
                      ingredients.
                    </p>
                  ) : aiSuggestions.length === 0 && !suggesting ? (
                    suggestNote ? (
                      <p className="mt-3 text-xs text-sun-400">{suggestNote}</p>
                    ) : (
                      <p className="mt-3 text-xs text-cream-200/50">
                        No suggestions yet. Click &quot;Suggest with AI&quot; to let the trained model
                        rank the safest complementary ingredients.
                      </p>
                    )
                  ) : (
                    <div className="mt-3 space-y-2">
                      {aiSuggestions.map((s) => (
                        <div
                          key={s.ingredient}
                          className="flex items-center justify-between gap-3 rounded-xl border border-forest-600 bg-forest-950 p-3"
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-medium">{s.ingredient}</p>
                              <Badge
                                variant={
                                  s.verdict === "safe"
                                    ? "success"
                                    : s.verdict === "caution"
                                      ? "warning"
                                      : "destructive"
                                }
                                className="uppercase"
                              >
                                {s.verdict}
                              </Badge>
                            </div>
                            {s.benefits.length > 0 && (
                              <p className="mt-1 truncate text-xs text-cream-200/60">
                                {s.benefits.join(" • ")}
                              </p>
                            )}
                            {s.note && (
                              <p className="mt-1 text-xs text-sun-400">{s.note}</p>
                            )}
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-cream-200/60">
                              {s.confidence}% conf.
                            </span>
                            <Button
                              size="sm"
                              onClick={() =>
                                setIngredients((list) => [...list, s.ingredient])
                              }
                            >
                              Add
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <p className="text-sm font-medium text-cream-100">
                      Selected ({ingredients.length})
                    </p>
                    {ingredients.length > 0 && (
                      <button
                        onClick={() => {
                          setIngredients([]);
                          setAiSuggestions([]);
                        }}
                        className="flex items-center gap-1 text-xs text-cream-200/60 transition-colors hover:text-terra-400"
                      >
                        <RotateCcw className="h-3 w-3" />
                        Clear all
                      </button>
                    )}
                  </div>
                  {ingredients.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {ingredients.map((ing) => (
                        <span
                          key={ing}
                          className="flex items-center gap-2 rounded-full border border-leaf-400/40 bg-leaf-500/10 px-3 py-1.5 text-sm text-cream-100"
                        >
                          {ing}
                          <button
                            onClick={() =>
                              setIngredients((list) => list.filter((x) => x !== ing))
                            }
                            aria-label={`Remove ${ing}`}
                            className="text-cream-200/60 transition-colors hover:text-terra-400"
                          >
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-cream-200/60">none yet</p>
                  )}
                </div>

                {error && <p className="text-sm text-terra-500">{error}</p>}

                <div className="flex gap-3">
                  <Button variant="ghost" onClick={() => setStep("type")}>
                    Back
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={runAnalysis}
                    disabled={ingredients.length < 2 || loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Predicting…
                      </>
                    ) : (
                      <>
                        <Leaf className="h-4 w-4" />
                        Analyze Combination
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {step === "result" && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>AI Prediction</CardTitle>
                    {analysisId && (
                      <p className="mt-1 text-xs text-cream-200/50">
                        Reference {analysisId}
                        {analyzedAt ? ` · ${analyzedAt}` : ""}
                      </p>
                    )}
                  </div>
                  <Badge
                    variant={
                      result.verdict === "safe"
                        ? "success"
                        : result.verdict === "caution"
                          ? "warning"
                          : "destructive"
                    }
                    className="uppercase"
                  >
                    {result.verdict}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                  {[
                    ["Compatibility", result.compatibilityScore],
                    ["Safety", result.safetyScore],
                    ["Benefit", result.benefitScore],
                    ["Risk", result.riskScore],
                    ["Scientific Confidence", result.scientificConfidence],
                  ].map(([label, score]) => (
                    <div key={label as string}>
                      <p className="text-xs text-cream-200/70">{label}</p>
                      <p className="mt-1 text-2xl font-bold text-leaf-400">{score}%</p>
                    </div>
                  ))}
                  <div>
                    <p className="text-xs text-cream-200/70">Toxicity</p>
                    <p
                      className={`mt-1 text-2xl font-bold uppercase ${
                        result.toxicityLevel === "high"
                          ? "text-terra-500"
                          : result.toxicityLevel === "medium"
                            ? "text-sun-400"
                            : "text-leaf-400"
                      }`}
                    >
                      {result.toxicityLevel}
                    </p>
                  </div>
                </div>
                <p className="mt-6 rounded-xl bg-forest-800 p-4 text-sm text-cream-100">
                  {result.rationale}
                </p>
              </CardContent>
            </Card>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-leaf-400">Benefits</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-inside space-y-2 text-sm text-cream-200/80">
                    {result.benefits.map((b) => (
                      <li key={b} className="list-disc">
                        {b}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-sun-400">Risks & Cautions</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-inside space-y-2 text-sm text-cream-200/80">
                    {result.risks.map((r) => (
                      <li key={r} className="list-disc">
                        {r}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Preparation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ol className="list-inside space-y-2 text-sm text-cream-200/80">
                  {result.preparation.map((p, i) => (
                    <li key={i} className="list-decimal">
                      {p}
                    </li>
                  ))}
                </ol>
                <div className="flex flex-wrap gap-6 border-t border-forest-700 pt-4 text-sm">
                  <p>
                    <span className="text-cream-200/70">Quantity:</span>{" "}
                    <span className="font-medium">{result.quantity}</span>
                  </p>
                  <p>
                    <span className="text-cream-200/70">Frequency:</span>{" "}
                    <span className="font-medium">{result.usageFrequency}</span>
                  </p>
                </div>
              </CardContent>
            </Card>

            <div className="rounded-2xl border border-sun-500/30 bg-sun-500/10 p-4 text-xs text-cream-100">
              Disclaimer: NaturaAI is for educational purposes only and does not replace
              professional medical advice. Consult a qualified healthcare professional before
              consuming or applying any herbal remedy.
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setResult(null);
                  reset("type");
                }}
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Analyze another combination
              </Button>
              <Button variant="ghost" onClick={() => reset("health")}>
                Start over
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
