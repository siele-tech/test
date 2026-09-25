import { describe, expect, it } from "vitest";

import { buildInsights } from "./insights";
import type { DashboardData } from "./types";

const data: DashboardData = {
  schemaVersion: 1,
  generatedAt: "2026-09-25T06:00:00+00:00",
  build: { commit: "abc1234", runNumber: "7", runUrl: null },
  quality: { status: "passed", files: 3, rows: 10 },
  range: { from: "2026-09-25", to: "2026-09-27", days: 3 },
  kpis: {
    date: "2026-09-27",
    revenue: 300,
    orders: 3,
    avgOrderValue: 100,
    revenueChangePct: 50,
    ordersChangePct: 0,
    avgOrderValueChangePct: 50,
  },
  totals: { revenue: 700, orders: 8, units: 12 },
  daily: [
    { date: "2026-09-25", revenue: 100, orders: 2 }, // Friday
    { date: "2026-09-26", revenue: 300, orders: 3 }, // Saturday
    { date: "2026-09-27", revenue: 300, orders: 3 }, // Sunday
  ],
  topProducts: [{ name: "Smart Watch", revenue: 350, units: 3 }],
  regions: [{ name: "North", revenue: 280, units: 4 }],
  categories: [{ name: "Electronics", revenue: 400, units: 5 }],
};

describe("buildInsights", () => {
  const insights = buildInsights(data);

  it("names the top product and its share of revenue", () => {
    expect(insights).toContain("Smart Watch is the best seller, bringing in 50% of all revenue.");
  });

  it("names the leading region", () => {
    expect(insights).toContain("The North region leads with $280 (40%).");
  });

  it("finds the best day (first one wins a tie)", () => {
    expect(insights.some((i) => i.startsWith("Best day so far: Sat 26 Sep"))).toBe(true);
  });

  it("compares weekends with weekdays", () => {
    expect(insights).toContain("Weekends average 200% more revenue than weekdays.");
  });

  it("returns nothing for an empty dataset", () => {
    const empty = { ...data, daily: [], topProducts: [], regions: [] };
    expect(buildInsights(empty)).toEqual([]);
  });
});
