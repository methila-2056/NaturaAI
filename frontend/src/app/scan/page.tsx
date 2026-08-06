"use client";

import Link from "next/link";
import { useState } from "react";
import { ImagePlus, Leaf, Loader2, ScanSearch } from "lucide-react";
import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/api";

interface RecognitionResult {
  identified: string;
  confidence: number;
  medicinal_uses: string[];
  filename?: string;
}

export default function ScanPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<RecognitionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setResult(null);
    setError(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(URL.createObjectURL(selected));
  }

  async function identify() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.recognize(file);
      setResult(res as RecognitionResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not identify the plant.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-10 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-forest-800 text-leaf-400">
            <ScanSearch className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Plant Scanner</h1>
            <p className="mt-1 text-cream-200/70">
              Upload a photo of a leaf, flower, fruit, stem, or root to identify the plant and
              its medicinal uses.
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Upload an image</CardTitle>
            <CardDescription>
              JPG, PNG, or WEBP. The recognition engine will return a species guess with a
              confidence score.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <label className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-forest-600 bg-forest-950/50 px-6 py-12 text-center transition-colors hover:border-leaf-400/50">
              <input type="file" accept="image/*" className="hidden" onChange={handleFile} />
              <ImagePlus className="h-8 w-8 text-leaf-400" />
              <span className="text-sm text-cream-200/80">
                {file ? file.name : "Click to choose a plant photo"}
              </span>
              <span className="text-xs text-cream-200/50">Maximum 10 MB</span>
            </label>

            {preview && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={preview}
                alt="Plant preview"
                className="mx-auto max-h-72 rounded-2xl border border-forest-700 object-contain"
              />
            )}

            {error && <p className="text-sm text-terra-500">{error}</p>}

            <Button className="w-full" onClick={identify} disabled={!file || loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Identifying…
                </>
              ) : (
                <>
                  <ScanSearch className="h-4 w-4" />
                  Identify Plant
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {result && (
          <Card className="mt-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Identification Result</CardTitle>
                <Badge variant={result.confidence >= 0.7 ? "success" : "warning"}>
                  {Math.round(result.confidence * 100)}% confidence
                </Badge>
              </div>
              {result.filename && <CardDescription>{result.filename}</CardDescription>}
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-forest-800 text-leaf-400">
                  <Leaf className="h-5 w-5" />
                </div>
                <p className="text-2xl font-bold">{result.identified}</p>
              </div>
              {result.medicinal_uses.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-medium text-cream-100">Medicinal uses</p>
                  <ul className="list-inside space-y-1 text-sm text-cream-200/80">
                    {result.medicinal_uses.map((use) => (
                      <li key={use} className="list-disc">
                        {use}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="rounded-2xl border border-sun-500/30 bg-sun-500/10 p-4 text-xs text-cream-100">
                Identification is approximate. Verify the plant with a botanical reference or
                expert before any use.
              </div>
              <Button variant="outline" asChild>
                <Link href="/analyze">Use this plant in a remedy</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
      <Footer />
    </main>
  );
}
