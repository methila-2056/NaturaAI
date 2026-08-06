import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import RemedyForm from "@/components/analysis/remedy-form";

export default function AnalyzePage() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <RemedyForm />
      <Footer />
    </main>
  );
}
