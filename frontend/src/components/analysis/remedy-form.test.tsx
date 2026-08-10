import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import RemedyForm from "./remedy-form";

const { apiMock } = vi.hoisted(() => ({
  apiMock: {
    herbs: vi.fn(),
    analyze: vi.fn(),
    suggest: vi.fn(),
  },
}));

vi.mock("@/lib/api", () => ({ api: apiMock }));

vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: any) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("framer-motion", () => ({
  motion: new Proxy(
    {},
    {
      get: () => ({ children }: any) => children,
    },
  ),
  AnimatePresence: ({ children }: any) => children,
}));

const analyzeResponse = {
  compatibilityScore: 85,
  safetyScore: 90,
  benefitScore: 80,
  riskScore: 15,
  scientificConfidence: 75,
  toxicityLevel: "low",
  verdict: "safe",
  benefits: ["Supports digestion", "Reduces inflammation"],
  risks: [],
  preparation: ["Boil 250 ml of filtered water"],
  quantity: "1 cup",
  usageFrequency: "twice daily",
  rationale: "Tulsi and Ginger complement each other well.",
};

function clickButton(name: RegExp | string) {
  fireEvent.click(screen.getByRole("button", { name }));
}

function completeWizard() {
  clickButton(/continue/i);
  clickButton(/continue/i);
  clickButton("Tulsi");
  clickButton("Ginger");
}

describe("RemedyForm", () => {
  it("walks through the wizard and calls the analyze API", async () => {
    apiMock.herbs.mockResolvedValue([]);
    apiMock.analyze.mockResolvedValue(analyzeResponse);
    render(<RemedyForm />);

    completeWizard();
    clickButton(/analyze combination/i);

    await waitFor(() => expect(apiMock.analyze).toHaveBeenCalledTimes(1));
    const payload = apiMock.analyze.mock.calls[0][0];
    expect(payload.ingredients).toEqual(["Tulsi", "Ginger"]);
    expect(payload.remedyType).toBe("internal");
    expect(payload.profile).toMatchObject({ age: 25, gender: "unknown" });

    expect(await screen.findByText("Supports digestion")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText(/Tulsi and Ginger complement each other well/i)).toBeInTheDocument();
  });

  it("blocks analysis until at least two ingredients are selected", () => {
    apiMock.herbs.mockResolvedValue([]);
    render(<RemedyForm />);

    clickButton(/continue/i);
    clickButton(/continue/i);
    clickButton("Tulsi");
    expect(screen.getByRole("button", { name: /analyze combination/i })).toBeDisabled();

    clickButton("Ginger");
    expect(screen.getByRole("button", { name: /analyze combination/i })).toBeEnabled();
  });

  it("displays an error when the analysis API fails", async () => {
    apiMock.herbs.mockResolvedValue([]);
    apiMock.analyze.mockRejectedValue(new Error("Backend is unreachable"));
    render(<RemedyForm />);

    completeWizard();
    clickButton(/analyze combination/i);

    expect(await screen.findByText("Backend is unreachable")).toBeInTheDocument();
  });
});
