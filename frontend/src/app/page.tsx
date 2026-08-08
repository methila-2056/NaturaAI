import { Navbar } from "@/components/landing/navbar";
import { Hero } from "@/components/landing/hero";
import { Stats } from "@/components/landing/stats";
import { Featured } from "@/components/landing/featured";
import { Capabilities } from "@/components/landing/capabilities";
import { About } from "@/components/landing/about";
import { Footer } from "@/components/landing/footer";

export default function Home() {
  return (
    <main>
      <Navbar />
      <Hero />
      <Stats />
      <Featured />
      <Capabilities />
      <About />
      <Footer />
    </main>
  );
}
