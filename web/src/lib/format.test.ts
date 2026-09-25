import { describe, expect, it } from "vitest";

import {
  formatChange,
  formatCompactCurrency,
  formatCurrency,
  formatLongDate,
  formatShortDate,
  share,
} from "./format";

describe("formatCurrency", () => {
  it("rounds to whole dollars with separators", () => {
    expect(formatCurrency(197367.4)).toBe("$197,367");
  });

  it("formats large numbers compactly", () => {
    expect(formatCompactCurrency(197367)).toBe("$197.4K");
  });
});

describe("formatChange", () => {
  it("marks growth as up", () => {
    expect(formatChange(12.345)).toEqual({ label: "+12.3% vs previous day", trend: "up" });
  });

  it("marks decline as down", () => {
    expect(formatChange(-4)).toEqual({ label: "−4.0% vs previous day", trend: "down" });
  });

  it("treats tiny changes as flat", () => {
    expect(formatChange(0.01).trend).toBe("flat");
  });

  it("handles a missing previous day", () => {
    expect(formatChange(null)).toEqual({ label: "no previous day", trend: "flat" });
  });
});

describe("dates", () => {
  it("never shifts the day because of time zones", () => {
    expect(formatShortDate("2026-09-25")).toBe("Fri 25 Sep");
    expect(formatLongDate("2026-09-25")).toBe("Friday 25 September 2026");
  });
});

describe("share", () => {
  it("returns a whole percentage", () => {
    expect(share(25, 200)).toBe("13%");
  });

  it("guards against division by zero", () => {
    expect(share(5, 0)).toBe("0%");
  });
});
