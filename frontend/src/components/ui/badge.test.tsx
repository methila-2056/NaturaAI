import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "./badge";

describe("Badge", () => {
  it("renders its children", () => {
    render(<Badge>Safe</Badge>);
    expect(screen.getByText("Safe")).toBeInTheDocument();
  });

  it("applies variant classes", () => {
    const { container } = render(<Badge variant="destructive">Unsafe</Badge>);
    expect(container.firstElementChild?.className).toContain("text-terra-500");
  });

  it("merges additional class names", () => {
    const { container } = render(<Badge className="uppercase">Caution</Badge>);
    expect(container.firstElementChild?.className).toContain("uppercase");
  });
});
