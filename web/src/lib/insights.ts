import { formatCurrency, formatShortDate, share } from "./format";
import type { DashboardData } from "./types";

const isWeekend = (isoDate: string) => {
  const day = new Date(`${isoDate}T00:00:00Z`).getUTCDay();
  return day === 0 || day === 6;
};

const mean = (values: number[]) =>
  values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;

/** Plain-English takeaways an analyst would call out in a meeting. */
export function buildInsights(data: DashboardData): string[] {
  const insights: string[] = [];
  const total = data.totals.revenue;

  const [topProduct] = data.topProducts;
  if (topProduct) {
    insights.push(
      `${topProduct.name} is the best seller, bringing in ${share(topProduct.revenue, total)} of all revenue.`,
    );
  }

  const [topRegion] = data.regions;
  if (topRegion) {
    insights.push(
      `The ${topRegion.name} region leads with ${formatCurrency(topRegion.revenue)} (${share(topRegion.revenue, total)}).`,
    );
  }

  if (data.daily.length) {
    const best = data.daily.reduce((a, b) => (b.revenue > a.revenue ? b : a));
    insights.push(
      `Best day so far: ${formatShortDate(best.date)} at ${formatCurrency(best.revenue)}.`,
    );
  }

  const weekend = mean(data.daily.filter((d) => isWeekend(d.date)).map((d) => d.revenue));
  const weekday = mean(data.daily.filter((d) => !isWeekend(d.date)).map((d) => d.revenue));
  if (weekend && weekday) {
    const diff = ((weekend - weekday) / weekday) * 100;
    insights.push(
      `Weekends average ${Math.abs(diff).toFixed(0)}% ${diff >= 0 ? "more" : "less"} revenue than weekdays.`,
    );
  }

  return insights;
}
